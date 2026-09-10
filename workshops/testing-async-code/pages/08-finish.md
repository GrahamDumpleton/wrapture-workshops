---
title: Finish
requires: [quiz:pending-never]
---

# Finish

Nothing about the bindings changed for async code; what changed is
when the outcome arrives:

- `returns()` and `raises()` on an `async def` target deliver on
  `await`, so the code under test runs its real loop and its real
  `except`.

- An event has two moments. `finished()` and `pending()` filter on the
  second, and `tape.pending` counts what never completed, which is how
  a call that was never awaited is caught.

- Concurrent tasks inherit the recording context, so a fan-out lands
  on one tape, each event correctly attributed.

- On an async generator, `returns()` yields the items under
  `async for` and `raises()` fails the iteration, where the consumer's
  error handling lives.

- Under pytest-asyncio the plugin's `tape` fixture spans each test,
  and `pending().assert_never()` is the line to keep.

```{quiz}
:id: pending-never
:title: The habit worth keeping
question: "Why adopt send.events.pending().assert_never() in every async test, even ones that pass today?"
options:
  - { text: "It costs nothing while every call is awaited, and it is the line that fails when someone later deletes an await", correct: true }
  - { text: "It makes the test wait for any coroutine still running before the assertions", explanation: "It asserts, it does not wait. An event still pending at that point is reported as a failure, not awaited." }
  - { text: "Without it, returns() on an async target would return the value at the call instead of on await", explanation: "How a stub delivers its outcome is decided by the target's calling convention, not by any assertion." }
  - { text: "It clears the pending events so the next test starts with an empty tape", explanation: "A tape is never cleared, and each test's tape is its own. The filter only reads." }
explanation: A dropped coroutine records an event whose second moment never comes. The assertion reads that state and is otherwise inert, so it belongs in every async test as a guard against a future missing await.
```

The Finish button below says where to go next.
