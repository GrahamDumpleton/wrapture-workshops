---
title: Finish
requires: [quiz:sequence-end]
---

# Finish

Phases are for behaviour that must change within one call of the code
under test, as it happens with a retry loop, a breaker or a polling
wait. Four ways a phase ends:

- `then(after=n)`, once the phase has handled `n` calls: the retry
  loop, and the give-up path with a bigger count.

- `then(until=fn)`, once `fn(event)` is true for a call it handled: the
  circuit breaker tripping on a real failure.

- A bare `then()` after `returns_from()`, when the sequence runs out:
  the polling loop settling on done. With no successor the exhaustion
  is a loud error.

- `advance()`, from the test or from a stage on another binding: the
  remote coming back when the monitor reported healthy.

A test that sits between calls does not need phases; it reconfigures
the binding in place and carries on. `passes_through()` on `on_call`
clears phase 0 only; `on_call.reset()` drops the whole chain.

```{quiz}
:id: sequence-end
:title: When a sequence phase ends
:shuffle: true
question: "After status.on_call.returns_from(['queued', 'running']), when does a bare status.on_call.then() take over?"
options:
  - { text: "On the third call, the one that finds the sequence empty", correct: true }
  - { text: "Only when the test calls status.advance()", explanation: "advance() works too, but a phase whose terminal is a sequence also ends when the sequence runs out." }
  - { text: "After the second call returns, before anything else happens", explanation: "The phase ends when a call finds the sequence empty; that call is handled by the successor." }
explanation: A returns_from() phase ends when a call finds its sequence exhausted, and that same call is handled by the next phase. advance() can end it early as well.
```

The Finish button below says where to go next.
