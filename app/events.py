from flask import current_app
from flask.signals import Namespace


class EventManager:

    def __init__(self):
        self.space = Namespace()
        self.events= {}

    def trigger(self, event_name, **params):
        self.events[event_name].send(
            current_app._get_current_object(),
            **params
        )

    def subscribe(self, event_name):
        if self.events.get(event_name) is None:
            self.events[event_name] = self.space.signal(event_name)
        return self.events[event_name].connect


event_manager = EventManager()
