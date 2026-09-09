---
title: Finish
requires: [quiz:wrap-or-replace]
---

# Finish

Four places where wrapping the real code changed what a test could
say:

- A stub is strict by default. A call the real method would reject is
  rejected by the stub too, so a drifted call fails in the test rather
  than in production.

- A binding on the class sees calls an object makes to itself. A mock
  behind the constructor seam cannot see `_take_payment()`, and
  patching it replaces it.

- The real method can run with one thing changed on the way in or the
  way out. The standard library has no spelling for that.

- On an error path the other collaborators stay real, so the test
  asserts on the real charge id, on what was never called, and on the
  order across bindings.

And one place where mock still fits: when the test itself must supply
the thing being called, wrapture's `stub()` and `mock(Spec)` are
strict and recorded, and what wrapture leaves out on purpose is a
spec-less `MagicMock` whose attributes exist on first touch.

```{quiz}
:id: wrap-or-replace
:title: Wrap or replace
question: "In test_error_path_with_wrapture, which of the four bound methods had their real code run?"
options:
  - { text: "charge and refund", correct: true }
  - { text: "charge, refund and send: everything except record", explanation: "send was never called at all, which is what send.events.assert_never() checks. The tape shows only three events." }
  - { text: "None of them; a binding replaces the method it names", explanation: "A binding with no behaviour configured wraps the real method and records it. Only record had raises() configured." }
  - { text: "charge, record and refund: the three on the tape", explanation: "record is on the tape because it was called, but raises() answered instead of the real method. The tree marks it as an injected failure." }
explanation: charge and refund had no behaviour and only observed, so their real code ran. record was called but raises() answered in its place, and send was never called, so the tape holds three events and only two real calls.
```

The Finish button below says where to go next.
