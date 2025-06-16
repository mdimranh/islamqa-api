import base64
from datetime import timedelta

from Crypto.Random import get_random_bytes
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import authentication, exceptions
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response

from apps.authentication.models import Session
from apps.user.models import User
from core.restapi.exceptions import InvalidToken
from core.utils.aes import AESCipher


class AccessTokenAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class to authenticate the user using access token and refresh token.

    """

    www_authenticate_realm = "api"
    media_type = "application/json"

    def generate_random_token(self, length=128):
        random_bytes = get_random_bytes(length)
        random_token = base64.urlsafe_b64encode(random_bytes).rstrip(b"=")
        return random_token.decode("utf-8")

    def authenticate(self, request):
        fid = request.META.get("HTTP_FID")
        refresh_token = request.COOKIES.get("refreshToken")
        access_token = request.COOKIES.get("accessToken")

        if access_token is None and refresh_token is None:
            # raise NotAuthenticated()
            return None, None

        if access_token:
            try:
                AESCipher().decrypt(access_token)
            except:
                return self.invalid_session_response(request)

            session = Session.objects.filter(accessToken=access_token, fid=fid).first()

            if not session:
                return self.invalid_session_response(request)

            if session.expiresAt >= timezone.now():
                return session.user, session

            if (
                session.refreshTokenExpiresAt >= timezone.now()
                and refresh_token == session.refreashToken
            ):
                session.accessToken = self.generate_random_token()
                session.expiresAt = timezone.now() + timedelta(minutes=5)
                session.save()
                return session.user, session

            session.logoutTime = timezone.now()
            session.save()
            return self.invalid_session_response(request)

        try:
            AESCipher().decrypt(refresh_token)
        except:
            return self.invalid_session_response(request)

        session = Session.objects.filter(refreashToken=refresh_token, fid=fid).first()

        if not session:
            return self.invalid_session_response(request)

        new_access_token = AESCipher().encrypt(
            {
                "type": "access",
                "user": session.user.json,
                "fid": fid,
                "exp": session.user.access_token_expiry(),
            }
        )

        session.accessToken = new_access_token
        session.expiresAt = timezone.now() + timedelta(minutes=5)
        session.save()

        request.COOKIES["nat"] = new_access_token
        request.COOKIES["nex"] = session.expiresAt

        return session.user, session

    def invalid_session_response(self, request):
        Session.objects.filter(fid=request.META.get("HTTP_FID")).update(
            logoutTime=timezone.now()
        )

        response = Response()
        response.delete_cookie("accessToken")
        response.delete_cookie("refreshToken")

        raise InvalidToken("You have not enough permission to access this resource.")

        return None, None


class TokenCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if "nat" in request.COOKIES:
            response.set_cookie(
                key="accessToken",
                value=request.COOKIES["nat"],
                httponly=True,
                secure=True,
                samesite="Lax",
                expires=request.COOKIES["nex"],
            )
        return response
