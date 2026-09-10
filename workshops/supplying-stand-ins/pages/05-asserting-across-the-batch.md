---
title: Asserting across the batch
requires: [verify:batch-ordered]
---

# Asserting across the batch

Each method records events by parameter name, so the assertions read
the same as they would against a real binding, and the tape sees
stubs, mocks and real bindings together. Here the order of one batch
is checked end to end: the channel is opened, both jobs are published,
and the channel is closed after the last publish.

```{cell-insert}
:id: insert-batch
:path: {{ notebook }}
:tags: [batch]
:run: true
with wrapture.timeline() as tape:
    pipeline.run(["job-1", "job-2"])
    channel.publish.events.with_args(body="job-1").assert_once()
    channel.publish.events.with_args(routing_key="jobs").assert_times(2)
    tape.assert_order(transport.open_channel, channel.publish, channel.publish, channel.close)
    batch = len(tape.all)

print(tape.tree())
batch
```

`with_args(routing_key="jobs")` matched both publishes even though the
pipeline never spelled the default out: matching is against the
signature-normalised call. The tape's six events are the four
transport calls plus the two hook calls, everything the test's
stand-ins saw, in one recording. `assert_order` steps accept stub and
mock methods directly, alongside bindings and filtered logs; without
flags it is a subsequence check, and `consecutive=True` or
`exact=True` tighten it when the test means "nothing between" or
"nothing else at all".

```{verify}
:id: batch-ordered
:label: The batch recorded six events in the expected order
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-batch; cell-executed batch
batch == 6 and tape.tree().startswith("Transport.open_channel()") and tape.tree().rstrip().endswith("Channel.close()  -> None")
```
