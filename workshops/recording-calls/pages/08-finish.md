---
title: Finish
requires: [quiz:class-binding]
---

# Finish

Everything here recorded real calls with the bindings doing nothing
but watch:

- The timeline is the scope and the tape is what it holds. Bindings
  handed to `timeline()` are applied on entry and removed on exit.

- An event carries the real path, instance, normalised arguments,
  result or exception, and its place in the call tree, so events can
  be compared with each other.

- `assert_` raises now, `expect_` is verified when the scope closes,
  and everything else returns data. Filters chain and never raise.

- The tree names the method that leaked and stack capture names the
  line. `assert_order()` checks the flow across bindings, and a nested
  timeline scopes the act step instead of resetting anything.

- The record became a test that failed until the code was fixed.

```{quiz}
:id: class-binding
:title: Where the binding goes
:shuffle: true
question: "Why is close bound on the Connection class rather than on a connection object?"
options:
  - { text: "The connections do not exist yet; a binding on the class covers every instance connect() mints later", correct: true }
  - { text: "Instances cannot be bound at all", explanation: "Callable bindings can be placed on an instance. It is the wrong place here because the objects that matter are created mid-call." }
  - { text: "So that the binding records the constructor as well", explanation: "The binding is on close(), not __init__. It records calls to close() on every instance." }
explanation: connect() mints the connections during the call, so nothing the test holds up front could be bound. Wrapping close() on the class wraps it for every instance, present and future.
```

The Finish button below says where to go next.
