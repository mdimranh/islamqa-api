from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from .models import User
from .serializers import UserSerializer


class UserListView(ListAPIView):
    """
    View to list all users.
    """

    permission_classes = (IsAuthenticated,)

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to list users.
        """
        return super().get(request, *args, **kwargs)
