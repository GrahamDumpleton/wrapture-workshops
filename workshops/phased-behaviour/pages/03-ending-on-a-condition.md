---
title: Ending on a condition
requires: [verify:breaker-tripped]
---

# Ending a phase on a condition

A count is one of three ways a phase can end. `then(until=fn)` ends the
phase once `fn(event)` is true for a call it handled. The event is the
same one a timeline would record, seen as the caller saw it, so the
condition can look at the arguments, the result, or whether the call
raised. That is enough to build a circuit breaker: run the real call
until one fails, then fail fast without touching the remote at all.

Fetch two good URLs, one bad one that the real `fetch()` rejects, and
then another good one.

```{cell-insert}
:id: insert-breaker
:path: {{ notebook }}
:tags: [breaker]
:run: true
class CircuitOpen(Exception):
    pass


def failed(event):
    return event.exception is not None


breaker = wrapture.binding(Client, "fetch")
breaker.on_call.passes_through()

tripped = breaker.on_call.then(until=failed)
tripped.raises(CircuitOpen("circuit open"))

outcomes = []
with wrapture.timeline(breaker) as tape:
    client = Client()
    for url in ["/a", "/b", "/bad", "/c"]:
        try:
            outcomes.append(client.fetch(url)["status"])
        except Exception as exc:
            outcomes.append(type(exc).__name__)

print(tape.tree())
outcomes
```

The `ConnectionError` is real, raised by the real method for a real
reason, and the `CircuitOpen` after it is the binding's. The tape
marks only the second as injected. A `side_effect` list has no way to
express a phase whose boundary depends on what the real code did.

```{verify}
:id: breaker-tripped
:label: The real failure tripped the breaker and the next call failed fast
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-breaker; cell-executed breaker
outcomes == [200, 200, "ConnectionError", "CircuitOpen"]
```
