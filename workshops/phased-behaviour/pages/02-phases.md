---
title: Phases
requires: [verify:retry-recovered]
---

# Phases

With mock the retry test is a `side_effect` list of two timeouts and a
canned dictionary. What the list cannot say is "and then run the real
code": every entry is a fabricated outcome, so the test proves the
loop retries but not that the real method is what it eventually
reaches.

In wrapture the behaviour configured on `on_call` is phase 0, and
`then()` adds the phase that takes over from it, with the argument
saying when the hand-over happens. Each phase is a complete behaviour
of its own with the full vocabulary, and nothing is inherited between
them, so a phase with no terminal runs the real operation. Stating
`passes_through()` on it is optional, and worth writing when running
the real thing is the point.

```{cell-insert}
:id: insert-phases
:path: {{ notebook }}
:tags: [phases]
:run: true
fetch = wrapture.binding(Client, "fetch")
fetch.on_call.raises(TimeoutError("busy"))

recovered = fetch.on_call.then(after=2)
recovered.passes_through()

print(fetch.on_call.explain())
```

The first two calls raise, and every call after that is real. Record
the retry loop and watch the hand-over: the tape marks which outcomes
were injected and which were real, each event carries the index of the
phase that handled it, and the binding knows which phase it is in.

```{cell-insert}
:id: insert-retry
:path: {{ notebook }}
:tags: [retry]
:run: true
with wrapture.timeline(fetch) as tape:
    result = fetch_with_retry(Client(), "/orders")
    handled = (fetch.events.in_phase(0).count, fetch.events.in_phase(1).count)

print(result)
print(tape.tree())
handled, fetch.phase
```

`in_phase()` counts the calls a phase handled and `binding.phase` is
the index of the phase active now. They answer different questions,
since a phase can be entered and left without handling a call. Phases
restart at 0 on every `apply()`, so a binding handed to `timeline()`
starts its script afresh in each test that uses it.

The give-up path is the same script with a bigger count. With
`then(after=3)` all three attempts raise, and the loop re-raises the
last one.

```{cell-insert}
:id: insert-give-up
:path: {{ notebook }}
:tags: [give-up]
:run: true
down = wrapture.binding(Client, "fetch")
down.on_call.raises(TimeoutError("busy"))
down.on_call.then(after=3).passes_through()

with wrapture.timeline(down) as tape:
    try:
        fetch_with_retry(Client(), "/orders")
    except TimeoutError as exc:
        outcome = f"gave up: {exc}"

print(outcome)
print(tape.tree())
```

```{verify}
:id: retry-recovered
:label: Two injected timeouts, then the real fetch, and the give-up path re-raised
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-give-up; cell-executed give-up
handled == (2, 1) and fetch.phase == 1 and outcome == "gave up: busy"
```

```{hint}
:title: Naming phases
The verbs on a phase return the phase, so `then(after=1).returns(b)`
works in one chain. Holding the phase in a variable named for what it
is, `recovered` here, and configuring it line by line as with
`on_call`, usually reads better in a test.
```
