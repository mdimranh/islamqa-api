# signal
from django.db.models.signals import post_save
from django.dispatch import receiver
from .events import userCreateEvent
from .models import User


@receiver(post_save, sender=User)
def user_create_signal(sender, instance, created, update_fields, **kwargs):
    user = User.objects.get(id=instance.id)
    if created:
        event = userCreateEvent.trigger(payload=user.json, immediate_actions=["email"])
