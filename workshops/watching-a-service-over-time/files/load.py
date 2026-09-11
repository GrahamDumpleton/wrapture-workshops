"""Play the part of a day's traffic: requests at the shop for a number of seconds.

Usage: python load.py [seconds]

A quote, an order, a declined order and a quote for an item that is not
in the catalog, round and round, a few dozen requests a second.
"""

import json
import os
import sys
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

BASE = "http://127.0.0.1:" + os.environ.get("SERVER_PORT", "5075")

ORDER = {"amount": 500, "card": "4111-1111-1111-1111", "tenant": "acme"}
DECLINED = {"amount": 250, "card": "4000-0000-0000-0000", "tenant": "globex"}


def send(method, path, payload=None):
    body = json.dumps(payload).encode() if payload is not None else None
    request = Request(BASE + path, data=body, method=method)
    if body is not None:
        request.add_header("Content-Type", "application/json")
    try:
        with urlopen(request) as reply:
            reply.read()
            return reply.status
    except HTTPError as error:
        return error.code


def main(seconds=10):
    deadline = time.monotonic() + seconds
    counts = {}
    while time.monotonic() < deadline:
        for method, path, payload in (
            ("GET", "/quote/widget", None),
            ("POST", "/order", ORDER),
            ("POST", "/order", DECLINED),
            ("GET", "/quote/missing", None),
        ):
            status = send(method, path, payload)
            counts[status] = counts.get(status, 0) + 1
        time.sleep(0.02)
    total = sum(counts.values())
    summary = ", ".join(f"{count} answered {status}" for status, count in sorted(counts.items()))
    print(f"{total} requests in {seconds}s: {summary}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 10)
