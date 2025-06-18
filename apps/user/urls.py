from django.urls import path

from .views import UserCRUDView

urlpatterns = [
    path("", UserCRUDView.as_view(), name="users"),
]
