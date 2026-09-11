"""Send thirty requests to the shop, on the port SERVER_PORT names (5072 by default).

Ten orders for acme, ten orders for globex on a card the gateway
declines, and ten quotes, each order carrying its tenant in an
X-Tenant header. Standard library only, so it runs on any Python.
"""

import json
import os
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:" + os.environ.get("SERVER_PORT", "5072")


def send(method, path, body=None, tenant=None):
    headers = {"Content-Type": "application/json"}
    if tenant is not None:
        headers["X-Tenant"] = tenant
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request) as response:
            return response.status
    except urllib.error.HTTPError as error:
        return error.code


for _ in range(10):
    send("POST", "/order", {"amount": 500, "card": "4111-1111-1111-1111", "tenant": "acme"}, tenant="acme")
    send("POST", "/order", {"amount": 250, "card": "4000-0000-0000-0000", "tenant": "globex"}, tenant="globex")
    send("GET", "/quote/widget")

print("30 requests sent")
