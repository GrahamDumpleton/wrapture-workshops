---
title: Welcome
requires: [verify:env-ready, verify:app-runs]
---

# Instrumenting a package nobody has covered

The Flask workshops switched on a whole framework's tracing with one
`[[instrument]]` entry, and the patching workshop put a small
`Instrumentation` class next to a config file to change what a
vendored client sent. This workshop is the author's side in full: a
class for a library that nobody has covered, from the shape of the
class to how it would be packaged, so that the next library you meet
without instrumentation is an afternoon's work rather than a
mystery.

## The library

{open}`hookline/client.py` and {open}`hookline/dispatch.py` make up
hookline, a small webhook library. `Client.deliver()` sends a payload
to a subscriber's URL, with a connect and a write step beneath it,
and raises `DeliveryError` for a subscriber that is down.
`Dispatcher.register()` stores a handler per kind of event,
`dispatch()` runs the matching one, and a handler that raises is
absorbed by `on_error()`, so `dispatch()` returns `None` rather than
failing. {open}`app.py` uses both halves: two deliveries, one to a
subscriber that is down, and two dispatched events, one to a handler
that raises. Nothing in any of them imports wrapture.

## An environment

wrapture is not installed in this JupyterLab, so make a virtual
environment in this directory and install wrapture and pytest, for
the tests on the fifth page. The commands run in the terminal below
the editor, which stays activated for the rest of the workshop.

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
:title: Install wrapture and pytest
:wait: prompt
pip install wrapture==1.0.0a22 pytest
```

```{verify}
:id: env-ready
:label: wrapture and pytest are installed in .venv
:substrate: shell
:trigger: after:install-deps
.venv/bin/python -c "import wrapture, pytest; print('wrapture', wrapture.__version__, 'and pytest', pytest.__version__)"
```

Run the application once as it is, to see what it prints on its own.

```{execute}
:id: run-plain
:session: shell
:wait: prompt
python app.py
```

```
delivery failed: https://globex.example/down: connection refused
emailed ann@example.com
None
failures: [('order.failed', ValueError('no handler for card declined'))]
```

```{verify}
:id: app-runs
:label: The application runs unobserved
:substrate: shell
:trigger: after:run-plain
out=$(.venv/bin/python app.py 2>&1) && printf '%s\n' "$out" | grep -q '^failures: \[(.order.failed., ValueError' && { echo "Two deliveries and two dispatches, one of each failing, and nothing observed"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If a check fails
The virtual environment must be at `.venv` in this directory, with
wrapture and pytest installed into it, and `app.py` must run from
this directory so that the `hookline` package beside it is found.
```
