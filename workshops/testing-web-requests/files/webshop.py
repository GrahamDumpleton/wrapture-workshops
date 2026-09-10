"""The shop behind Flask, built by a factory: a quote, an order, a CSV
export and a health check.

Nothing here imports wrapture. The quote view raises KeyError for an
item that is not in the catalog, which Flask turns into a 500.
"""

from flask import Flask, jsonify, request

from shop import CardDeclined, OrderService

CATALOG = {"widget": 25, "gadget": 120, "gizmo": 60}


def lookup(item):
    return CATALOG[item]


def create_app():
    app = Flask("webshop")
    service = OrderService()

    @app.get("/health")
    def health():
        return "ok\n"

    @app.get("/quote/<item>")
    def quote(item):
        return jsonify(item=item, price=lookup(item))

    @app.post("/order")
    def order():
        data = request.get_json()
        try:
            charge = service.place(data["amount"], data["card"], tenant=data["tenant"])
        except CardDeclined as exc:
            return jsonify(error=str(exc)), 402
        return jsonify(charge)

    @app.get("/export.csv")
    def export():
        def rows():
            for item in sorted(CATALOG):
                yield f"{item},{CATALOG[item]}\n"

        return app.response_class(rows(), mimetype="text/csv")

    return app
