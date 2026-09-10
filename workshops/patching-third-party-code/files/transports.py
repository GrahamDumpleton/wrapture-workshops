"""Transports for the vendored client.

echo() returns exactly what the client handed it, so every run shows
what the library would have sent. DropsFirst raises a ConnectionError
on its first call and echoes from the second, for the retry page.
"""


def echo(method: str, url: str, headers: dict, timeout: int) -> dict:
    return {"method": method, "url": url, "headers": headers, "timeout": timeout}


class DropsFirst:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, method: str, url: str, headers: dict, timeout: int) -> dict:
        self.calls += 1
        if self.calls == 1:
            raise ConnectionError("connection reset")

        return echo(method, url, headers, timeout)
