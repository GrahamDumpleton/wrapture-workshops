---
title: Finish
requires: [quiz:lifecycle]
---

# Finish

You have taken one binding through its lifecycle:

- `binding(Gateway, "charge")` names a location and patches nothing.

- `on_call.returns()`, `raises()` and `transforms_result()` configure
  behaviour, and still patch nothing.

- `apply()` installs the patch, `suspend()` and `resume()` switch it
  off and on in place, and `remove()` restores the original.

- A binding is a context manager, so a `with` block applies it on
  entry and removes it on exit.

- The real method can keep running while one thing about the call is
  changed.

Every other use of wrapture, recording calls in tests, tracing a
running program, exporting to a tracing backend, is built on this one
object and this lifecycle.

```{quiz}
:id: lifecycle
:title: The lifecycle
question: "After charge = wrapture.binding(Gateway, 'charge') and charge.on_call.returns({'id': 'stub'}), what does Gateway().charge(500) return?"
options:
  - { text: "The real result, because nothing is applied yet", correct: true }
  - { text: "The stub, because behaviour was configured", explanation: "Configuring behaviour never patches. The stub answers only after apply(), or inside a with block." }
  - { text: "An error, because the binding is not active", explanation: "An unapplied binding does nothing at all; the real method answers as if the binding did not exist." }
explanation: Creating and configuring a binding leave the target untouched. Only apply(), a with block or a recording scope installs the patch.
```

The Finish button below says where to go next.
