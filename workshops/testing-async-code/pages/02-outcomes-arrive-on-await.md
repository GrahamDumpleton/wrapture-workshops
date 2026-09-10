---
title: Outcomes arrive on await
requires: [verify:stub-awaited]
---

# Outcomes arrive on await

`returns()` on a binding whose target is `async def` does not return
the value from the call, because the real method would not either.
The call still produces an awaitable, and the value arrives when it
is awaited. The notifier's `await` works unchanged against the stub.

```{cell-insert}
:id: insert-stub
:path: {{ notebook }}
:tags: [stub]
:run: true
send = wrapture.binding(PushClient, "send")
send.on_call.returns("queued")

with send, wrapture.timeline() as tape:
    delivered = await notifier.broadcast(["ana", "ben"], "hello")
    send.events.finished().assert_times(2)
    sent = [event.arguments["user"] for event in send.events]
    tree = tape.tree()

print(tree)
delivered, sent
```

Two sends, both finished, and the notifier counted two deliveries
through its own loop. The tree marks each result `(injected)`, since
the value came from the stub, and the `finished()` filter is the one
to notice: an event on an async target completes when the coroutine
does, not when the call is made. The next pages turn on that
distinction.

```{verify}
:id: stub-awaited
:label: Both sends were awaited and the stubbed value arrived on await
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-stub; cell-executed stub
delivered == 2 and sent == ["ana", "ben"]
```

```{hint}
:title: If the check fails
`send` must be a binding on `PushClient.send` with `returns("queued")`
configured, and the cell must await `notifier.broadcast()` inside the
`with` block. Run the cell again after any edit.
```
