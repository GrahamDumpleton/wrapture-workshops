---
title: Advancing from outside
requires: [verify:recovered]
---

# Advancing from outside

The third way a phase ends is that something other than this binding's
own calls decides it should. A bare `then()` with no condition ends
only when the test calls `binding.advance()`, which also works whatever
the exit condition, so a test can force the next phase early. The
simplest use is a test that sits between calls.

```{cell-insert}
:id: insert-advance
:path: {{ notebook }}
:tags: [advance]
:run: true
remote = wrapture.binding(Client, "fetch")
remote.on_call.raises(ConnectionError("down"))
remote.on_call.then().passes_through()

with remote:
    client = Client()
    try:
        client.fetch("/x")
    except ConnectionError as exc:
        print("before advance:", exc)

    remote.advance()
    print("after advance:", client.fetch("/x"))
```

The more interesting use is when the trigger lives in a different
binding. Here the remote stays down until a health check, itself a
binding, reports it healthy, and the health check's own result stage
advances the remote. `reconnect()` polls the monitor and tries the
client each time round.

```{cell-insert}
:id: insert-health
:path: {{ notebook }}
:tags: [health]
:run: true
remote = wrapture.binding(Client, "fetch")
remote.on_call.raises(ConnectionError("down"))

online = remote.on_call.then()
online.passes_through()

health = wrapture.binding(Monitor, "check")
health.on_call.returns_from(["unhealthy", "unhealthy", "healthy"])
health.on_call.then().returns("healthy")


def note_recovery(result):
    if result == "healthy":
        remote.advance()


health.on_call.validates_result(note_recovery)

with wrapture.timeline(remote, health) as tape:
    recovered_fetch = reconnect(Monitor(), Client(), "/x")

print(tape.tree())
recovered_fetch
```

The two scripts interleave on the tape. A stage such as
`validates_result()` belongs to the phase it was configured on, which
follows from phases inheriting nothing from each other. That is why
"healthy" is the last value of the phase 0 sequence rather than the
value the successor returns: if the triggering value only ever came
from phase 1, the stage on phase 0 would never see it. A stage that
should run in every phase is configured in every phase. When the
condition is visible in the binding's own calls, `then(until=...)`
says it more directly, and is the form to reach for first.

```{verify}
:id: recovered
:label: The remote came back once the monitor reported healthy
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-health; cell-executed health
recovered_fetch == {"url": "/x", "status": 200} and remote.phase == 1 and tape.tree().count("(injected)") == 5
```
