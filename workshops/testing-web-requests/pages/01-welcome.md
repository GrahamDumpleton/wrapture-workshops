---
title: Welcome
requires: [verify:env-ready]
---

# Requests in tests, and at the boundary

The tracing workshops watched the Flask shop from outside, under the
runner, with a config file. A test wants the same view from inside:
send a request through the test client and assert on what the
request did, not only on the response it returned. This workshop
runs the Flask instrumentation for the scope of a test, reads the
request event it records, and then goes one step further, to a
binding on the application's own WSGI boundary, where a test can
answer a request without the application, make the server see a
fault, and change a response on its way out.

## The shop, built by a factory

{open}`webshop.py` is the shop behind Flask from the earlier
workshops with two changes. It has an `/export.csv` route that
streams its body a row at a time, and the application is built by a
`create_app()` factory rather than at import, which is how a Flask
application is usually tested and, on the next page, the thing that
matters. The quote view still raises a `KeyError` for an item that is
not in the catalog, which Flask turns into a 500, and {open}`shop.py`
is the order service beneath it.

## An environment for the tests

wrapture is not installed in this JupyterLab, so make a virtual
environment in this directory and install wrapture, the
wrapture-instrumentation package that knows about Flask, Flask
itself and pytest. The commands run in the terminal below the
editor, which stays activated for the rest of the workshop.

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
:title: Install wrapture, its Flask instrumentation, Flask and pytest
:wait: prompt
pip install wrapture==1.0.0a22 wrapture-instrumentation==1.0.0a1 flask pytest
```

```{verify}
:id: env-ready
:label: wrapture, wrapture-instrumentation, Flask and pytest are installed in .venv
:substrate: shell
:trigger: after:install-deps
.venv/bin/python -c "import wrapture, flask, pytest, importlib.metadata as m; print('wrapture', wrapture.__version__, 'with wrapture-instrumentation', m.version('wrapture-instrumentation') + ', Flask', m.version('flask'), 'and pytest', pytest.__version__)"
```

```{hint}
:title: If the check fails
The virtual environment must be at `.venv` in this directory, with
all four packages installed into it. Run the two commands above
again; creating the environment a second time does no harm.
```
