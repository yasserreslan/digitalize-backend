import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError
from digitalize.models import Device
from digitalize.settings import PEM_PRIVATE_KEY, PEM_PUBLIC_KEY
from django.contrib.auth.hashers import make_password
import hashlib
from user_agents import parse

def parse_token(token):
    try:
        public_key = PEM_PUBLIC_KEY
        payload = jwt.decode(token, public_key, algorithms=['RS256'])
        return payload
    except (DecodeError, ExpiredSignatureError, Exception):
        return None

def create_token(payload, expiration=None):

    private_key = PEM_PRIVATE_KEY
    algorithm = 'RS256'
    if expiration:
        payload['exp'] = expiration 
    token = jwt.encode(payload, private_key, algorithm=algorithm)
    return token



from datetime import datetime, timedelta
from django.db.models import Count
from .models import SystemSettings, User

def check_registration_restriction():

    registration_setting = SystemSettings.objects.get(setting_name='user_registration')
    if registration_setting.setting_value != 'active':
        return False
    
    today = datetime.now().date()
    
    # Retrieve the daily registration limit from system settings
    limit_setting = SystemSettings.objects.get(setting_name='daily_registration_limit')
    daily_limit = int(limit_setting.setting_value)  

    # Count number of normal users registered today
    today_registrations = User.objects.filter(
        created_at__date=today,
        user_type='normal'
    ).count()
    
    # Check if the limit has been reached
    if today_registrations >= daily_limit:
        return False
    else:
        return True

# Function to create a user using the User model
def create_user(username, email, password, user_type,device_id,device_type,token = None):
    try:

        # check user type
        if user_type not in ("admin","normal"):
            err = Exception("Cannot create user")
            raise err

        # If user_type is admin, check authorization header otherwise not needed
        if user_type == "admin":
            # parse the jwt token and get the role from the body

            payload = parse_token(token)
            if not payload:
                raise Exception(f'Error creating user: Unauthorized')
            
            if payload.get("role") != "admin":
                raise Exception(f'Error creating user: Unauthorized')
        else:
            # Check user cap setting
            within_limit = check_registration_restriction()
            if not within_limit:
                raise Exception(f'Limit reached')
            
        # Hash password
        hashed_password = make_password(password)

        # Create new user
        new_user = User.objects.create(
            username=username, 
            email=email, 
            password=hashed_password,
            user_type = user_type
        )
        
        new_user.save()

        # create device for user

        device = Device(device_id=device_id, user=new_user,device_type=device_type,status="active")
        device.save()

        token_payload = {
            "user_id":new_user.user_id,
            "role":user_type,
            "device_id":device_id,
            "exp": int((datetime.utcnow() + timedelta(days=30)).timestamp())
        }

        response_token = create_token(token_payload)

        return response_token
    except Exception as err:
        raise Exception(f'Error creating user: {err}')



# Custom exception for inactive devices
class InactiveDeviceException(Exception):
    def __init__(self, message="You device is not active"):
        self.message = message
        super().__init__(self.message)

class UnauthorizedException(Exception):
    def __init__(self, message="You are not authorized"):
        self.message = message
        super().__init__(self.message)

class InvalidTokenException(Exception):
    def __init__(self, message="Invalid Token"):
        self.message = message
        super().__init__(self.message)

class DeviceDoesNotExistException(Exception):
    def __init__(self, message="Device does not exist"):
        self.message = message
        super().__init__(self.message)

# checks for user token and returns user_id

def check_user_token(token):
    
    payload = parse_token(token)
    print(payload)
    if not payload:
        raise InvalidTokenException()
    
    device_id = payload["device_id"]
    user_id = payload["user_id"]
    role = payload["role"]


    # We need to check if the device that has issued this token is active 

    if not device_id or role != "normal":
        raise UnauthorizedException()

    try:
        device = Device.objects.get(device_id=device_id, user__user_id=user_id)
    
    except Device.DoesNotExist:
        raise DeviceDoesNotExistException()
    
    if device.status != "active":
        raise InactiveDeviceException()
    
    return user_id



def check_admin_token(token):
    payload = parse_token(token)
    if not payload:
        raise InvalidTokenException()
    
    role = payload["role"]

    if role != "admin":
        raise UnauthorizedException()
    
    return payload["user_id"]




from .models import AdminActionLog, User

def log_admin_action(admin_user_id, action_type, action_description):
    try:
        admin_user = User.objects.get(user_id=admin_user_id)
        new_log = AdminActionLog(
            admin_user=admin_user,
            action_type=action_type,
            action_description=action_description
        )
        new_log.save()
        return "Action logged successfully."
    except User.DoesNotExist:
        return "Admin user not found."
    except Exception as e:
        return f"Error logging action: {str(e)}"
    

# Get Device type from User-Agent header

def get_device_type(user_agent_string):

    user_agent = parse(user_agent_string)

    return user_agent.device.family



# One way hashing function to hash the User-Agent Header in order to store it in the database as device_id

def hash_string(input_string):

    sha256 = hashlib.sha256()

    sha256.update(input_string.encode('utf-8'))

    hashed_string = sha256.hexdigest()

    return hashed_string