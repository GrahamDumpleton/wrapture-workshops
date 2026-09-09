---
title: Generators
requires: [verify:iteration-seen]
---

# Generators

Code that streams is lazy by design, and what matters about it does
not show in a return value: how far the consumer pulled, and whether
it finished or dropped the source part way. A canned list can prove
neither, since a list is never lazy. Binding a generator function
records **one event for the whole iteration**, opened when the call
creates the generator and filled in as the consumer iterates, with
`items` counting the values pulled through it. `statuses()` reads
`history()` to the end.

```{cell-insert}
:id: insert-stream
:path: {{ notebook }}
:tags: [stream]
:run: true
orders = [Order(1, 10), Order(2, 20), Order(3, 30), Order(4, 40)]
orders[1].pay()
orders[1].ship()

stream = wrapture.binding("shop", "history")

with wrapture.timeline(stream) as tape:
    print(statuses(orders))
    finished = stream.events.first

print(tape.tree())
finished.items, finished.result
```

Four items, and at exhaustion `result` is the generator's return
value, None for a generator that only yields. `first_shipped()` stops
at the first shipped order and returns, dropping the generator before
it is exhausted.

```{cell-insert}
:id: insert-stopped
:path: {{ notebook }}
:tags: [stopped]
:run: true
with wrapture.timeline(stream) as tape:
    print(first_shipped(orders))
    stopped = stream.events.first

print(tape.tree())
stopped.items, stopped.result is wrapture.MISSING
```

Two items, no result at all: `wrapture.MISSING` rather than None, and
no arrow in the tree, which is the honest signal that the iteration
never finished. That answers how far the consumer read and whether it
finished without touching the consumer or capturing a single item.
Item values are deliberately left off the tape; a test that wants to
see or change each item says so with an iterator proxy, which is a
later workshop.

```{verify}
:id: iteration-seen
:label: One event per iteration, with the count and whether it finished
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-stopped; cell-executed stopped
finished.items == 4 and finished.result is None and stopped.items == 2 and stopped.result is wrapture.MISSING
```

```{hint}
:title: Generators only
This treatment keys on the bound call returning a real generator. A
method that returns some other kind of iterator, or a list, records an
ordinary result with no item count.
```
