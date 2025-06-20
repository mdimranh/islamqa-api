# events/tasks.py
from background_task import background
from .models import EventRecord
from .manager import eventManager

@background(schedule=5)
def process_event_actions():
    events = EventRecord.objects.filter(processed=False).all()
    for event in events:
        event_class = eventManager.get_event(event.name)(event.payload)
        event_class.execute(event.actions.all())
        event.processed = True
        event.save()
