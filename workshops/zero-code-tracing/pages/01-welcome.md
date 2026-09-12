---
title: Welcome
requires: [verify:env-ready]
---

# Tracing without touching the program

The previous workshop traced the shop with three bindings and a sink,
all applied from the program's own entry point. That is fine when the
program is yours. It is less fine when the application is one you
inherited and would rather not touch, when someone else owns the
deployment, or when you simply do not want observation code living
inside the thing being observed. For all of those the entry point edit
is one edit too many.

The same setup can live in a file next to the program instead, with
nothing in the program saying so. That is what this workshop does.

The shop is {open}`shop.py`: an order service that takes a payment
through a gateway, records it in a ledger and sends a notification,
with a card number on each order and a tenant it belongs to.
{open}`orders.py` places three orders, one of which the gateway
declines. The entry point, {open}`main.py`, is two lines, and neither
of them mentions wrapture. It stays that way for the whole workshop.

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
pip install wrapture==1.0.0b1
```

Run the program once, as it stands.

```{execute}
:id: run-silent
:session: shell
:wait: prompt
python main.py
```

Three orders placed, in silence. The next page makes the same run
narrate itself without changing a line of it.

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
