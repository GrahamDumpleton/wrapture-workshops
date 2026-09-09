"""Place three orders, one of which the gateway declines."""

from shop import CardDeclined, OrderService

ORDERS = [
    (500, "4111-1111-1111-1111", "acme"),
    (250, "4000-0000-0000-0000", "globex"),
    (120, "5555-4444-3333-2222", "globex"),
]


def run():
    service = OrderService()
    for amount, card, tenant in ORDERS:
        try:
            service.place(amount, card, tenant=tenant)
        except CardDeclined:
            pass
