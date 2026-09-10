---
title: A failure the code handled
requires: [verify:failure-noted]
---

# A failure the code handled

An event's `exception` is the exception that escaped the scope. Code
that catches an exception and handles it leaves the scope completing
normally, with a result and no exception, which is the honest record
of control flow but not of the failure. `OrderService.place` does
exactly that: it catches `CardDeclined` and returns a declined
outcome. `note_exception()` is the sibling of `annotate()` for that
place. It attaches the exception to the event without changing
control flow, and `shop.py` calls it in the `except` clause.

```{cell-insert}
:id: insert-noted
:path: {{ notebook }}
:tags: [noted]
:run: true
with wrapture.timeline(place, charge) as tape:
    outcome = service.place(250, "4000-0000-0000-0000", tenant="globex")

    declined = place.events.raising(CardDeclined).assert_once().first
    noted = declined.caught[0].exception
    tree = tape.tree()

print(tree)
outcome, declined.result == outcome, declined.exception, declined.failed, type(noted).__name__
```

The noted exception lands on the event's `caught` tuple, distinct
from `exception`, so the two facts never blur: the scope returned,
and a failure was noted against it. `event.failed` answers "did this
operation fail, however the failure surfaced", and `raising()` widens
to match, so the filter found the declined order even though `place`
returned normally. The tree shows the note as the same `!!` marker
after the result, so one line says both.

The common case is a framework whose error handler turns a `KeyError`
into a 500 response: the handler is the only place the exception can
be seen, and it is not the event that failed. That is what
`current_event(kind="request").note_exception(exc)` is for, aiming
the note at the request rather than at the handler's own call.

```{verify}
:id: failure-noted
:label: The declined order returned normally and still reads as failed
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-noted; cell-executed noted
declined.result == outcome and declined.exception is None and declined.failed and isinstance(noted, CardDeclined)
```

```{hint}
:title: If the check fails
The `place` binding must be handed to the timeline, and the order
must use the card ending in four zeros so the gateway declines it.
`declined.caught` is the tuple of noted exceptions; `shop.py` notes
one.
```
