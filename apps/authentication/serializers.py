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

    def get_user(self):
        """
        Returns the user instance if the credentials are valid.
        """

        email = self.validated_data.get("email")
        password = self.validated_data.get("password")
        fid = self.validated_data.get("fid", "")

        return User.objects.filter(email=email, is_active=True).first()

    def login(self):
        """
        Logs in the user and creates a session.
        """
        user = self.get_user()
        if not user or not user.check_password(self.validated_data["password"]):
            return Response({"message": "Invalid email or password."}, status=400)

        session, created = Session.objects.get_or_create(
            user=user,
            fid=self.validated_data.get("fid", ""),
            defaults={
                "accessToken": aes.encrypt(
                    {
                        "type": "access",
                        "user": user.json,
                        "fid": self.validated_data.get("fid", ""),
                        "exp": user.access_token_expiry(),
                    }
                ),
                "refreashToken": aes.encrypt(
                    {
                        "type": "refresh",
                        "user_id": user.id,
                        "fid": self.validated_data.get("fid", ""),
                        "exp": user.refresh_token_expiry(),
                    }
                ),
                "ip": self.context["request"].META.get("REMOTE_ADDR"),
                "userAgent": self.context["request"].META.get("HTTP_USER_AGENT", ""),
                "expiresAt": user.access_token_expiry(),
                "refreshTokenExpiresAt": user.refresh_token_expiry(),
            },
        )

        response = Response()
        response.set_cookie(
            key="accessToken",
            value=session.accessToken,
            httponly=True,
            secure=True,
            samesite="Lax",
            expires=session.expiresAt,
        )
        response.set_cookie(
            key="refreshToken",
            value=session.refreashToken,
            httponly=True,
            secure=True,
            samesite="Lax",
            expires=session.refreshTokenExpiresAt,
        )
        return response
