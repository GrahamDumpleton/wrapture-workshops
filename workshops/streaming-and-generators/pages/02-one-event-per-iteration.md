---
title: One event per iteration
requires: [verify:iteration-recorded]
---

# One event per iteration

Bind the generator method and record inside a timeline. Calling a
generator function records one event covering the whole iteration,
not one per page, and the event's `items` field counts what was
pulled through it. When the consumer reads to the end, `result` holds
the generator's return value, `None` here.

```{cell-insert}
:id: insert-finished
:path: {{ notebook }}
:tags: [finished]
:run: true
pages = wrapture.binding(Catalogue, "pages")

with wrapture.timeline(pages) as tape:
    collect_ids(catalogue.pages())
    finished = pages.events.first

print(tape.tree())
finished.items, finished.result
```

Stopping early looks different. `first_match` finds id 3 on the
second page and returns, so the generator is dropped before it is
exhausted. The event closes with the item count reached and no result
at all: `wrapture.MISSING` rather than `None`, and no arrow in the
tree, which is the honest signal that the iteration never finished.

```{cell-insert}
:id: insert-abandoned
:path: {{ notebook }}
:tags: [abandoned]
:run: true
with wrapture.timeline(pages) as tape:
    first_match(catalogue.pages(), lambda item: item["id"] == 3)
    abandoned = pages.events.first

print(tape.tree())
abandoned.items, abandoned.result is wrapture.MISSING
```

That already answers how far the consumer read and whether it
finished, without touching the consumer. This treatment keys on the
bound call returning a real generator, which `pages()` does; a method
returning any other kind of iterator records it as an ordinary result
with no item count.

```{verify}
:id: iteration-recorded
:label: Three pages and a result for the full read, two pages and no result for the early stop
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-abandoned; cell-executed abandoned
finished.items == 3 and finished.result is None and abandoned.items == 2 and abandoned.result is wrapture.MISSING
```
