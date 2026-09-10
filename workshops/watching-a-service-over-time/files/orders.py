"""A day's traffic against the shop, compressed: orders in a loop.

One card in four is declined, so a share of the calls raise. Nothing
here knows it will be observed.
"""

import time

from shop import CardDeclined, OrderService

CARDS = [
    "4111-1111-1111-1111",
    "4222-2222-2222-2222",
    "4333-3333-3333-3333",
    "4000-0000-0000-0000",
]


def traffic(service, orders=100):
    for index in range(orders):
        try:
            service.place(50 + index % 7 * 10, CARDS[index % len(CARDS)], tenant="acme")
        except CardDeclined:
            pass


def run_for(service, seconds):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        traffic(service, 20)
        time.sleep(0.05)
