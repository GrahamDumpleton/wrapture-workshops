---
title: Welcome
requires: [verify:env-ready]
---

# Changing what a library does

A vendored HTTP client sends every request the application makes. It
has no hook for what you now need: every request must carry a tenant
header, a transient connection reset should be retried once, and in
development the timeout it reads from a class attribute must be
clamped. The library is not yours to edit, and forking it to add
three lines means carrying that fork forever.

Assigning replacement functions onto the module is the traditional
answer, and it works until you need it not to. A hand-rolled patch
has no off switch, leaves no record of what was changed, cannot be
reconfigured without being reinstalled, and has to be placed after
the library's import in a way nothing enforces. wrapture treats a
patch as an object with a lifecycle. It wraps the real method rather
than replacing it, applies and removes cleanly, can be suspended and
reconfigured while installed, reports its own state honestly, and can
be installed at process start from a config file without the
application knowing.

{open}`vendored_client.py` is the stand-in for the vendored library.
{open}`transports.py` holds an `echo` transport that returns exactly
what the client handed it, so every run shows what the library would
have sent, and a `DropsFirst` transport for the retry page.
{open}`app.py` is the application, one request through the client,
for the last page.

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

Run the application once, as it stands.

```{execute}
:id: run-app
:session: shell
:wait: prompt
python app.py
```

```
{'method': 'GET', 'url': 'https://api.example/orders', 'headers': {}, 'timeout': 30}
```

No tenant header, no retry, a thirty second timeout. Each page from
here changes one of those without touching the library.

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
