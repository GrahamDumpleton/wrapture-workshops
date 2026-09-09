"""The shop's configuration, as a module other modules import.

SETTINGS is a dict other modules hold by reference, TIMEOUT a module
constant, and FORMATTERS a registry of callables looked up by name.
"""

SETTINGS = {"currency": "USD", "tax_rate": 0.2}

TIMEOUT = 30.0


def plain(total):
    return f"total={total:.2f}"


FORMATTERS = {"plain": plain}
