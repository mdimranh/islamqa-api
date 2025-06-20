class EventManager:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        self.events = dict()

    def register(self, event_name, event_class):
        if event_name in self.events:
            raise Exception(f"Event {event_name} already registered")
        self.events[event_name] = event_class

    def get_event(self, event_name):
        return self.events[event_name]

eventManager = EventManager()