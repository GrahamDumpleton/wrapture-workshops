---
title: Transforming items
requires: [verify:items-thinned]
---

# Transforming items

`on_item.transforms_item()` rewrites each item and hands the rewritten
one on. The real generator keeps running, so this changes only the
one thing the test cares about: here, shrinking every page to a
single item to check that the exporter counts rows and not pages.

```{cell-insert}
:id: insert-thin
:path: {{ notebook }}
:tags: [thin]
:run: true
thin = wrapture.iterator()
thin.on_item.transforms_item(lambda page: {**page, "items": page["items"][:1]})

pages.on_call.passes_through().transforms_result(thin)

with pages:
    rows = []
    thinned = Exporter().write(catalogue.pages(), rows)

thinned, rows
```

Three rows from three pages of one item each, and the catalogue still
served every page: the transform sits between the generator and its
consumer, not inside either.

```{verify}
:id: items-thinned
:label: Each page reached the exporter with one item
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-thin; cell-executed thin
thinned == 3 and rows == ["1,item-1", "3,item-3", "5,item-5"]
```
