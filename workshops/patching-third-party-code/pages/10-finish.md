---
title: Finish
requires: [quiz:deferred-refused]
---

# Finish

The library was never edited, and every change to it had a lifecycle:

- `transforms_args()` rewrote the call on the way in, and the real
  method still ran. `apply()` installed it, `suspend()` and
  `resume()` switched it off and on with the skipped calls counted,
  and `remove()` restored the original exactly.

- The pipeline was reconfigured while installed with
  `passes_through()`, and `decorates()` put a retry at its centre
  with the transform still around it.

- An attribute binding clamped a value the library reads, through
  instances, for the extent of a block.

- `when_imported()` ran the binding code the moment the module was
  imported, and a config file did the same from outside the
  application, with an unknown setting refused at load.

- A capture policy recorded the calls with the token redacted, on the
  same binding that can carry the behaviour.

```{quiz}
:id: deferred-refused
:title: Deferred targets
question: "Why does wrapture refuse the deferred target vendored_client? but accept a binding created inside a when_imported hook?"
options:
  - { text: "A deferred wrap registers a hook and returns no handle, so there would be nothing to suspend, remove or report on; the hook runs your code with the module, so the binding exists and holds its wrapper", correct: true }
  - { text: "The deferred form only works for module-level functions, not methods", explanation: "wrapt's deferred form handles methods too. The refusal is about the missing handle, not the kind of target." }
  - { text: "The hook imports the module early so the binding can resolve it", explanation: "The hook waits for the module to be imported by whoever imports it first, and runs at that moment. It never triggers the import itself." }
  - { text: "Deferred patching would apply the patch twice if the module were reloaded", explanation: "Reloading is not the concern. A binding needs the wrapper it applied in order to manage it, and a deferred wrap never hands one back." }
explanation: A binding is a patch with a lifecycle, and the lifecycle needs the wrapper. The deferred form gives none back, so it is refused with a message that points at when_imported, where the binding is created after the import it depends on, by construction.
```

The Finish button below says where to go next.
