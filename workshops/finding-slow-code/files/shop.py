"""An order service: take a payment, record it, send a notification.

A card number travels with each order, the gateway declines cards
ending in four zeros, and each order belongs to a tenant. If the ledger
write fails, the payment is refunded and the error propagates. The
payment step goes through a private method on the service.

This copy of the shop is slow somewhere. The workshop finds where.
"""

import time


class CardDeclined(Exception):
    pass


class Gateway:
    def charge(self, amount, card):
        if card.endswith("0000"):
            raise CardDeclined(f"card ending {card[-4:]} declined")
        return {"id": f"ch_{amount}", "amount": amount}

    def refund(self, charge_id):
        return {"id": f"re_{charge_id}"}


class Ledger:
    def record(self, entry):
        time.sleep(0.03)
        return f"led_{entry['id']}"


class Notifier:
    def send(self, message):
        return True


class OrderService:
    def __init__(self, gateway=None, ledger=None, notifier=None):
        self.gateway = Gateway() if gateway is None else gateway
        self.ledger = Ledger() if ledger is None else ledger
        self.notifier = Notifier() if notifier is None else notifier

    def place(self, amount, card, tenant):
        charge = self._take_payment(amount, card)
        try:
            self.ledger.record(charge)
        except Exception:
            self.gateway.refund(charge["id"])
            raise
        self.notifier.send(f"order {charge['id']} placed")
        return charge

    def _take_payment(self, amount, card):
        return self.gateway.charge(amount, card)
