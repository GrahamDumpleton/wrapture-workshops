---
title: This call logged it
requires: [verify:warning-pinned]
---

# This call logged it

A log message the code under test emits is an observation like any
other, and `capture_logs()` records standard library logging onto the
tape as events of kind `"log"`. The capture applies like a binding,
so `timeline()` accepts it alongside them, and its `events` speak the
same vocabulary. Three log-shaped filters join the family:
`at_level()` means "at least this severe", `with_message()` is a
case-sensitive `fnmatch` pattern, and `without_message()` is its
negation.

```{cell-insert}
:id: insert-logs
:path: {{ notebook }}
:tags: [logs]
:run: true
charge = wrapture.binding(Gateway, "charge")
record = wrapture.binding(Ledger, "record")
place = wrapture.binding(OrderService, "place")
logs = wrapture.capture_logs("shop")

with wrapture.timeline(place, charge, record, logs) as tape:
    service.place(500, "4111-1111-1111-1111", tenant="acme")
    service.place(250, "4000-0000-0000-0000", tenant="globex")
    warning = logs.events.at_level("WARNING").with_message("*declined*").assert_once().first
    logs.events.at_level("ERROR").assert_never()
    logged_inside = tape.parent_of(warning) is charge.events.raising(CardDeclined).first
    tree = tape.tree()

print(tree)
warning.data["message"], logged_inside
```

The reason to reach for this over pytest's `caplog` is position. The
log event nests inside the call that emitted it, so the test pins the
warning to the declined charge rather than to "somewhere during the
test", and the tree shows the message in place, one line, under the
call. The captured fields ride in `event.data`: `level`, `message`,
`module`, `funcName` and `lineno`, with the logger name as the
event's `path`.

Capture sits at `logging.Logger.handle`, so it hears each record once,
on the logger that emitted it, before propagation and whatever the
handlers do. The warning still reached standard error; nothing the
application configured was touched. The default level is `WARNING`,
so capture volume is a deliberate choice rather than an ambient flood.

Two other things in this tree are the subject of later pages: the
`block: fulfil` line under the paid order, and the `!! CardDeclined`
on an order that returned normally.

```{verify}
:id: warning-pinned
:label: The warning was captured and sits inside the declined charge
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-logs; cell-executed logs
warning.data["message"] == "card ending 0000 declined" and logged_inside
```

```{hint}
:title: If the check fails
`logs` must be `capture_logs("shop")`, the logger name `shop.py`
uses, and it must be handed to `timeline()` with the bindings.
`logged_inside` compares the warning's parent with the charge event
that raised `CardDeclined`.
```
