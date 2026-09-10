---
title: Naming the phases
requires: [verify:phase-scoped]
---

# Naming the phases

An integration test that performs several acts otherwise leaves one
flat tape, and "the events during the second order" means parent
chasing. `wrapture.block(name)` is a context manager that records the
enclosed stretch of code as one event of kind `"block"`, and
everything recorded inside nests under it. `tape.blocks(name)` selects
block events by name, and `tape.within(event)` scopes the whole query
surface to one block's contents.

```{cell-insert}
:id: insert-phases
:path: {{ notebook }}
:tags: [phases]
:run: true
with wrapture.timeline(place, charge, record) as tape:
    with wrapture.block("paid order"):
        service.place(500, "4111-1111-1111-1111", tenant="acme")
    with wrapture.block("declined order"):
        service.place(250, "4000-0000-0000-0000", tenant="globex")

    declined = tape.blocks("declined order").assert_once().first
    inside = tape.within(declined)
    inside.for_binding(record).assert_never()
    inside.for_binding(charge).assert_once()
    phases = [event.path for event in inside.all]
    root_is_block = inside.root is declined

print(tape.tree())
phases, root_is_block
```

The view `within()` returns is tape-like and live: `all`,
`for_binding()`, `blocks()`, `roots()`, `tree()` and `assert_order()`
all work scoped to the block's descendants, so an ordering assertion
on the view never sees an event outside it. The block is not a member
of its own view; the view exposes it as `root`. And the tree gains
narrative structure for free, one `block:` line per phase.

```{verify}
:id: phase-scoped
:label: The declined order's phase holds a charge and no ledger write
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-phases; cell-executed phases
phases == ["shop:OrderService.place", "shop:Gateway.charge"] and root_is_block
```

```{hint}
:title: If the check fails
The two orders must be placed inside two differently named blocks,
and the assertions must read the view of the `"declined order"`
block. `phases` lists the paths of the events inside it, in recorded
order.
```
