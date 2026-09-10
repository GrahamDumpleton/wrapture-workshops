---
title: A block in the code
requires: [verify:fulfil-declared]
---

# A block in the code

The other use of a block lives in the application. Once the code
declares "this is the fulfilment phase", a test asserts on the phase
instead of reverse-engineering it from call patterns. `shop.py` wraps
the ledger write and the notification in `block("fulfil",
data={"tenant": tenant})`, so the block event carries the tenant as
seed data from the moment it is declared. Like a log statement, the
marker is embedded by the author and inert when nothing listens, so
it can stay in production code.

```{cell-insert}
:id: insert-fulfil
:path: {{ notebook }}
:tags: [fulfil]
:run: true
with wrapture.timeline(place, charge, record) as tape:
    service.place(500, "4111-1111-1111-1111", tenant="acme")

    fulfil = tape.blocks("fulfil").assert_once().first
    under_place = tape.parent_of(fulfil) is place.events.first
    tape.within(fulfil).for_binding(record).assert_once()
    tape.within(fulfil).for_binding(charge).assert_never()

fulfil.kind, fulfil.data, under_place
```

The block sits under the `place` call that opened it, the ledger
write is inside it and the charge is not, exactly as the code says.
The `data` mapping already holds two keys: `tenant`, seeded at the
declaration, and `entry`, which the next page explains.

There is deliberately no decorator form of `block()`. The
whole-function case already has an answer: bind the function, or
decorate it with `@observed`, and it records a call event, which is
what a whole function is. `block()` marks what is smaller than a
function, the stretches inside one that no callable boundary covers.

```{verify}
:id: fulfil-declared
:label: The fulfil block sits under the order and holds the ledger write
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-fulfil; cell-executed fulfil
fulfil.kind == "block" and fulfil.data["tenant"] == "acme" and under_place
```

```{hint}
:title: If the check fails
`tape.blocks("fulfil")` finds the block `shop.py` declares; if it
finds nothing, the order was placed outside the timeline. The block's
`data` carries the tenant seeded at the declaration.
```
