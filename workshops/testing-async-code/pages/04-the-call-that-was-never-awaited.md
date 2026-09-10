---
title: The call that was never awaited
requires: [verify:pending-caught]
---

# The call that was never awaited

Here is the async bug worth a page of its own. `Notifier.nudge()` in
`push.py` calls `self.client.send()` and forgets the `await`. It
compiles, it runs, and it does nothing.

An event has two moments, the call and the completion, and
`Event.finished` says whether the second ever happened. For a
coroutine that means "was it awaited", so the assertion that catches
this bug is one filter, `pending()`. The cell also collects the
warning Python raises when the dropped coroutine is collected, to
read it afterwards rather than have it interrupt the output.

```{cell-insert}
:id: insert-nudge
:path: {{ notebook }}
:tags: [nudge]
:run: true
send.on_call.returns("queued")

with send, wrapture.timeline() as tape:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        await notifier.nudge("ana")
    send.events.assert_once()
    called = len(send.events)
    awaited = len(send.events.finished())
    still_open = tape.pending

warned = [str(warning.message) for warning in caught]
called, awaited, still_open, warned
```

The send was called, which is why the `assert_called()` habit from
`unittest.mock` misses this bug, but it never finished: nothing was
awaited. The tape counts its open events too, so the smell shows even
without a targeted assertion; the tape's repr reads `1 pending` while
that stays true.

Python's own safety net is the "coroutine was never awaited"
`RuntimeWarning` when the dropped coroutine is collected. wrapture
names that warning usefully as well: the coroutine a stubbed
`async def` hands back carries the target's name, so the warning says
`PushClient.send`, not the name of some library helper.

```{verify}
:id: pending-caught
:label: The send was called, never awaited, and the tape says so
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-nudge; cell-executed nudge
called == 1 and awaited == 0 and still_open == 1 and any("PushClient.send" in message for message in warned)
```

```{hint}
:title: If the check fails
The cell must await `notifier.nudge("ana")` inside both `with` blocks
and read the counts before the timeline closes. `still_open` is
`tape.pending`, the number of events with no completion yet, which
should be one.
```
