from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import User,Device
import json
from .utils  import DeviceDoesNotExistException, InactiveDeviceException, InvalidTokenException, UnauthorizedException, check_admin_token, check_user_token, create_token, create_user, get_device_type, hash_string, log_admin_action,parse_token


@csrf_exempt
@require_http_methods(["POST"])
def register_user(request):
    try:
        data = json.loads(request.body)

        # Extract user data from request
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        user_type = data.get('user_type')

        authorization_header = request.META.get('HTTP_AUTHORIZATION', None)
        device_id = request.headers.get('User-Agent')

        device_type = get_device_type(device_id)

        device_id = hash_string(device_id)

        # create user
        response = create_user(username, email, password, user_type,token=authorization_header,device_id = device_id,device_type=device_type)

        return JsonResponse({'token': response}) # return token
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

from django.contrib.auth import authenticate
from datetime import datetime, timedelta
from django.contrib.auth.hashers import check_password

@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    user_type = data.get('user_type')

    device_id = request.headers.get('User-Agent')
    # check if device already exists if not create new device for user
    
    device_type = get_device_type(device_id)

    device_id = hash_string(device_id)

    try:
        user = User.objects.get(username=username, user_type=user_type)
    
        try:
            device = Device.objects.get(device_id=device_id, user=user)
            if device.status != 'active':
                return JsonResponse({'error': 'Device not permitted'}, status=403)
        except Device.DoesNotExist:

            Device.objects.create(device_id=device_id, device_type=device_type, user=user, status='active')

        if check_password(password, user.password):
            # User authenticated, create token
            payload = {
                'user_id': user.user_id,
                'role': user.user_type,
                'device_id':device_id,
                'exp': datetime.utcnow() + timedelta(days=30)  # Token expiration
            }
            token = create_token(payload)
            return JsonResponse({'token': token})
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Invalid credentials'}, status=401)



@require_http_methods(["GET"])
def get_user_devices(request):
    try:
        
        token = request.headers.get('Authorization')
        if not token:
            return JsonResponse({'error': 'You are not authorized'}, status=401)
        
        user_id = check_user_token(token)

        # Query for the user's devices
        devices = Device.objects.filter(user_id=user_id).values()
    
        return JsonResponse(list(devices), safe=False)
    
    except (InactiveDeviceException,UnauthorizedException,InactiveDeviceException,DeviceDoesNotExistException) as e:
        return JsonResponse({'error': e.message}, status=401)
    except InvalidTokenException as e:
        return JsonResponse({'error': str(e)}, status=401)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)




from .models import SystemSettings
@csrf_exempt
@require_http_methods(["POST"])
def change_registration_limit(request):
    token = request.headers.get('Authorization')
    
    try:
        user_id = check_admin_token(token)

    except:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    data = json.loads(request.body)
    new_limit = data.get('limit')

    if not new_limit:
        return JsonResponse({'message': 'Enter limit'},status = 400)
    
    SystemSettings.objects.update_or_create(
        setting_name='daily_registration_limit',
        defaults={'setting_value': new_limit}
    )

    log_admin_action(user_id,"change_registration_limit",f"Changed registration limit to {new_limit}")

    return JsonResponse({'message': 'Registration limit updated'})



@csrf_exempt
@require_http_methods(["POST"])
def toggle_user_registration(request):

    token = request.headers.get('Authorization')

    try:
        user_id = check_admin_token(token)
    except:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    setting = SystemSettings.objects.get(setting_name='user_registration')
    setting.setting_value = 'paused' if setting.setting_value == 'active' else 'active'
    setting.save()

    string_value = 'Paused' if setting.setting_value == 'active' else 'Activated'
    log_admin_action(user_id,"toggle_user_registration",f"{string_value} user registration")

    return JsonResponse({'message': 'User registration status toggled'})


from django.http import JsonResponse
from .models import Device, User
from django.views.decorators.http import require_http_methods

@csrf_exempt
@require_http_methods(["POST"])
def change_device_status(request):

    data = json.loads(request.body)
    user_id = data.get('user_id')  # ID of the user
    device_id = data.get('device_id')

    try:
        device = Device.objects.get(device_id=device_id, user__user_id=user_id)
        device.status = 'inactive' if device.status == 'active' else 'active'
        device.save()
        return JsonResponse({'message': f'Device status changed to {device.status}'})
    except Device.DoesNotExist:
        return JsonResponse({'error': 'Device not found or does not belong to the user'}, status=404)





@csrf_exempt
@require_http_methods(["GET"])
def get_system_settings(request):
    token = request.headers.get('Authorization')

    try:
        admin_id = check_admin_token(token)
    except:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    settings = SystemSettings.objects.all().values()
    return JsonResponse(list(settings), safe=False)



@require_http_methods(["GET"])
def get_all_users(request):
    token = request.headers.get('Authorization')

    try:
        admin_id = check_admin_token(token)
    except:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    users_with_devices = []

    # Fetch all normal users
    normal_users = User.objects.filter(user_type='normal')
    
    for user in normal_users:
        # Fetch devices for each user
        devices = list(Device.objects.filter(user=user).values('device_id','device_type','status'))
        users_with_devices.append({
            'user_id': user.user_id,
            'username': user.username,
            'devices': devices
        })

    return JsonResponse(users_with_devices, safe=False)