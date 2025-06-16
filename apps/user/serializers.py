from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "date_joined",
            "is_staff",
            "is_superuser",
        )
        read_only_fields = ("id", "date_joined")
