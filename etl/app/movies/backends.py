import http
import json
from enum import StrEnum, auto

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

User = get_user_model()


class Roles(StrEnum):
    ADMIN = auto()
    SUBSCRIBER = auto()
    SUPERUSER = auto()


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        url = settings.AUTH_LOGIN_URL
        payload = {'email': username, 'password': password}
        response = requests.post(url, data=json.dumps(payload))
        if response.status_code != http.HTTPStatus.OK:
            return None
        data = response.json()

        username = data.get('email')
        is_staff = is_superuser = data['role'] in ['admin', 'superuser']
        user, created = User.objects.get_or_create({"username": username,
                                                    "is_staff": is_staff,
                                                    "is_superuser": is_superuser},
                                                   id=data['id'], )
        if not created:
            user.username = username
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.save()
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
