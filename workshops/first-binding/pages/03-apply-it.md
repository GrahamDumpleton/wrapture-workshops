---
title: Apply it
requires: [verify:binding-applied]
---

# Apply it

`apply()` installs the patch. From then on the configured behaviour
answers instead of the real method.

```{cell-insert}
:id: insert-apply
:path: {{ notebook }}
:tags: [apply]
:run: true
charge.apply()
```

The repr now says `active configured`. Call the method again.

```{cell-insert}
:id: insert-call-stub
:path: {{ notebook }}
:tags: [call-stub]
:run: true
gateway.charge(500)
```

The stub answers, for the same `gateway` object you made before the
binding existed. The binding is on the class, so every instance,
present and future, goes through it.

```{verify}
:id: binding-applied
:label: The stub answers the call
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-call-stub; cell-executed call-stub
print(charge.applied and gateway.charge(500) == {"id": "stub"})
```
