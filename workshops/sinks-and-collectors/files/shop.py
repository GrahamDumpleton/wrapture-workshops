"""An order service: take a payment, record it, send a notification.

A card number travels with each order, the gateway declines cards
ending in four zeros, and each order belongs to a tenant. The gateway
authorises the card before charging it, through a method of its own,
and the notifier delivers on one of two channels, email or sms.
"""


class CardDeclined(Exception):
    pass


class Gateway:
    def authorise(self, card):
        if card.endswith("0000"):
            raise CardDeclined(f"card ending {card[-4:]} declined")
        return f"auth_{card[-4:]}"

    def charge(self, amount, card):
        self.authorise(card)
        return {"id": f"ch_{amount}", "amount": amount}


class Ledger:
    def record(self, entry):
        return f"led_{entry['id']}"


class Notifier:
    def send(self, channel, message):
        return f"{channel}:{message}"


class OrderService:
    def __init__(self):
        self.gateway = Gateway()
        self.ledger = Ledger()
        self.notifier = Notifier()

    def place(self, amount, card, tenant, channel="email"):
        charge = self.gateway.charge(amount, card)
        self.ledger.record(charge)
        self.notifier.send(channel, f"order {charge['id']} placed")
        return charge
