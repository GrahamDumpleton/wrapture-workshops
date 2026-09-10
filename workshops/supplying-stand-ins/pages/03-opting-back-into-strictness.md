---
title: Opting back into strictness
requires: [verify:contract-checked]
---

# Opting back into strictness

The hook contract is worth checking too: the pipeline must call it as
`on_complete(job, outcome)`. `mimics=` borrows a real callable's
signature, so the stub checks each call and records arguments by
parameter name, and `with_args()` can match them. `pipeline.py`
documents the contract as a function, which is what the stub mimics.

```{cell-insert}
:id: insert-mimics
:path: {{ notebook }}
:tags: [mimics]
:run: true
hook = wrapture.stub(mimics=on_complete)
pipeline = Pipeline(transport, on_complete=hook)

with wrapture.timeline():
    pipeline.run(["job-1"])
    hook.events.with_args(job="job-1", outcome="sent").assert_once()
    by_name = hook.events.first.arguments

by_name
```

If the pipeline drifted, calling the hook with an extra keyword or
forgetting an argument, the call would raise `TypeError` exactly as
the real hook would, before anything was recorded. Call it wrongly by
hand to see the check fire.

```{cell-insert}
:id: insert-drift
:path: {{ notebook }}
:tags: [drift]
:run: true
try:
    hook("job-1")
except TypeError as exc:
    drift = str(exc)

drift
```

Integration drift between the pipeline and its hooks cannot hide
behind the stand-in. `mimics=` borrows the kind of the callable too:
a stub mimicking an `async def` is a coroutine function and is
awaited like one, and for a stand-in with nothing to mimic, `kind=`
states the calling convention directly.

```{verify}
:id: contract-checked
:label: The mimicking stub records by name and rejects a drifted call
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-drift; cell-executed drift
by_name == {"job": "job-1", "outcome": "sent"} and "outcome" in drift
```
