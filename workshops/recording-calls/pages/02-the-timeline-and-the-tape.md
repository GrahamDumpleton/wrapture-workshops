---
title: The timeline and the tape
requires: [verify:tape-recorded]
---

# The timeline and the tape

Bind `connect` on `Database` and `close` on `Connection`, and record
both onto one tape. Neither binding has any behaviour configured, so
they observe and nothing else.

```{cell-insert}
:id: insert-tape
:path: {{ notebook }}
:tags: [tape]
:run: true
connect = wrapture.binding(Database, "connect")
close = wrapture.binding(Connection, "close")

with wrapture.timeline(connect, close) as tape:
    report(Repository(Database()), [1, 2])

print(tape.tree())
```

Three acquisitions, two releases, and reading down the tape you can
already see which one has no partner.

The two words are two views of one thing. The timeline is the scope:
`with wrapture.timeline(...)` opens it, the bindings handed to it are
applied on entry and removed on exit, and while it is open every call
through every applied binding records an event. The tape is what the
scope holds.

Notice that `close` is bound on the `Connection` class, not on any
connection object. The connections do not exist when the block starts;
`connect()` mints them mid-call. A binding on the class wraps the
method for every instance, present and future, which is exactly what
covers objects a factory hands out. A mock injected through a seam
cannot see those objects at all.

```{verify}
:id: tape-recorded
:label: The tape holds five events
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-tape; cell-executed tape
len(tape.all) == 5
```

```{hint}
:title: Bindings applied some other way
A binding applied by a fixture or an outer `with` records onto an open
tape as well, and a binding applied with no timeline open records
nothing and costs almost nothing beyond the wrapper's own dispatch.
Leaving bindings applied and only occasionally recording is a
supported pattern, not a mistake.
```
