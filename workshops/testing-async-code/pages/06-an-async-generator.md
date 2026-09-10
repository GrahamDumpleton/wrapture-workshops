---
title: An async generator
requires: [verify:items-on-iteration, verify:failure-on-iteration]
---

# An async generator

The receipts stream is an async generator, and its stub follows the
same rule: the outcome arrives the way the real protocol delivers it.
`returns()` on an async-generator target yields the given items under
`async for`, and the event records the iteration as one operation
with a live item count.

```{cell-insert}
:id: insert-stream
:path: {{ notebook }}
:tags: [stream]
:run: true
receipts = wrapture.binding(PushClient, "receipts")
receipts.on_call.returns(["r-1", "r-2"])

with receipts, wrapture.timeline():
    received = await collect_receipts(PushClient(), "batch-9")
    stream = receipts.events.finished().assert_once().first
    streamed = stream.items

received, streamed
```

```{verify}
:id: items-on-iteration
:label: The stubbed receipts arrived under async for
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-stream; cell-executed stream
received == ["r-1", "r-2"] and streamed == 2
```

`raises()` on the same target fails the iteration rather than the
call, which is where an `async for` consumer's error handling
actually lives.

```{cell-insert}
:id: insert-stream-error
:path: {{ notebook }}
:tags: [stream-error]
:run: true
receipts.on_call.raises(ConnectionError("stream dropped"))

with receipts, wrapture.timeline():
    try:
        await collect_receipts(PushClient(), "batch-9")
    except ConnectionError as exc:
        stream_error = str(exc)
    receipts.events.raising(ConnectionError).assert_once()

stream_error
```

The consumer's `except` caught it in the loop, and the one recorded
event carries the exception. A stream consumed halfway stays
`pending()`, the same two-moments rule as everywhere else.

```{verify}
:id: failure-on-iteration
:label: The stubbed failure reached the consumer on iteration
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-stream-error; cell-executed stream-error
stream_error == "stream dropped"
```

```{hint}
:title: If a check fails
`receipts` must be a binding on `PushClient.receipts`, the async
generator method. The first cell configures `returns()` with a list;
the second replaces it with `raises()`, so run them in order.
```
