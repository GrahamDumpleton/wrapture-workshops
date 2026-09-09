"""An order service: take a payment, record it, send a notification.

If the ledger write fails, the payment is refunded and the error
propagates. The collaborators can be injected through the constructor,
and the payment step goes through a private method on the service.
"""


class Gateway:
    def charge(self, amount, currency="USD"):
        return {"id": f"ch_{amount}", "amount": amount}

    def refund(self, charge_id):
        return {"id": f"re_{charge_id}"}


class Ledger:
    def record(self, entry):
        return f"led_{entry['id']}"


class Notifier:
    def send(self, message):
        return True


class OrderService:
    def __init__(self, gateway=None, ledger=None, notifier=None):
        self.gateway = Gateway() if gateway is None else gateway
        self.ledger = Ledger() if ledger is None else ledger
        self.notifier = Notifier() if notifier is None else notifier

    def place(self, amount):
        charge = self._take_payment(amount)
        try:
            self.ledger.record(charge)
        except Exception:
            self.gateway.refund(charge["id"])
            raise
        self.notifier.send(f"order {charge['id']} placed")
        return charge

    def _take_payment(self, amount):
        return self.gateway.charge(amount)
