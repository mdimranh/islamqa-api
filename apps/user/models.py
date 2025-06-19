# model
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

# utils
from datetime import timedelta
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model that uses email as the unique identifier instead of username.
    This model inherits from AbstractUser, which provides the default fields and methods
    for a user in Django, but overrides the username field to use email instead.
    """

    username = None  # Disable the username field
    email = models.EmailField(
        unique=True,
        error_messages={
            "unique": "A user with that email already exists.",
        },
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def access_token_expiry(self):

        return timezone.now() + timedelta(minutes=5)

    def refresh_token_expiry(self, remember_me=False):
        from datetime import timedelta

        return timezone.now() + timedelta(days=30 if remember_me else 1)

    @property
    def json(self):
        """
        Returns a JSON representation of the user.
        """
        from .serializers import UserSerializer

        return UserSerializer(self).data

    def __str__(self):
        return self.email

    def __repr__(self):
        return f"User(email={self.email})"
