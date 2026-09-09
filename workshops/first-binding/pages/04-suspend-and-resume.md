---
title: Suspend and resume
requires: [verify:binding-resumed]
---

# Suspend and resume

Sometimes you want a patch out of the way for a moment without taking
it down, for example while other code is calling the method. `suspend()`
makes the binding inert in place.

```{cell-insert}
:id: insert-suspend
:path: {{ notebook }}
:tags: [suspend]
:run: true
charge.suspend()
```

The repr says `active suspended configured`: the wrapper is still
installed and the behaviour is still there, but calls pass straight
through.

```{cell-insert}
:id: insert-call-suspended
:path: {{ notebook }}
:tags: [call-suspended]
:run: true
gateway.charge(500)
```

The real method answers again. `resume()` puts the behaviour back.

```{cell-insert}
:id: insert-resume
:path: {{ notebook }}
:tags: [resume]
:run: true
charge.resume()
```

```{cell-insert}
:id: insert-call-resumed
:path: {{ notebook }}
:tags: [call-resumed]
:run: true
gateway.charge(500)
```

```{verify}
:id: binding-resumed
:label: The binding is active again after resuming
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-call-resumed; cell-executed call-resumed
print(charge.applied and not charge.suspended and gateway.charge(500) == {"id": "stub"})
```

```{hint}
:title: Suspended versus removed
A suspended binding keeps its wrapper installed and lets calls pass
straight through, which is safe to do at any moment. Removing it, on
the next page, takes the wrapper out and restores the original
attribute.
```
