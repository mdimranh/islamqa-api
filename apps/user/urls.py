from django.urls import path

from .views import UserCRUDView
from .signals import *

urlpatterns = [
    path("", UserCRUDView.as_view(), name="users"),
]
