---
title: The request event
requires: [verify:first-request-passes]
---

# The request event

`wrapture.instrumentation("flask")` applies the same instrumentation
the config file named, for the scope of a with-block, and removes it
on exit. It takes what an `[[instrument]]` entry's `name` takes, and
the entry's settings as keyword arguments. Flask is already imported
when the test module loads, so the hook fires on entry, and one thing
follows from how the hook works: the middleware is installed on each
application as it is constructed, so an application built before the
scope is untouched. That is why the shop has a factory. The fixture
enters the scope first and builds the application inside it.

The plugin's `tape` fixture opens a recording scope around each test
that asks for it, and the events the instrumentation's bindings
record land there, request and view alike.

```{file-write}
:id: write-conftest
:path: conftest.py
:open: true
import pytest
import wrapture

from webshop import create_app

pytest_plugins = ["wrapture.pytest_plugin"]


@pytest.fixture
def client():
    with wrapture.instrumentation("flask"):
        yield create_app().test_client()
```

One more habit the tests need. A request event is structurally a
generator event: the call to the application is one phase, and the
body the server consumes afterwards is the streaming tail, so the
event closes when the body closes. The test client hands back the
response without consuming it, so a test that reads the event before
consuming and closing the body sees it still open. `fetch()` plays
the server's part in full.

```{file-write}
:id: write-first-test
:path: test_requests.py
:open: true
import wrapture


def fetch(client, path):
    reply = client.get(path)
    reply.get_data()
    reply.close()
    return reply


def test_a_quote_is_one_request_tree(client, tape):
    reply = fetch(client, "/quote/widget")
    assert reply.status_code == 200

    request = tape.where(label="webshop.wsgi_app").assert_once()[0]
    assert request.kind == "request"
    assert request.result == "200 OK"
    assert request.data["method"] == "GET"
    assert request.data["path"] == "/quote/widget"
    assert request.data["route"] == "/quote/<item>"
    assert request.data["endpoint"] == "quote"

    view = tape.where(label="quote").assert_once()[0]
    assert view.parent_id == request.seq
    assert view.arguments == {"item": "widget"}
```

```{execute}
:id: run-first-test
:session: shell
:wait: prompt
pytest -q test_requests.py
```

The request records one event of kind `"request"`, labelled after the
application, and the assertion vocabulary needs nothing new for it.
The status line is its `result`, the way a return value is the
outcome of a call, so every filter and assertion shows it unchanged.
`data` carries the HTTP details: `method`, `path`, `query`, `scheme`,
`remote`, the response's content type and length, and the `bytes`
actually served. The instrumentation adds `route` and `endpoint` once
routing has matched, the low-cardinality keys a backend groups by,
and the view records beneath the request under its endpoint name with
its arguments captured. With no binding in hand, `tape.where()`
selects by the label an event is shown under, and `find_binding()`
would recover the view's proxy by its label the same way.

```{verify}
:id: first-request-passes
:label: The request tree test passes
:substrate: shell
:trigger: after:run-first-test
out=$(.venv/bin/python -m pytest -q --color=no test_requests.py 2>&1) && printf '%s\n' "$out" | grep -q '1 passed' && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check runs `pytest -q test_requests.py` with the venv's own
interpreter. A `NoBindingError` or an empty `EventLog` in the failure
means the instrumentation did not record the request: the
application must be built inside the `instrumentation()` scope, which
the `client` fixture does, and the test must ask for the `tape`
fixture. A `result` of `MISSING` means the body was not consumed and
closed.
```
