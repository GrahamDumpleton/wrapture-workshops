"""A vendored HTTP client: the library you cannot edit.

Its shape is the usual one. A request() method assembles headers,
reads a timeout from a class attribute, and hands the call to a
transport. There is no hook for adding a header, no retry, and no way
to override the timeout short of editing the file.
"""


class Client:
    timeout: int = 30

    def __init__(self, base_url: str, transport) -> None:
        self.base_url = base_url
        self.transport = transport

    def request(self, method: str, path: str, headers=None, token=None) -> dict:
        headers = dict(headers or {})
        if token is not None:
            headers["Authorization"] = f"Bearer {token}"

        return self.transport(method, self.base_url + path, headers, self.timeout)
