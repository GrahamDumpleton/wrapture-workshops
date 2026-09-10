---
title: Welcome
requires: [verify:env-ready]
---

# Where the time goes

The `/order` endpoint of the Flask shop is slow. The view calls the
order service, the service calls the gateway and then the ledger, and
the question is which of those the time is going to. This copy of the
shop, {open}`shop.py`, has the cause planted in it, and the workshop
pretends not to know where.

The usual move is a stopwatch. A `perf_counter()` before and after the
service call, a log line with the difference, another pair around the
gateway, another around the ledger. Each of those is a code change in
a layer that should not know it is being measured, the numbers arrive
as separate log lines that you correlate by eye, and none of them are
tied to the request they belong to, so one slow request among fast
ones is invisible in the average. A profiler has the opposite problem:
it sees every frame in the process, most of them framework internals,
and cannot tell one request from the next.

{open}`webshop.py` is the shop behind Flask from the previous
workshop, and {open}`wrapture.toml` is the config that traced it,
with the health check already ignored. {open}`traffic.py` sends
thirty requests, for a later page.

## An environment for the server

wrapture is not installed in this JupyterLab, so make a virtual
environment in this directory and install wrapture, its Flask
instrumentation, Flask and pytest. The commands run in the terminal on
the left, under the editor, which stays activated for the rest of the
workshop and is where the server and the test will run. The terminal
on the right is for sending requests.

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
.venv/bin/python -c "import wrapture, flask, pytest, importlib.metadata as m; print('wrapture', wrapture.__version__, 'with wrapture-instrumentation', m.version('wrapture-instrumentation'), 'Flask', m.version('flask'), 'and pytest', pytest.__version__)"
```

```{hint}
:title: If the check fails
The virtual environment must be at `.venv` in this directory, with
all four packages installed into it. Run the two commands above
again; creating the environment a second time does no harm.
```
