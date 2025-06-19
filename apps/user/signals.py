# signal
from django.db.models.signals import post_save
from django.dispatch import receiver

# local model
from .models import User

# event
from .events import userCreateEvent


@receiver(post_save, sender=User)
def user_create_signal(sender, instance, created, update_fields, **kwargs):
    if created:
        event = userCreateEvent("created", instance)
        event.trigger()
