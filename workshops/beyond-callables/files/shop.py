"""Orders with a status that moves through fixed stages, a pricing
function that reads its configuration from everywhere configuration
usually lives, and a generator that streams order history.
"""

import os

import config
from config import SETTINGS


class Order:
    status = "new"

    def __init__(self, order_id, amount):
        self.order_id = order_id
        self.amount = amount

    def __repr__(self):
        return f"Order({self.order_id})"

    def pay(self):
        self.status = "paid"

    def ship(self):
        self.status = "shipped"


def describe(order):
    if order.status == "shipped":
        return f"order {order.order_id} is on its way"
    return f"order {order.order_id} is {order.status}"


def price(amount, style="plain"):
    if "API_KEY" not in os.environ:
        raise RuntimeError("API_KEY is not configured")

    total = amount * (1 + SETTINGS["tax_rate"])
    formatter = config.FORMATTERS[style]

    return f"[{SETTINGS['currency']} within {config.TIMEOUT}s] " + formatter(total)


def history(orders):
    for order in orders:
        yield {"order_id": order.order_id, "status": order.status}


def statuses(orders):
    return [entry["status"] for entry in history(orders)]


def first_shipped(orders):
    for entry in history(orders):
        if entry["status"] == "shipped":
            return entry["order_id"]
    return None
