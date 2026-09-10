---
title: Welcome
requires: [verify:env-ready]
---

# A program that narrates itself

In a test, a binding observes a method and a `timeline()` collects
what it saw. Nothing about the binding is specific to testing, though.
It emits events, and what happens to them is decided by whoever is
listening. Take the tape away, register something else, and the same
binding narrates a running program as it goes. This workshop is the
minimal version of that: a small shop, three bindings and one sink.

The shop is {open}`shop.py`: an order service that takes a payment
through a gateway, records it in a ledger and sends a notification. A
card number travels with each order, the gateway declines cards
ending in four zeros, and each order belongs to a tenant. A second
module, {open}`orders.py`, places three orders, one of which is
declined.

The question is a simple one. When an order is placed, what actually
happens? Which methods run, with what, and what comes back? A log line
would answer that only where someone had already thought to add one,
and this code has none.

## An environment for the program

wrapture is not installed in this JupyterLab, so make a virtual
environment in this directory and install wrapture into it. The
commands run in the workshop terminal, under the editor, which stays
activated for the rest of the workshop.

```{execute}
:id: create-venv
:session: shell
:title: Create and activate a virtual environment
:wait: prompt
python3 -m venv .venv && . .venv/bin/activate
```

```{execute}
:id: install-wrapture
:session: shell
:title: Install wrapture
:wait: prompt
pip install wrapture==1.0.0a22
```

Run the three orders once, as the program stands.

```{execute}
:id: run-silent
:session: shell
:wait: prompt
python -c "import orders; orders.run(); print('three orders placed')"
```

Three orders placed, and not a word about what happened to them. The
next page changes that without touching `shop.py` or `orders.py`.

```{verify}
:id: env-ready
:label: wrapture is installed in .venv
:substrate: shell
:trigger: after:install-wrapture
.venv/bin/python -c "import wrapture; print('wrapture', wrapture.__version__)"
```

```{hint}
:title: If the check fails
The virtual environment must be at `.venv` in this directory, with
wrapture installed into it. Run the two commands above again; creating
the environment a second time does no harm.
```
