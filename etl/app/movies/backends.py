import http
import json
from enum import StrEnum, auto

import requests
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden

User = get_user_model()


class Roles(StrEnum):
    ADMIN = auto()
    SUBSCRIBER = auto()
    SUPERUSER = auto()


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        AUTH_HOST = "127.0.0.1:8000"
        AUTH_API_LOGIN_URL = f"http://{AUTH_HOST}/auth/login"
        url = AUTH_API_LOGIN_URL
        payload = {'email': username, 'password': password}
        response = requests.post(url, data=json.dumps(payload))
        if response.status_code != http.HTTPStatus.OK:
            return None
        data = response.json()
        try:
            user, created = User.objects.get_or_create(id=data['id'], )
            user.username = data.get('email')
            user.is_staff = user.is_superuser = data['role'] in ['admin', 'superuser']
            user.save()
        except Exception:
            return None
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
