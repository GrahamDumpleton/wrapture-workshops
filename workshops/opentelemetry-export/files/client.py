"""Place three orders against the running quote service.

Each order is one tree here and one tree on the server, joined by the
trace id minted at this side's root; client.jsonl and server.jsonl
carry the same ids.
"""

from frontend import place_order


def main():
    for item in ("widget", "gadget", "missing"):
        print(place_order(item))


if __name__ == "__main__":
    main()
