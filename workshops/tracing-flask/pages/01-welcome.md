---
title: Welcome
requires: [verify:env-ready]
---

# One request as one tree

For a web application the natural unit of tracing is the request: one
HTTP request, its method, path and status, and every observed call
made while handling it, as one tree. The config file from the previous
workshop cannot give you that on its own, and it is worth being clear
about why before showing what does.

A WSGI application looks like any other callable, but it routes the
interesting facts around the return value. The status and headers
travel through the `start_response` callback rather than being
returned. The body is an iterable that the server consumes after the
call has returned, so a streaming application does most of its work
after a call event would already have closed. And when a view raises,
the framework catches the exception and turns it into a 500 response
before any wrapper on the application ever sees it. A binding on the
application callable would record a call that returned an iterable
and raised nothing, which is true and useless.

## The shop behind Flask

{open}`webshop.py` is the shop from the earlier workshops behind a
small Flask application. A `/quote/<item>` route renders a template,
`/order` places an order through the `OrderService` in
{open}`shop.py`, and `/health` exists because every deployed service
has one. Nothing in it mentions wrapture. The quote
view raises a `KeyError` for an item that is not in the catalog, which
Flask turns into a 500, and that is the request this workshop most
wants to see.

## An environment for the server

wrapture is not installed in this JupyterLab, so make a virtual
environment in this directory and install wrapture, the
wrapture-instrumentation package that knows about Flask, and Flask
itself. The commands run in the terminal on the left, under the
editor, which stays activated for the rest of the workshop and is
where the server will run. The terminal on the right is for sending
requests to it.

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
pip install wrapture==1.0.0b1 wrapture-instrumentation==1.0.0b1 flask
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
