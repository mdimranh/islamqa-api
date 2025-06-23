from core.restapi.views import ApiView
from core.restapi.response import DictResponse
from core.utils.aes import aes

from .models import User
from apps.authentication.models import Session

from .serializers import LoginSerializer


class LoginView(ApiView):
    """
    Base view for authentication-related endpoints.
    """

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests.
        """
        data = request.data
        data["fid"] = request.META.get("HTTP_FID", "")
        serializer = LoginSerializer(data=data, context={"request": request})

        if serializer.is_valid():
            user = self.get_user(data)
            if user and user.check_password(serializer.validated_data["password"]):
                return self.login(request, serializer.validated_data)
            return DictResponse(message="Invalid email or password.", status=400)
        return DictResponse(validation_error=serializer.errors, status=400)

    def get_user(self, data):
        """
        Returns the user instance if the credentials are valid.
        """

        email = data.get("email")
        password = data.get("password")
        fid = data.get("fid", "")

        return User.objects.filter(email=email, is_active=True).first()

    def login(self, request, data):
        """
        Logs in the user and creates a session.
        """
        user = self.get_user(data)
        if not user or not user.check_password(data["password"]):
            return DictResponse(message="Invalid email or password.", status=400)

        session, created = Session.objects.get_or_create(
            user=user,
            fid=data.get("fid", ""),
            defaults={
                "accessToken": aes.encrypt(
                    {
                        "type": "access",
                        "user": user.json,
                        "fid": data.get("fid", ""),
                        "exp": user.access_token_expiry(),
                    }
                ),
                "refreashToken": aes.encrypt(
                    {
                        "type": "refresh",
                        "user_id": user.id,
                        "fid": data.get("fid", ""),
                        "exp": user.refresh_token_expiry(
                            remember_me=data.get("remember_me", False)
                        ),
                    }
                ),
                "ip": request.META.get("REMOTE_ADDR"),
                "userAgent": request.META.get("HTTP_USER_AGENT", ""),
                "expiresAt": user.access_token_expiry(),
                "refreshTokenExpiresAt": user.refresh_token_expiry(
                    remember_me=data.get("remember_me", False)
                ),
            },
        )

        response = DictResponse()
        response.set_cookie(
            key="accessToken",
            value=session.accessToken,
            httponly=False,
            samesite="None",
            secure=True,
            # max_age=user.access_token_expiry(),
        )
        response.set_cookie(
            key="refreshToken",
            value=session.refreashToken,
            httponly=False,
            samesite="None",
            secure=True,
            # max_age=user.refresh_token_expiry(remember_me=data.get("remember_me", False)),
        )
        return response
