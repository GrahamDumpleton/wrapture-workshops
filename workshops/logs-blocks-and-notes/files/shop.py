"""An order service: take a payment, record it, send a notification.

This copy of the shop talks about itself. The gateway logs a warning
before declining a card, the service declares its fulfilment phase as
a block and annotates it with the ledger entry, and a declined card
is handled rather than raised, with the exception noted against the
order. All of that is inert when nothing is listening.
"""

import logging

import wrapture

log = logging.getLogger("shop")


class CardDeclined(Exception):
    pass


class Gateway:
    def charge(self, amount, card):
        if card.endswith("0000"):
            log.warning("card ending %s declined", card[-4:])
            raise CardDeclined(f"card ending {card[-4:]} declined")
        return {"id": f"ch_{amount}", "amount": amount}


class Ledger:
    def record(self, entry):
        return f"led_{entry['id']}"


class Notifier:
    def send(self, message):
        return True


class OrderService:
    def __init__(self):
        self.gateway = Gateway()
        self.ledger = Ledger()
        self.notifier = Notifier()

    def place(self, amount, card, tenant):
        try:
            charge = self.gateway.charge(amount, card)
        except CardDeclined as exc:
            wrapture.note_exception(exc)
            return {"status": "declined", "tenant": tenant}

        with wrapture.block("fulfil", data={"tenant": tenant}):
            entry = self.ledger.record(charge)
            wrapture.annotate(entry=entry)
            self.notifier.send(f"order {charge['id']} placed")

        return {"status": "placed", "id": charge["id"], "tenant": tenant}
