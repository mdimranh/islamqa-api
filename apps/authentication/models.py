from django.db import models

from apps.user.models import User


class Session(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="user_session",
    )
    accessToken = models.TextField()
    refreashToken = models.TextField()
    ip = models.GenericIPAddressField(protocol="IPv4")
    userAgent = models.TextField()
    fid = models.CharField(max_length=50)  # Fingerprint ID
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    expiresAt = models.DateTimeField()
    refreshTokenExpiresAt = models.DateTimeField()
    isLoggedIn = models.BooleanField(default=True)
    logoutTime = models.DateTimeField(null=True, blank=True)
    remember_me = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"ip : {self.ip} for userAgent : {self.userAgent}"
