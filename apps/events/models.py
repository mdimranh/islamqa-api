from django.db import models

class EventRecord(models.Model):
    name = models.CharField(max_length=100)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)


class EventAction(models.Model):
    event = models.ForeignKey(EventRecord, on_delete=models.CASCADE, related_name='actions')
    action_type = models.CharField(max_length=50)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
