# events/base.py
from .models import EventRecord, EventAction
from .tasks import process_event_actions

class BaseEvent:
    def __init__(self, payload: dict):
        self.payload = payload

    def to_actions(self):
        actions = []
        for attr in dir(self):
            if attr.startswith('action_'):
                actions.append({
                    'type': attr[7:],
                    'value': getattr(self, attr)
                })
        return actions

    @classmethod
    def trigger(cls, payload: dict, immediate_actions=[]):
        instance = cls(payload)
        event_record = EventRecord.objects.create(
            name=cls.__name__,
            payload=payload
        )
        for action in instance.to_actions():
            if action['type'] in immediate_actions:
                try:
                    action_attr = getattr(instance, "action_"+action['type'])
                    action_attr()
                except Exception as e:
                    print(e)
            else:
                EventAction.objects.create(
                    event=event_record,
                    action_type=action['type']
                )
        process_event_actions()
        return event_record

    def execute(self, actions=[]):
        for action in actions:
            if hasattr(self, "action_"+action['type']):
                action_attr = getattr(self, "action_"+action['type'])
                action_attr()

    def __repr__(self):
        return f"{self.__class__.__name__}(payload={self.payload})"