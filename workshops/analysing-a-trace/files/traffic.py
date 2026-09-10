"""Place three hundred orders for two tenants, some of them declined."""

import random

from shop import CardDeclined, OrderService

CARDS = ["4111-1111-1111-1111", "5555-4444-3333-2222", "4000-0000-0000-0000"]
AMOUNTS = {"acme": (200, 2000), "globex": (20, 200)}


def orders(count=300, seed=1):
    chooser = random.Random(seed)
    for number in range(count):
        tenant = "acme" if number % 3 == 0 else "globex"
        low, high = AMOUNTS[tenant]
        amount = chooser.randint(low, high)
        card = chooser.choices(CARDS, weights=[5, 4, 1])[0]
        yield amount, card, tenant


def run():
    service = OrderService()
    placed = declined = 0
    for amount, card, tenant in orders():
        try:
            service.place(amount, card, tenant=tenant)
            placed += 1
        except CardDeclined:
            declined += 1
    return placed, declined


if __name__ == "__main__":
    placed, declined = run()
    print(f"{placed} orders placed, {declined} declined")
