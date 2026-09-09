---
title: Sequences
requires: [verify:polling-settled]
---

# Sequences

For "return the next value on each call" a phase per value would be
tiresome, so `returns_from(iterable)` is a terminal that draws
successive values, one per call, lazily. A generator or
`itertools.cycle()` works too. When the sequence runs out the phase
ends and the call that found it empty is handled by the successor, so
a bare `then()` after a sequence means "when it is exhausted". A
polling loop is the natural example.

```{cell-insert}
:id: insert-polling
:path: {{ notebook }}
:tags: [polling]
:run: true
status = wrapture.binding(Job, "status")
status.on_call.returns_from(["queued", "running", "running"])

settled = status.on_call.then()
settled.returns("done")

with wrapture.timeline(status) as tape:
    finished = wait_for(Job())

print(tape.tree())
finished
```

This is the closest thing to mock's `side_effect` list, and the
deliberate difference is that values and exceptions are kept apart:
`side_effect=[a, b, Err]` becomes `returns_from([a, b])` followed by a
phase that `raises(Err)`. More lines for the same three outcomes, but
each phase says what it is.

Running out with no successor is a loud error at the call site rather
than a `StopIteration` leaking out of the code under test, and the
message says what to do.

```{cell-insert}
:id: insert-exhausted
:path: {{ notebook }}
:tags: [exhausted]
:run: true
short = wrapture.binding(Job, "status")
short.on_call.returns_from(["queued", "running"])

try:
    with short:
        wait_for(Job())
except wrapture.SequenceExhaustedError as exc:
    exhausted = str(exc)

print(exhausted)
```

```{verify}
:id: polling-settled
:label: The poll settled on done, and the short sequence failed loudly
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-exhausted; cell-executed exhausted
finished and "add one with then()" in exhausted
```

```{hint}
:title: A known sequence of random numbers
`binding(random, "random").on_call.returns_from([0.1, 0.9, 0.5])`
makes code that jitters or samples deterministic without seeding
tricks. It catches `random.random()` callers; code holding its own
`random.Random()` instance is covered by binding `random.Random`
instead.
```
