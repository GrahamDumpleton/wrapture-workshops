---
title: A timeout mid-broadcast
requires: [verify:timeout-handled]
---

# A timeout mid-broadcast

`raises()` is the same shape: the exception arrives on await, so the
notifier's `except TimeoutError` around the `await` is what handles
it. `then(after=1)` lets the first send succeed and fails every send
after it, and the partial-result behaviour is tested with the real
control flow.

```{cell-insert}
:id: insert-timeout
:path: {{ notebook }}
:tags: [timeout]
:run: true
send.on_call.then(after=1).raises(TimeoutError("gateway busy"))

with send, wrapture.timeline() as tape:
    delivered = await notifier.broadcast(["ana", "ben", "cal"], "hello")
    send.events.raising(TimeoutError).assert_once()
    timed_out = send.events.raising(TimeoutError).first.arguments["user"]
    attempted = len(send.events)

send.on_call.reset()
delivered, timed_out, attempted
```

One user was delivered to, the second send timed out, and the third
was never attempted, all through the notifier's real loop. The last
line clears the phases so the next page starts from a plain binding.

```{verify}
:id: timeout-handled
:label: The broadcast stopped at the second send
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-timeout; cell-executed timeout
delivered == 1 and timed_out == "ben" and attempted == 2
```

```{hint}
:title: If the check fails
The phase must be added on the same `send` binding the previous page
configured, with `after=1`, so the first send still returns `"queued"`
and the second raises. If the cell was run twice, the earlier
`reset()` already cleared the phases; run the previous page's cell
again first.
```
