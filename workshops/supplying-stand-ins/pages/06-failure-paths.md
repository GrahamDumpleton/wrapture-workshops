---
title: Failure paths, reconfigured in place
requires: [verify:closed-on-failure]
---

# Failure paths, reconfigured in place

Every mock method carries the same `returns()` and `raises()` verbs,
so a failure is injected where the test needs it and the pipeline's
clean-up promise is checked: the channel must be closed even when a
publish blows up. The behaviour is put back afterwards, since the
double is shared by the cells above.

```{cell-insert}
:id: insert-failure
:path: {{ notebook }}
:tags: [failure]
:run: true
channel.publish.raises(ConnectionError("broker gone"))

with wrapture.timeline():
    try:
        pipeline.run(["job-1"])
    except ConnectionError as exc:
        failure = str(exc)
    channel.close.events.assert_once()
    closed = channel.close.events.count

channel.publish.returns(None)

failure, closed
```

Two doubles of the same class stay apart, each recording its own
events, so a pipeline that opens one channel per priority can be
tested without the calls merging.

```{cell-insert}
:id: insert-apart
:path: {{ notebook }}
:tags: [apart]
:run: true
fast, slow = wrapture.mock(Channel), wrapture.mock(Channel)

with wrapture.timeline():
    fast.publish("job-1", routing_key="fast")
    slow.publish("job-2")
    fast.publish.events.assert_once()
    slow.publish.events.with_args(routing_key="jobs").assert_once()
    apart = (fast.publish.events.count, slow.publish.events.count)

apart
```

A double is a value like a stub: the test places it and owns its
lifetime, and nothing needs removing afterwards, because nothing was
installed anywhere. To substitute a class at a location instead, so
code that constructs its own collaborator gets doubles, hold a
factory in a value binding on that location.

```{verify}
:id: closed-on-failure
:label: The channel was closed after the failed publish, and two doubles stayed apart
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-apart; cell-executed apart
failure == "broker gone" and closed == 1 and apart == (1, 1)
```
