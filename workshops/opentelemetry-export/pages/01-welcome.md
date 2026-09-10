---
title: Welcome
requires: [verify:env-ready]
---

# The same events, sent to a backend

Everything in the tracing workshops so far rendered a trace for a
person to read or wrote it to a file for later. The other destination
is a tracing backend, fed while the application runs, and
OpenTelemetry is the one the ecosystem has converged on. wrapture
treats it as a first-class destination rather than something bolted
on: the `wrapture.otel` subpackage ships in every wheel, and the
`otel` extra brings the SDK and the OTLP exporter with it. A plain
install pays nothing for this, since nothing in base wrapture imports
the subpackage until a config asks for it.

No collector is needed here. The SDK's console exporters print the
spans and the metrics to standard output instead, and the pages read
them back from there.

{open}`webshop.py` is the shop behind Flask from the earlier
workshops, unchanged, with {open}`shop.py` beneath it. {open}`spans.py`
reads the console exporters' output back, and the last page brings a
second pair of programs, a client and a quote service, for one trace
across two processes.

## An environment for the server

wrapture is not installed in this JupyterLab, so make a virtual
environment in this directory and install wrapture with its `otel`
extra, its Flask instrumentation and Flask. The commands run in the
terminal on the left, under the editor, which stays activated for the
rest of the workshop and is where the servers run. The terminal on the
right is for sending requests.

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
:title: Install wrapture with the otel extra, its Flask instrumentation and Flask
:wait: prompt
pip install "wrapture[otel]==1.0.0a22" wrapture-instrumentation==1.0.0a1 flask
```

```{verify}
:id: env-ready
:label: wrapture with the otel extra, wrapture-instrumentation and Flask are installed in .venv
:substrate: shell
:trigger: after:install-deps
.venv/bin/python -c "import wrapture, wrapture.otel, flask, importlib.metadata as m; print('wrapture', wrapture.__version__, 'with opentelemetry-sdk', m.version('opentelemetry-sdk') + ', wrapture-instrumentation', m.version('wrapture-instrumentation'), 'and Flask', m.version('flask'))"
```

```{hint}
:title: If the check fails
The virtual environment must be at `.venv` in this directory, with
the three packages installed into it; the quotes around
`wrapture[otel]` matter, since the brackets mean something to the
shell. Run the two commands above again; creating the environment a
second time does no harm.
```
