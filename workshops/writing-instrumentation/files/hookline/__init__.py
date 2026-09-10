"""hookline: deliver webhooks to subscribers and dispatch the events
that come back.

A small library that nobody has written wrapture instrumentation
for. Nothing in it knows wrapture exists.
"""

from .client import Client, DeliveryError
from .dispatch import Dispatcher

__all__ = ["Client", "DeliveryError", "Dispatcher"]
