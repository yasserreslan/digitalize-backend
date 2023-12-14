"""
URL configuration for digitalize project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import change_device_status, change_registration_limit, get_all_users, get_system_settings, get_user_devices, login, register_user, toggle_user_registration

urlpatterns = [
    path("admin/", admin.site.urls),
    path('register/', register_user, name='register_user'),
    path('login/', login, name='login'),
    path('devices/', get_user_devices, name='devices'),
    path('devices/status/', change_device_status, name='deactivate_device'),
    path('settings/registration_limit/', change_registration_limit, name='change_registration_limit'),
    path('settings/toggle_registration/', toggle_user_registration, name='toggle_user_registration'),
    path('settings/', get_system_settings, name='get_system_settings'),
    path('users/', get_all_users, name='get_normal_users_with_devices'),

]
