"""The outbound half: deliver a payload to a subscriber's URL.

deliver() is the one call an application makes; the connect and
write steps beneath it are the library's own business.
"""

import time


class DeliveryError(Exception):
    pass


class Client:
    def __init__(self, timeout=5):
        self.timeout = timeout

    def deliver(self, url, payload, headers=None):
        headers = dict(headers or {})
        self._connect(url)
        self._write(url, payload, headers)
        if url.endswith("/down"):
            raise DeliveryError(f"{url}: connection refused")
        return {"url": url, "status": 202, "bytes": len(str(payload))}

    def _connect(self, url):
        time.sleep(0.002)

    def _write(self, url, payload, headers):
        time.sleep(0.001)
