"""The inbound half: subscribers register a handler per kind of event,
and dispatch() runs the one that matches.

A handler that raises does not take the dispatcher down: the
exception goes to on_error(), which records it, and dispatch()
returns None.
"""


class Dispatcher:
    def __init__(self):
        self.handlers = {}
        self.failures = []

    def register(self, kind, handler):
        self.handlers[kind] = handler
        return handler

    def dispatch(self, kind, event):
        handler = self.handlers[kind]
        try:
            return handler(event)
        except Exception as exc:
            self.on_error(kind, event, exc)
            return None

    def on_error(self, kind, event, exc):
        self.failures.append((kind, exc))
