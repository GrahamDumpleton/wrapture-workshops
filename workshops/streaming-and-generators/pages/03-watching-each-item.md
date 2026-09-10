---
title: Watching each item
requires: [verify:items-watched]
---

# Watching each item

Item values are deliberately not captured on the tape: a long stream
would retain every item, and no policy can guess which matter. When a
test wants to know which pages went by, or to react to each one, it
says so with an iterator proxy. `iterator()` creates a factory with
no target; behaviour is configured on its namespaces, and calling the
factory with a generator returns a wrapped generator applying that
behaviour. `on_item.validates_item()` runs a check per item and passes
the item through unchanged, `on_finish.validates()` runs at normal
exhaustion with the generator's return value, and
`on_abandon.notifies()` runs when a started, unexhausted generator is
closed, explicitly or by garbage collection.

Since the factory is a callable that takes an iterator and returns
one, it slots straight into the binding's `transforms_result()`: every
generator `pages()` returns is wrapped on the way out. Behaviour
applies whenever the binding is applied, timeline or not, so
`with pages:` is enough here.

```{cell-insert}
:id: insert-watch
:path: {{ notebook }}
:tags: [watch]
:run: true
cursors = []
outcomes = []

watch = wrapture.iterator()
watch.on_item.validates_item(lambda page: cursors.append(page["cursor"]))
watch.on_finish.validates(lambda value: outcomes.append(("finished", value)))
watch.on_abandon.notifies(lambda: outcomes.append(("abandoned", None)))

pages.on_call.transforms_result(watch)

with pages:
    collect_ids(catalogue.pages())

cursors, outcomes
```

Now the early-stopping consumer through the same proxy, inside a
timeline this time. The two layers compose: the consumer drives the
recording relay, which drives the proxy, which drives the real
generator, so the event's `items` and the proxy's `cursors` agree.
The difference from `collect_ids` shows up as data: two pages seen,
then an abandonment, because `first_match` dropped the generator and
Python closed it on the spot. An item stage can also call
`wrapture.annotate()` to pin what it knows onto the very event being
recorded.

```{cell-insert}
:id: insert-annotate
:path: {{ notebook }}
:tags: [annotate]
:run: true
def note_cursor(page):
    wrapture.annotate(last_cursor=page["cursor"])

watch.on_item.validates_item(note_cursor)

cursors.clear()
outcomes.clear()

with wrapture.timeline(pages):
    first_match(catalogue.pages(), lambda item: item["id"] == 3)
    noted = pages.events.first

cursors, outcomes, noted.items, noted.data
```

Reconfiguring the factory affects only generators wrapped afterwards,
so a proxy can be adjusted between calls without re-binding.

```{verify}
:id: items-watched
:label: The proxy saw two pages, heard the abandonment, and pinned the last cursor on the event
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-annotate; cell-executed annotate
cursors == [0, 2] and outcomes == [("abandoned", None)] and noted.items == 2 and noted.data == {"last_cursor": 2} and noted.result is wrapture.MISSING
```

```{hint}
:title: If the check fails after running the cells twice
The first cell above appends to `cursors` and `outcomes` and the
second clears them, so run the two in order. The check wants the
state the second cell leaves: two cursors and one abandonment.
```
