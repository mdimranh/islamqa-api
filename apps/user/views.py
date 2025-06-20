from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from core.restapi.views.crud import CrudAPIView

from .models import User
from .serializers import *

from .events import userCreateEvent
from apps.events.manager import eventManager
eventManager.register("user_create", userCreateEvent)

class UserCRUDView(CrudAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailsSerializer
    serializer_class_for_post = UserCreateSerializer
    
