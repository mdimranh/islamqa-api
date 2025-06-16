from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.models import Session

from .serializers import LoginSerializer


class AuthenticationView(APIView):
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
            user = serializer.get_user()
            if user and user.check_password(serializer.validated_data["password"]):
                return serializer.login()
            return Response({"message": "Invalid email or password."}, status=400)
        return Response(serializer.errors, status=400)
