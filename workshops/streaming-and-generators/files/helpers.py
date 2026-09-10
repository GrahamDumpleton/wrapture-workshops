"""Test helpers for the catalogue."""


def fail_at(position, exc):
    """An item check that raises exc at the item in the given position,
    counting items through the proxy it is given to, so build a fresh
    one per iteration."""
    seen = 0

    def check(page):
        nonlocal seen
        seen += 1

        if seen == position:
            raise exc

    return check
