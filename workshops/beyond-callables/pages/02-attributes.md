---
title: Attributes
requires: [verify:status-guarded]
---

# Attributes

A binding names a location, and what it does depends on what it finds
there. A function or method gives a callable binding with `on_call`. A
plain class attribute, a property or a slot gives an attribute binding
with three namespaces instead, `on_get`, `on_set` and `on_delete`, one
per operation, each with the vocabulary you know from `on_call`. Bind
`Order.status` and record an order being paid and described.

```{cell-insert}
:id: insert-record
:path: {{ notebook }}
:tags: [record]
:run: true
status = wrapture.binding(Order, "status")
print(status)

with wrapture.timeline(status) as tape:
    order = Order(2, 50)
    order.pay()
    describe(order)
    kinds = [event.kind for event in tape.all]

print(tape.tree())
kinds
```

The repr says `attribute`, detected from the class default it found.
The tape has one event per operation: the write `pay()` made, and the
two reads in `describe()`. Nothing was patched on the instance; the
binding installed a descriptor on the class while applied, and the
write landed in the instance dictionary as it always does.

`on_get.returns()` is what mock's `PropertyMock` is for: a test of the
shipped branch of `describe()` need not walk an order through paying
and shipping to get one.

```{cell-insert}
:id: insert-fake
:path: {{ notebook }}
:tags: [fake]
:run: true
shipped = wrapture.binding(Order, "status")
shipped.on_get.returns("shipped")

with shipped:
    faked = describe(Order(3, 10))

print(faked)
print(shipped.explain())
Order(3, 10).status
```

The interesting one is `on_set`, since a write is where an invariant
gets broken. `on_set.validates(check)` sees the value alone; a
transition guard needs the current state too, and `on_set.decorates()`
hands it the write to perform, the instance and the value. The guard
below allows only the forward moves and rejects the rest.

```{cell-insert}
:id: insert-guard
:path: {{ notebook }}
:tags: [guard]
:run: true
ALLOWED = {"new": {"paid"}, "paid": {"shipped"}, "shipped": set()}


def guarded(write, instance, value):
    current = instance.status
    if value not in ALLOWED[current]:
        raise ValueError(f"cannot go from {current} to {value}")
    write(value)


guard = wrapture.binding(Order, "status")
guard.on_set.decorates(guarded)

with wrapture.timeline(guard) as tape:
    order = Order(4, 10)
    order.pay()
    try:
        order.pay()
    except ValueError as exc:
        rejected = str(exc)
    order.ship()

print(rejected)
print(tape.tree())
order.status
```

Paying twice was refused and the order still reached shipped. Look at
the tree: each write has a read nested under it, because the guard's
own `instance.status` went through the binding too, and the tape
records the nesting rather than hiding it.

```{verify}
:id: status-guarded
:label: Reads and writes were recorded, the read was faked, and the second payment was refused
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-guard; cell-executed guard
kinds == ["set", "get", "get"] and faked == "order 3 is on its way" and rejected == "cannot go from paid to paid" and order.status == "shipped"
```

```{hint}
:title: Attributes that only exist on instances
`status` here is a class default, which is what the binding wrapped.
An attribute assigned only in `__init__` has nothing on the class to
wrap; `binding(Order, "status", missing_ok=True)` covers it, and the
write in `__init__` then passes through `on_set` like any other. The
target must be a class or a module: a binding cannot intercept the
attribute of one instance, since the descriptor goes on the class.
```
