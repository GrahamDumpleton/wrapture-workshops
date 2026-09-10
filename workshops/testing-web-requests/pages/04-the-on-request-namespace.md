---
title: The on_request namespace
requires: [verify:boundary-tests-pass]
---

# The on_request namespace

Everything so far only watched. A binding on the application's WSGI
boundary can also intervene, and requests get a behaviour namespace
of their own, named for the event kind as `on_call` is; `on_call` on
a wsgi binding raises `WrongModeError` pointing at it. The mode is
never detected, because a WSGI application looks like any other
callable, so a binding says `mode="wsgi"` explicitly, and the
middleware it installs records the request itself, so these tests
need no instrumentation at all. Flask keeps its application callable
on the instance's `wsgi_app` attribute, the documented place for
middleware, and a callable binding on one instance affects only that
instance.

Terminals replace the application, exactly as `on_call.returns()`
replaces a call. `returns()` takes the status, the headers and the
body, an iterable of byte strings as in WSGI itself, and the recorded
event is marked injected. `raises()` makes the server see the
application raise. Stages intervene while the application still
runs: `transforms_environ` shapes what it sees, `transforms_response`
rewrites the status or headers on every `start_response` call, and
`transforms_body` wraps the iterable.

```{file-write}
:id: write-boundary-tests
:path: test_boundary.py
:open: true
import pytest
import wrapture

import webshop
from webshop import create_app


def fetch(client, path):
    reply = client.get(path)
    reply.get_data()
    reply.close()
    return reply


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def boundary(app):
    with wrapture.binding(app, "wsgi_app", mode="wsgi", label="webshop.wsgi_app") as boundary:
        yield boundary


def test_a_canned_response_never_reaches_the_application(app, boundary, tape):
    boundary.on_request.returns(
        "503 Service Unavailable", [("Content-Type", "text/plain")], [b"maintenance window\n"]
    )
    with wrapture.binding(webshop, "lookup").expect_never():
        reply = fetch(app.test_client(), "/quote/widget")

    assert reply.status_code == 503
    assert reply.get_data() == b"maintenance window\n"
    request = boundary.events.assert_once()[0]
    assert request.injected
    assert request.result == "503 Service Unavailable"


def test_the_server_sees_the_application_raise(app, boundary, tape):
    boundary.on_request.raises(ConnectionResetError("backend gone"))
    with pytest.raises(ConnectionResetError):
        app.test_client().get("/quote/widget")
    boundary.events.raising(ConnectionResetError).assert_once()


def test_a_failure_is_rewritten_on_the_way_out(app, boundary, tape):
    def hide(status, headers):
        if status.startswith("500"):
            return "503 Service Unavailable", [*headers, ("Retry-After", "60")]
        return status, headers

    boundary.on_request.transforms_response(hide)
    reply = fetch(app.test_client(), "/quote/missing")
    assert reply.status_code == 503
    assert reply.headers["Retry-After"] == "60"
    request = boundary.events.assert_once()[0]
    assert request.result == "503 Service Unavailable"
```

```{execute}
:id: run-boundary-tests
:session: shell
:wait: prompt
pytest -q test_boundary.py
```

Three pass. The canned response never called the application: the
binding on the shop's `lookup` helper, which the quote view calls,
records nothing, and the request event says `injected`. The fault
reaches the test client the way it would reach a real server, and
the event records the exception. The rewrite runs on the way out,
and the recorded status is the last one forwarded, so a test reading
the event sees what the client saw, not what the application said.
`boundary.explain()` lists the stages and terminal configured in the
order they apply, and `passes_through()` clears them all. Because
each test's fixture builds a fresh binding, nothing configured in one
test survives into the next.

```{verify}
:id: boundary-tests-pass
:label: The three boundary tests pass
:substrate: shell
:trigger: after:run-boundary-tests
out=$(.venv/bin/python -m pytest -q --color=no test_boundary.py 2>&1) && printf '%s\n' "$out" | grep -q '3 passed' && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check runs `test_boundary.py` with the venv's own interpreter
and expects three passes. A `WrongModeError` means the binding was
made without `mode="wsgi"`; a `MISSING` result in the rewrite test
means the body was not consumed and closed before the event was
read; a `ConfigError` about a target already instrumented means a
`instrumentation("flask")` scope from `conftest.py` is still open,
which these tests do not use.
```
