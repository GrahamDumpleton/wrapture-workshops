---
title: Finish
requires: [quiz:no-translation]
---

# Finish

The suite never went red, and each idiom found its spelling:

- `return_value` and `side_effect` as an exception are `returns()` and
  `raises()`, strict by default, with the rest of the pipeline left
  real.

- A `side_effect` list is phases: values from `returns_from()`,
  `then(after=n)` or `then(until=fn)` for the next regime, and
  `raising()` on the events to say which calls failed.

- `patch.multiple` is a `bindings()` group, mixing stubbed, failing
  and merely observed members, applied all or nothing.

- `patch.dict` and `setenv` are a value binding, with-block or
  decorator; `wraps` is a binding with no behaviour, or one that
  changes one thing about the real call.

- `assert_has_calls` is `assert_order(..., consecutive=True)` on the
  tape, across any bindings; `caplog` is `capture_logs()`, with the
  message's position in the tree.

- A bare `Mock()` stays a bare `Mock()` until there is a class to name.

```{quiz}
:id: no-translation
:title: What has no translation
question: "Which of these mock idioms has no wrapture equivalent, by design?"
options:
  - { text: "A bare Mock() handed to the code under test as a collaborator", correct: true }
  - { text: "side_effect as a list of outcomes", explanation: "That is returns_from() and then(): more lines, but each phase says what it is, and a phase can end on a condition as well as a count." }
  - { text: "patch.dict on os.environ", explanation: "That is a value binding on os.environ with item=, as a with-block or a bound() decorator, restored on exit like patch.dict." }
  - { text: "assert_has_calls across two different mocks", explanation: "That is assert_order() on the tape, which takes any bindings and filtered logs, with consecutive=True for the contiguous check." }
explanation: A mock in wrapture requires a spec and fabricates nothing beyond it. The spec-less double, whose attributes exist on first touch, is the one thing left to unittest.mock, because an object that answers everything verifies nothing.
```

The Finish button below says where to go next.
