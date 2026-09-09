---
title: Scope it to a block
requires: [verify:block-scoped]
---

# Scope it to a block

Applying and removing by hand is the long form. The common case is a
patch that lasts for one block of code, and a binding is a context
manager, so behaviour reads in one line. Here the binding makes the
call fail with a timeout, which is how a test reaches the code that
handles one.

```{cell-insert}
:id: insert-block
:path: {{ notebook }}
:tags: [block]
:run: true
try:
    with wrapture.binding(Gateway, "charge").on_call.raises(TimeoutError("down")):
        gateway.charge(500)
except TimeoutError as exc:
    outcome = f"raised {exc}"

outcome
```

Inside the block the call raised. Leaving the block removed the
binding, so the method is real again.

```{cell-insert}
:id: insert-after-block
:path: {{ notebook }}
:tags: [after-block]
:run: true
gateway.charge(500)
```

```{verify}
:id: block-scoped
:label: The failure was injected inside the block only
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-after-block; cell-executed after-block
print(outcome == "raised down" and gateway.charge(500)["id"] == "ch_500")
```
