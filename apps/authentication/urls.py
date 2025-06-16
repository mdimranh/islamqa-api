from django.urls import path

from .views import AuthenticationView

urlpatterns = [
    path("login", AuthenticationView.as_view(), name="login"),
]
