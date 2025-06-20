from django.contrib import admin
from .models import EventRecord, EventAction

admin.site.register(EventRecord)
admin.site.register(EventAction)