---
title: Remove it
requires: [verify:binding-removed]
---

# Remove it

`remove()` takes the patch down and restores the original exactly.

```{cell-insert}
:id: insert-remove
:path: {{ notebook }}
:tags: [remove]
:run: true
charge.remove()
```

The repr is back to `unapplied`. Call the method once more.

```{cell-insert}
:id: insert-call-removed
:path: {{ notebook }}
:tags: [call-removed]
:run: true
gateway.charge(500)
```

The real method answers. The binding still exists and still holds its
behaviour, so it can be applied again later.

```{verify}
:id: binding-removed
:label: The real method is restored
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-call-removed; cell-executed call-removed
print(not charge.applied and gateway.charge(500) == {"id": "ch_500", "amount": 500})
```
