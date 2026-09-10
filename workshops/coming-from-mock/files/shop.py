"""An order service: take a payment, record it, send a notification.

The gateway declines cards ending in four zeros and logs a warning
when it does, each charge carries the currency named by the
SHOP_CURRENCY environment variable, and the notifier delivers through
a transport it is handed, if any. place_with_retry() retries an order
while the gateway times out.
"""

import logging
import os

log = logging.getLogger("shop")


class CardDeclined(Exception):
    pass


class Gateway:
    def charge(self, amount, card):
        if card.endswith("0000"):
            log.warning("card ending %s declined", card[-4:])
            raise CardDeclined(f"card ending {card[-4:]} declined")
        currency = os.environ.get("SHOP_CURRENCY", "AUD")
        return {"id": f"ch_{amount}", "amount": amount, "currency": currency}

    def refund(self, charge_id):
        return {"id": f"re_{charge_id}"}


class Ledger:
    def record(self, entry):
        return f"led_{entry['id']}"


class Notifier:
    def __init__(self, transport=None):
        self.transport = transport

    def send(self, message):
        if self.transport is None:
            return True
        return self.transport.deliver(message, priority="normal")


class OrderService:
    def __init__(self, gateway=None, ledger=None, notifier=None):
        self.gateway = Gateway() if gateway is None else gateway
        self.ledger = Ledger() if ledger is None else ledger
        self.notifier = Notifier() if notifier is None else notifier

    def place(self, amount, card, tenant):
        charge = self.gateway.charge(amount, card)
        try:
            self.ledger.record(charge)
        except Exception:
            self.gateway.refund(charge["id"])
            raise
        self.notifier.send(f"order {charge['id']} placed for {tenant}")
        return charge


def place_with_retry(service, amount, card, tenant, attempts=3):
    for attempt in range(attempts):
        try:
            return service.place(amount, card, tenant)
        except TimeoutError:
            if attempt == attempts - 1:
                raise
