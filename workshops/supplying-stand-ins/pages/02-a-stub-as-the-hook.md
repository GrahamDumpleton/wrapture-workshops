---
title: A stub as the hook
requires: [verify:hook-fired]
---

# A stub as the hook

The hook is one callable that the pipeline promises to call. A bare
`stub()` accepts any arguments, returns `None`, and records; the label
names it in events and failure output. The transport is not the
subject of this first test, so its methods are stubbed too, one
collaborator built from the named class with `mock()`. Every method of
`Transport` becomes a recording stub that returns `None` until
configured; `open_channel` is configured to return a `Channel` double
so the pipeline has something to publish on.

```{cell-insert}
:id: insert-hook
:path: {{ notebook }}
:tags: [hook]
:run: true
hook = wrapture.stub("on_complete")

channel = wrapture.mock(Channel)
transport = wrapture.mock(Transport)
transport.open_channel.returns(channel)

pipeline = Pipeline(transport, on_complete=hook)

with wrapture.timeline():
    sent = pipeline.run(["job-1", "job-2"])
    hook.events.assert_times(2)
    reported = [event.args for event in hook.events]

sent, reported
```

The hook fired once per job, with the arguments the pipeline actually
sent riding on the event. A bare stub accepts anything, so they record
under its `*args` and `**kwargs` rather than by name. Not caring what
arrives is the point of reaching for a bare stub, and it is the
explicit opposite of the package's default strictness. Note the
`timeline()` with no bindings: stubs and mocks are already observed,
so the timeline only opens the recording scope. Outside one, their
`events` are not kept, which is why the cell reads them inside.

```{verify}
:id: hook-fired
:label: The hook recorded one call per job with the pipeline's arguments
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-hook; cell-executed hook
sent == 2 and reported == [("job-1", "sent"), ("job-2", "sent")]
```
