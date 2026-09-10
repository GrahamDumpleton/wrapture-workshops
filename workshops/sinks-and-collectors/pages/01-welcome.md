---
title: Welcome
requires: [verify:env-ready]
---

# Where events go

Binding points emit events; sinks consume them. The live tracing
workshop registered one sink, a `Printer`, and narrowed what reached
it. This workshop is about the other side of the tape in full: what a
sink is, which sinks can hear what, what it costs when nobody is
listening, how sinks compose, the two that keep numbers instead of
events, and the declarations on a binding that decide what its
events are before any sink hears them.

The recording gate is "is anything listening", not "is there a
timeline". A `Tape` scoped to a test is one kind of listener, and a
sink registered for the life of the process is another. When nothing
is listening, an applied binding constructs no event at all.

{open}`shop.py` is the order service from the earlier workshops, with
two additions this workshop uses: the gateway authorises a card
through a method of its own before charging it, and the notifier
delivers on a channel, email or sms. {open}`orders.py` places three
orders, one declined, as many times over as a page asks.

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
