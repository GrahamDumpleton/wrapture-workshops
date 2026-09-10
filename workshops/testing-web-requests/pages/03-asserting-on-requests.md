---
title: Asserting on requests
requires: [verify:four-tests-pass]
---

# Asserting on requests

Three more things a request event says that a response does not.
The export streams its body, and the event counts the chunks and the
bytes as the server consumed them, so a test can tell that a route
actually streamed rather than built a list. A view that raises rarely
shows the exception on the request event, because Flask catches it
and answers 500 from its own handler, so the request completes with a
status and no exception; the instrumentation notes the exception
against the request from that handler, and `raising()` finds it
either way. And a path the instrumentation is told to ignore records
nothing at all, the view included, so a health check leaves the tape
empty rather than leaving a parentless view behind.

```{file-write}
:id: append-tests
:path: test_requests.py
:mode: append
:open: true



def test_the_export_streams(client, tape):
    reply = fetch(client, "/export.csv")
    assert reply.status_code == 200

    request = tape.where(label="webshop.wsgi_app").assert_once()[0]
    assert request.result == "200 OK"
    assert request.items == 3
    assert request.data["bytes"] == 30


def test_a_missing_item_answers_500_for_a_reason(client, tape):
    reply = fetch(client, "/quote/missing")
    assert reply.status_code == 500

    request = tape.where(label="webshop.wsgi_app").raising(KeyError).assert_once()[0]
    assert request.result == "500 INTERNAL SERVER ERROR"
    assert request.exception is None
    assert request.failed


def test_health_checks_are_not_recorded(tape):
    from webshop import create_app

    with wrapture.instrumentation("flask", ignore_paths=["/health"]):
        client = create_app().test_client()
        fetch(client, "/health")
        fetch(client, "/quote/gizmo")

    tape.where(label="webshop.wsgi_app").assert_once()
    assert [event.data["path"] for event in tape.roots()] == ["/quote/gizmo"]
```

```{execute}
:id: run-four-tests
:session: shell
:wait: prompt
pytest -q test_requests.py
```

Four pass. In the export test, `items` is the number of chunks the
body produced and `data["bytes"]` what reached the server, with
`duration` running to the last byte and `body_duration` the time
spent producing chunks. In the 500 test, `exception` is `None`
because the application returned normally as far as the middleware
saw, `failed` is true because the note is a failure, and the
`KeyError` sits under `caught` where `raising()` looks. The last test
passes a setting the way the config file would, and asks for the
application itself, since the fixture's scope has no ignore list; a
second scope in the same test would be refused, because one target
is instrumented once per process at a time.

```{verify}
:id: four-tests-pass
:label: All four request tests pass
:substrate: shell
:trigger: after:run-four-tests
out=$(.venv/bin/python -m pytest -q --color=no test_requests.py 2>&1) && printf '%s\n' "$out" | grep -q '4 passed' && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check runs the file with the venv's own interpreter and expects
four passes. A failure in the export test with `items` of 1 means
the route returned a list rather than a generator; a failure in the
500 test means `raising()` found no noted `KeyError`, so the
instrumentation was not applied; a failure in the last test with two
roots means `ignore_paths` was not passed.
```
