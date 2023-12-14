from django.db import models
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)  
    email = models.CharField(max_length=100, unique=True)
    user_type = models.CharField(max_length=10, choices=[('normal', 'Normal'), ('admin', 'Admin')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'


class Device(models.Model):
    id = models.AutoField(primary_key=True)
    device_id = models.TextField()
    device_type = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=100)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'devices'

class AdminActionLog(models.Model):
    action_id = models.AutoField(primary_key=True)
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=100)
    action_description = models.TextField()
    action_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admin_action_log'

class SystemSettings(models.Model):
    setting_id = models.AutoField(primary_key=True)
    setting_name = models.CharField(max_length=100, unique=True)
    setting_value = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'system_settings'


    

    

