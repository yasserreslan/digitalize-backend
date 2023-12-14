from django.apps import AppConfig
from django.contrib.auth.hashers import make_password

from digitalize.settings import DEFAULT_PASSWORD, DEFAULT_USERNAME

class DigitalizeConfig(AppConfig):
    name = 'digitalize'

    def ready(self):
        
        from .models import User
        username = DEFAULT_USERNAME
        password = DEFAULT_PASSWORD
        if not User.objects.filter(username=username).exists():
            User.objects.create(username=username, password=make_password(password),user_type="admin")
