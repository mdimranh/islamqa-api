from rest_framework import serializers
from rest_framework.response import Response

from apps.authentication.models import Session
from apps.user.models import User
from core.utils.aes import aes


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """

    email = serializers.EmailField(required=True, write_only=True)
    password = serializers.CharField(write_only=True, required=True)
    fid = serializers.CharField(required=False, write_only=True)
    remember_me = serializers.BooleanField(default=False, write_only=True)
