"""The shop behind Flask: a quote, an order and a health check.

Nothing here imports wrapture. The quote view raises KeyError for an
item that is not in the catalog, which Flask turns into a 500.
"""

from flask import Flask, jsonify, render_template, request

from shop import CardDeclined, OrderService

CATALOG = {"widget": 25, "gadget": 120}

app = Flask("webshop")
service = OrderService()


@app.get("/health")
def health():
    return "ok\n"


@app.get("/quote/<item>")
def quote(item):
    price = CATALOG[item]
    return render_template("quote.html", item=item, price=price)


@app.post("/order")
def order():
    data = request.get_json()
    try:
        charge = service.place(data["amount"], data["card"], tenant=data["tenant"])
    except CardDeclined as exc:
        return jsonify(error=str(exc)), 402
    return jsonify(charge)
