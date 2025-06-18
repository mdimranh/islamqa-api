from django.urls import include, path

urlpatterns = [
    path("/auth", include("apps.authentication.urls")),
    path("/users", include("apps.user.urls")),
]
