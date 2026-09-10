"""The server half: a small quote service, unaware it is observed.

Nothing here imports wrapture. The server.toml next to it wraps the
WSGI application in the recording middleware and observes the helper;
the middleware parses the traceparent header the client sends, so
this process's events join the client's trace.
"""

import json

CATALOG = {"widget": 25, "gadget": 120}


def quote(item):
    price = CATALOG[item]
    return {"item": item, "price": price}


def app(environ, start_response):
    path = environ.get("PATH_INFO", "")

    if path.startswith("/quote/"):
        try:
            payload = quote(path.removeprefix("/quote/"))
        except KeyError:
            start_response("404 Not Found", [("Content-Type", "text/plain")])
            return [b"no such item\n"]

        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(payload).encode() + b"\n"]

    start_response("404 Not Found", [("Content-Type", "text/plain")])
    return [b"not found\n"]
