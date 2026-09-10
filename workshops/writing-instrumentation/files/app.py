"""An application using hookline: two deliveries, one to a subscriber
that is down, and two dispatched events, one to a handler that
raises.

Nothing here imports wrapture.
"""

from hookline import Client, DeliveryError, Dispatcher

client = Client()
dispatcher = Dispatcher()


def order_placed(event):
    return f"emailed {event['customer']}"


def order_failed(event):
    raise ValueError(f"no handler for {event['reason']}")


dispatcher.register("order.placed", order_placed)
dispatcher.register("order.failed", order_failed)

for url in ("https://acme.example/hooks", "https://globex.example/down"):
    try:
        client.deliver(url, {"order": 42}, headers={"X-Signature": "s3cret"})
    except DeliveryError as exc:
        print("delivery failed:", exc)

print(dispatcher.dispatch("order.placed", {"customer": "ann@example.com"}))
print(dispatcher.dispatch("order.failed", {"reason": "card declined"}))
print("failures:", dispatcher.failures)
