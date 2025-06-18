from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from core.restapi.views.crud import CrudAPIView

from .models import User
from .serializers import UserSerializer


class UserCRUDView(CrudAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
