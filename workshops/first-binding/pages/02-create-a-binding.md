---
title: Create a binding
requires: [verify:binding-unapplied]
---

# Create a binding

A binding names one attribute of a class or module and holds the
behaviour to apply there. Creating one is just naming the location.
Add a cell that binds `charge` on `Gateway` and shows the binding.

```{cell-insert}
:id: insert-binding
:path: {{ notebook }}
:tags: [binding]
:run: true
charge = wrapture.binding(Gateway, "charge")
charge
```

The repr always tells you the binding's state. Right now it says
`unapplied`: creating a binding never patches anything.

Configuring behaviour does not patch anything either. Tell the binding
to answer every call with a stub.

```{cell-insert}
:id: insert-configure
:path: {{ notebook }}
:tags: [configure]
:run: true
charge.on_call.returns({"id": "stub"})
```

The behaviour object it hands back shows the binding as `unapplied
configured`: it now has something to do, and is still not installed.
The repr says only that much. Ask the binding what it is set up to do.

```{cell-insert}
:id: insert-explain
:path: {{ notebook }}
:tags: [explain]
:run: true
print(charge.explain())
```

`explain()` names the channel, `on_call`, and the one thing configured
on it. Call the real method to confirm that none of this has touched
`Gateway`.

```{cell-insert}
:id: insert-call-real
:path: {{ notebook }}
:tags: [call-real]
:run: true
gateway.charge(500)
```

The real method still answers, with a real charge id. The binding is
an ordinary object you hold; it does nothing to `Gateway` until you
ask it to.

```{verify}
:id: binding-unapplied
:label: The binding exists and nothing is patched yet
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-call-real; cell-executed call-real
print(charge.configured and not charge.applied and gateway.charge(500)["id"] == "ch_500")
```

```{hint}
:title: Why separate creating from applying
Because bindings can be declared once, at module scope in a test file
or a fixture, given behaviour, and shared, with each test applying and
removing them. Nothing happens until `apply()`, a `with` block or a
recording scope.
```
