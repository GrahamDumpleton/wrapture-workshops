---
title: Finish
requires: [quiz:misspelled-method]
---

# Finish

One opt-out from wrapping, and it stayed strict:

- `stub()` supplies one callable, permissive by choice, recording
  whatever arrives; `mimics=` borrows a real signature and kind so
  the stub checks each call and records by name.

- `mock(Spec)` supplies one collaborator with exactly the spec's
  surface: a misspelled method is an `AttributeError`, a drifted call
  a `TypeError`, and an unconfigured method returns `None` rather than
  inventing a chain.

- Both record on the same tape as any binding, so `with_args()`,
  `assert_times()` and `assert_order()` work across stubs, doubles and
  real code in one recording.

- `returns()` and `raises()` on a double's method reconfigure it in
  place, and two doubles of one class keep their events apart.

```{quiz}
:id: misspelled-method
:title: What a double does with a name it does not know
question: "The pipeline is changed to call transport.open_channnel(), with three n's. What happens when a test runs it with wrapture.mock(Transport)?"
options:
  - { text: "AttributeError at the call site inside the pipeline, naming the attribute the spec does not have", correct: true }
  - { text: "The call is recorded under the new name and returns None", explanation: "A mock fabricates nothing beyond its spec. Only the methods Transport really has exist on the double, so there is nothing to record the call under." }
  - { text: "TypeError, because the signature does not match", explanation: "Signature checks apply to calls of methods the spec has. A name the spec lacks fails earlier, on the attribute lookup." }
  - { text: "Nothing until the test asserts on transport.open_channel, which then reports zero calls", explanation: "That is the unittest.mock outcome, where the misspelled attribute is invented on first touch. Here the pipeline fails on the lookup itself." }
explanation: Accessing a name the spec does not have raises AttributeError wherever it happens, in the test and in the code under test alike. That is the fence that makes the double verify something.
```

The Finish button below says where to go next.
