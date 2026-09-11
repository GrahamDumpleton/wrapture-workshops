---
title: Welcome
requires: [verify:env-ready]
---

# One trace across two processes

wrapture's event linkage, the sequence numbers and parent ids that
rebuild a tree, is process local. A trace identity extends the tree
across processes: every tree of events carries a W3C trace id, minted
at its root, and the identity travels in the `traceparent` header of
outbound requests, so two services both observed by wrapture join
their trace files on one id, with or without a tracing backend
involved.

The mechanism is on by default and costs nothing when nothing
listens: a root call, request or block that inherited no context
mints one random id per tree, only while events are being recorded
at all. Children share their tree's identity, and every JSON Lines
line carries it under its `trace` key.

## Two programs, standard library only

{open}`client.py` places three orders through {open}`frontend.py`,
which fetches quotes over HTTP with `urllib`, and {open}`server.py`
serves them from {open}`backend.py`, a WSGI application with no
framework at all, on port {{ quote_port }}. Neither side imports anything beyond
the standard library, and the server never mentions wrapture. The
client's one embedded touch is a pair of `wrapture.block()` markers
in `fetch_quote`, splitting the exchange into making the request and
consuming the reply, two phases `urlopen()` cannot separate by
itself since the response leaves the call with its body unread.

The last two pages bring a third program, an upload service that
hands work to a thread pool and a queue rather than waiting for it.

## An environment for both

wrapture is not installed in this JupyterLab, so make a virtual
environment in this directory and install it. The commands run in
the terminal on the left, under the editor, which stays activated for
the rest of the workshop and is where the server runs. The terminal
on the right is for the client.

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
wrapture installed into it. Run the two commands above again;
creating the environment a second time does no harm.
```
