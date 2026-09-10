---
title: Welcome
requires: [verify:env-ready]
---

# Reports on a schedule

A service has been running in staging for a day. Nothing is on fire,
but nobody can say with confidence what it actually does: which
functions the traffic reaches, how often, how slow each one is, and
whether any of that changes through the day. Adding a stopwatch and a
log line to each function means an edit and a redeploy for every
question, and the answers land in a log file that was never designed
to be summed.

Recording every call for a day is the wrong tool too, because the
answer is a handful of numbers per function, not a million events.
What is wanted is a summary that resets on a schedule, so the same
table can be compared hour against hour, a way to ask for one right
now when something looks off, and, for the occasional deep dive, a
raw stream that rotates rather than grows. wrapture's windows and
collectors are exactly that shape, and a config file makes the whole
arrangement zero-code.

## The shop, twice

{open}`shop.py` is the order service from the earlier workshops, and
{open}`orders.py` drives it directly, in a loop, with one card in four
declined. {open}`webshop.py` is the same shop behind Flask, with a
quote, an order and a health check, and {open}`load.py` sends requests
at it for a number of seconds, a few dozen a second. The first page
uses the shop directly; the rest watch the Flask shop from outside.

## An environment for the server

wrapture is not installed in this JupyterLab, so make a virtual
environment in this directory and install wrapture, the
wrapture-instrumentation package that knows about Flask, and Flask
itself. The commands run in the terminal on the left, under the
editor, which stays activated for the rest of the workshop and is
where the server runs. The terminal on the right is for the traffic.

```{execute}
:id: create-venv
:session: shell
:title: Create and activate a virtual environment
:wait: prompt
python3 -m venv .venv && . .venv/bin/activate
```

```{execute}
:id: install-deps
:session: shell
:title: Install wrapture, its Flask instrumentation and Flask
:wait: prompt
pip install wrapture==1.0.0a22 wrapture-instrumentation==1.0.0a1 flask
```

```{verify}
:id: env-ready
:label: wrapture, wrapture-instrumentation and Flask are installed in .venv
:substrate: shell
:trigger: after:install-deps
.venv/bin/python -c "import wrapture, flask, importlib.metadata as m; print('wrapture', wrapture.__version__, 'with wrapture-instrumentation', m.version('wrapture-instrumentation'), 'and Flask', m.version('flask'))"
```

```{hint}
:title: If the check fails
The virtual environment must be at `.venv` in this directory, with
all three packages installed into it. Run the two commands above
again; creating the environment a second time does no harm.
```
