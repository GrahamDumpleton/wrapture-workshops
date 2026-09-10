---
title: Finish
requires: [quiz:fixture-handle]
---

# Finish

One owner per binding, and a plugin for when that rule is broken:

- The with-block for a patch one test needs, `bound()` with `taped()`
  for a test that binds its targets around its whole body, with the
  bindings injected by name and expectations verified on removal.

- A yield fixture that hands the binding over, so the test
  reconfigures it in flight and never touches its lifecycle; a shared
  declaration applied per test, with `reset()` when the last test's
  behaviour should not carry over.

- The plugin's sweep fails a leaking test by name and removes the
  binding so the tests after it are unaffected; its `tape` fixture
  puts the call tree under a failure report; and its assertion output
  prints an event log's events, with what a filter discarded.

- A `Counter` on the database layer, applied once for the session,
  gives every test a query budget at almost no cost.

```{quiz}
:id: fixture-handle
:title: What a test may do with a fixture's binding
:shuffle: true
question: "A yield fixture applies a binding and yields it. Which of these may a test that receives it do?"
options:
  - { text: "Reconfigure it through on_call, as often as it likes", correct: true }
  - { text: "Enter it as a context manager, to scope part of the test", explanation: "The fixture already applied it, so entering it again raises AlreadyAppliedError. A narrower scope needs a binding of the test's own." }
  - { text: "Call remove() at the end, to be safe", explanation: "Removal belongs to the fixture, after the yield. A test that removes a fixture's binding is mixing scoping styles; it happens to be harmless here only because remove() is idempotent." }
  - { text: "Call apply() again after a remove(), to reuse it", explanation: "Neither call is the test's to make. Pick one owner for each binding's lifecycle; the test only changes behaviour." }
explanation: Whoever owns a binding, the test only reconfigures it through the handle it was given. The fixture applies before the yield and removes after it, whatever the test did in between.
```

The Finish button below says where to go next.
