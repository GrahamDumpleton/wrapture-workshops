---
title: Concurrent sends
requires: [verify:fan-out-recorded]
---

# Concurrent sends

Real notifiers fan out concurrently. `ConcurrentNotifier` gathers one
send per user, and each task's events land on the shared tape,
correctly attributed, so the test asserts on the whole fan without
caring how the scheduler interleaved it.

```{cell-insert}
:id: insert-concurrent
:path: {{ notebook }}
:tags: [concurrent]
:run: true
with send, wrapture.timeline() as tape:
    count = await ConcurrentNotifier(PushClient()).broadcast(["ana", "ben", "cal"], "hi")
    send.events.finished().assert_times(3)
    users = sorted(event.arguments["user"] for event in send.events)
    left_open = tape.pending

count, users, left_open
```

Three sends, all finished, nothing left pending. The tape is scoped by
context, and asyncio tasks inherit the context they were created in,
so every task created by `gather()` records onto this timeline. Calls
made inside a coroutine's body nest under its event even when other
tasks run in between.

```{verify}
:id: fan-out-recorded
:label: All three concurrent sends finished on one tape
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-concurrent; cell-executed concurrent
count == 3 and users == ["ana", "ben", "cal"] and left_open == 0
```

```{hint}
:title: If the check fails
The `send` binding must still be configured to return `"queued"` from
the previous page. `left_open` should be zero: `gather()` awaits every
send before `broadcast()` returns.
```
