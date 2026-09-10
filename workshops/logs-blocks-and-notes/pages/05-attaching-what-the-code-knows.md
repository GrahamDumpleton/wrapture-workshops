---
title: Attaching what the code knows
requires: [verify:annotations-found]
---

# Attaching what the code knows

A capture policy is a blanket setting. Annotation is targeted:
`annotate(**data)` merges into the in-flight event's `data`, from
anywhere in observed code or from inside a `decorates()` handler.
The innermost event in flight is the one it lands on, which inside
the fulfil block is the block, and that is where the `entry` key on
the previous page came from: `shop.py` calls
`wrapture.annotate(entry=entry)` right after the ledger write.

The test side can annotate too. A handler around `Gateway.charge`
tags each charge with an amount band, which a filter then reads.

```{cell-insert}
:id: insert-annotate
:path: {{ notebook }}
:tags: [annotate]
:run: true
def banded(wrapped, instance, args, kwargs):
    amount = args[0] if args else kwargs["amount"]
    wrapture.annotate(band="large" if amount >= 300 else "small")
    return wrapped(*args, **kwargs)


charge.on_call.decorates(banded)

with wrapture.timeline(place, charge, record) as tape:
    service.place(500, "4111-1111-1111-1111", tenant="acme")
    service.place(120, "5555-4444-3333-2222", tenant="globex")

    large = charge.events.matching(lambda event: event.data.get("band") == "large").assert_once().first
    entries = [event.data["entry"] for event in tape.blocks("fulfil")]

charge.on_call.reset()
large.arguments["amount"], entries
```

Two charges, one tagged `large`, and two fulfil blocks each carrying
the ledger entry the code attached. Outside recording, `annotate()`
is a silent no-op, so observed code calls it unconditionally, as
`shop.py` does. When the event to annotate is further out than the
innermost one, `current_event()` takes filters: `kind="request"`
selects the nearest enclosing request a middleware recorded, and
`binding=` the nearest event a given binding recorded, and the handle
it returns is empty and inert when nothing matched.

```{verify}
:id: annotations-found
:label: The handler tagged the large charge and the code tagged both entries
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-annotate; cell-executed annotate
large.arguments["amount"] == 500 and entries == ["led_ch_500", "led_ch_120"]
```

```{hint}
:title: If the check fails
The `banded` handler must call `annotate()` before calling `wrapped`,
and must be installed with `charge.on_call.decorates(banded)` before
the timeline opens. `entries` reads the `entry` key `shop.py` attaches
to each fulfil block.
```
