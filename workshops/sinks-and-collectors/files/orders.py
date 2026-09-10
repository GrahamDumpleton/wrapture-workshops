"""Place three orders, one of which the gateway declines.

run(times=n) places the same three orders n times over, for the pages
that need more than one call tree.
"""

from shop import CardDeclined, OrderService

ORDERS = [
    (500, "4111-1111-1111-1111", "acme", "email"),
    (250, "4000-0000-0000-0000", "globex", "sms"),
    (120, "5555-4444-3333-2222", "globex", "sms"),
]


def run(times=1):
    service = OrderService()
    for _ in range(times):
        for amount, card, tenant, channel in ORDERS:
            try:
                service.place(amount, card, tenant=tenant, channel=channel)
            except CardDeclined:
                pass
