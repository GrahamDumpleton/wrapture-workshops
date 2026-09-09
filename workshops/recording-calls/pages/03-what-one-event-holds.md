---
title: What one event holds
requires: [verify:leak-found]
---

# What one event holds

Each call through a binding inside the scope records one event, and an
event is a good deal richer than a mock's call record. Look at the
first `connect` event.

```{cell-insert}
:id: insert-event
:path: {{ notebook }}
:tags: [event]
:run: true
with wrapture.timeline(connect, close):
    report(Repository(Database()), [1, 2])
    first = connect.events.first

first.path, first.arguments, first.result, first.seq, first.depth
```

`path` is the fully qualified location, `arguments` the call
normalised against the real signature with defaults applied, `result`
the real return value, or `exception` when the call raised, and `seq`,
`depth` and `parent_id` place the event in the call tree. There are
timings too.

A binding's `events` is a filterable view over the tape for that one
binding, and it is read inside the block, after the code under test
has run. Because the values are real, they can be compared across
events. A `connect` event's `result` is the connection it minted, and a
`close` event's `instance` is the connection it was called on, so the
leaked connections are the difference between the two sets.

```{cell-insert}
:id: insert-pair
:path: {{ notebook }}
:tags: [pair]
:run: true
with wrapture.timeline(connect, close):
    report(Repository(Database()), [1, 2])
    acquired = {event.result for event in connect.events}
    released = {event.instance for event in close.events}

leaked = acquired - released
leaked
```

That is the whole question answered, and it needed nothing from the
repository.

```{verify}
:id: leak-found
:label: The leaked connection is the second one
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-pair; cell-executed pair
[connection.number for connection in leaked] == [2]
```

```{hint}
:title: Reading events outside the block
`connect.events` outside a timeline raises: events are only recorded
inside a `timeline()`. Read what you need inside the block and keep
the result, as `leaked` does here, or keep the `tape` the block hands
you, whose `all` list stays readable afterwards.
```
