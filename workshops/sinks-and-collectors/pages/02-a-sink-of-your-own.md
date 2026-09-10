---
title: A sink of your own
requires: [verify:failures-counted]
---

# A sink of your own

A sink subclasses `wrapture.Sink` and overrides the notifications it
cares about. Each event is heard at most twice: `on_enter` when it is
recorded, with its position on the tape already assigned and its
outcome fields still unset, then exactly one of `on_exit` or
`on_error` when the operation completes or raises. `flush()` is the
fourth method, for a sink that buffers.

The protocol is small enough that a special-purpose sink is a few
lines. This one counts the operations that raised, by path, and
declares that it needs no argument or result values at all.

```{file-write}
:id: write-failures
:path: failures.py
:open: true
import wrapture

from shop import Gateway, Ledger, OrderService
import orders


class Failures(wrapture.Sink):
    """Count the operations that raised, by path."""

    capture_args = "none"
    capture_result = "none"

    def __init__(self):
        self.by_path = {}

    def on_error(self, event):
        self.by_path[event.path] = self.by_path.get(event.path, 0) + 1


class Broken(wrapture.Sink):
    """A sink with a bug in it."""

    def on_enter(self, event):
        raise RuntimeError("sink bug")


wrapture.binding(OrderService, "place").apply()
wrapture.binding(Gateway, "charge").apply()
wrapture.binding(Ledger, "record").apply()

failures = wrapture.add_sink(Failures())
orders.run()
wrapture.remove_sink(failures)

for path, count in sorted(failures.by_path.items()):
    print(count, "raised in", path)

broken = wrapture.add_sink(Broken())
orders.run()
wrapture.remove_sink(broken)
print("notifications the broken sink failed:", broken.errors)
```

```{execute}
:id: run-failures
:session: shell
:wait: prompt
python failures.py
```

```
1 raised in shop:Gateway.charge
1 raised in shop:OrderService.place
.venv/lib/python3.14/site-packages/wrapture/sinks.py:266: SinkErrorWarning: sink <__main__.Broken object at 0x...> raised from a notification; the error was suppressed and the observed call is unaffected. Further failures of this sink are counted on its errors attribute without warning again.
  _note_sink_error(sink)
notifications the broken sink failed: 8
```

Two properties of delivery matter to a sink author. Notifications run
inline, on the thread that executed the observed operation, so they
should be quick; code a sink calls is never itself recorded, so a sink
can touch observed objects without recording recursively. And a sink
can never take the application down: an exception raised from a
notification is suppressed, counted on the sink's `errors`, and
reported with a `SinkErrorWarning` the first time only, so a sink
broken in a hot loop cannot flood the warnings. The eight operations
all ran and completed normally while `Broken` failed on every one.

The two `capture_` declarations say how much of each event's values
the sink needs, using the levels a binding's capture policy uses. The
effective level for an event is the highest any active sink declares,
so a sink that asks for nothing lets recording skip value capture
entirely when it is the only listener.

```{verify}
:id: failures-counted
:label: The sink counted one failure per path, and the broken sink was contained
:substrate: shell
:trigger: after:run-failures
out=$(.venv/bin/python failures.py 2>&1) && printf '%s\n' "$out" | grep -q '^1 raised in shop:Gateway.charge$' && printf '%s\n' "$out" | grep -q '^1 raised in shop:OrderService.place$' && printf '%s\n' "$out" | grep -q 'SinkErrorWarning' && printf '%s\n' "$out" | grep -q '^notifications the broken sink failed: 8$' && { echo "Two failures counted by path; the broken sink failed 8 notifications and warned once"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check runs `failures.py` and expects one failure counted for the
charge and one for the order that contained it, one `SinkErrorWarning`,
and eight failed notifications on the broken sink. What it printed is
the message above.
```
