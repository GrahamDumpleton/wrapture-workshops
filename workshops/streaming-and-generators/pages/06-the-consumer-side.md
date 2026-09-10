---
title: The consumer side
requires: [verify:consumer-proxied]
---

# The consumer side

So far the proxy has been attached where the generator is produced.
It can equally be attached where one is consumed: `transforms_args()`
on the consumer's binding rewrites the incoming arguments, and the
factory wraps the generator among them. This is the form for when the
producer is not something you can or want to bind, a generator built
inline, or one arriving from outside the code under test, and it
works without touching `Catalogue` at all. Clear the producer's
behaviour first so the two proxies do not stack.

```{cell-insert}
:id: insert-consumer
:path: {{ notebook }}
:tags: [consumer]
:run: true
pages.on_call.passes_through()

cursors.clear()
outcomes.clear()

write = wrapture.binding(Exporter, "write")
write.on_call.transforms_args(lambda args, kwargs: ((watch(args[0]), *args[1:]), kwargs))

with wrapture.timeline(write):
    exported = Exporter().write(catalogue.pages(), [])
    write_event = write.events.first

cursors, outcomes, exported, write_event.items
```

Recording is different on this side. The event for `Exporter.write`
records the call and its result of 5 as usual, but gains no item
count: the item lifecycle belongs to the generator's own event, which
exists only when the producer is bound too. Bind both when you want
both.

```{verify}
:id: consumer-proxied
:label: The proxy on the argument saw every page, and the consumer's event has no item count
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-consumer; cell-executed consumer
cursors == [0, 2, 4] and outcomes == [("finished", None)] and exported == 5 and not write_event.items
```
