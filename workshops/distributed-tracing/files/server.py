"""Serve the quote service on the port QUOTE_PORT names (5076 by default).

Each request the client sends prints as one tree here, carrying the
same trace id the client minted; server.jsonl records the events with
the id on every line. Stop with Ctrl-C.
"""

import os
from wsgiref.simple_server import WSGIRequestHandler, make_server

from backend import app


class QuietHandler(WSGIRequestHandler):
    """Suppress the default per-request access log line, so the
    printed call trees are the output."""

    def log_message(self, format, *args):
        pass


def main():
    port = int(os.environ.get("QUOTE_PORT", "5076"))

    with make_server("127.0.0.1", port, app, handler_class=QuietHandler) as server:
        print(f"quote service on http://127.0.0.1:{port}, Ctrl-C to stop")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
