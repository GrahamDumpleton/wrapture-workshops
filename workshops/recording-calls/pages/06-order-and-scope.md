---
title: Order and scope
requires: [verify:scoped]
---

# Order across bindings, and scope instead of resetting

Per-binding logs answer questions about one call site; the tape
answers questions about the flow between them. `tape.assert_order()`
is a subsequence check across any bindings: other events may appear
before, between and after, and only the relative order of the named
bindings' events matters, so a connect followed somewhere by a close
passes on this tape. `exact=True` says those bindings' events are
exactly the steps given, one connect and one close, which a leaking
run cannot satisfy. On failure the message says where the walk went
wrong and prints the actual timeline.

```{cell-insert}
:id: insert-order
:path: {{ notebook }}
:tags: [order]
:run: true
with wrapture.timeline(connect, close) as tape:
    report(Repository(Database()), [1, 2])
    tape.assert_order(connect, close)
    try:
        tape.assert_order(connect, close, exact=True)
    except AssertionError as exc:
        order_failure = str(exc)

print(order_failure)
```

A step can also be a filtered log, which is how to say which call:
`tape.assert_order(charge.events.raising(TimeoutError), refund)` reads
as "the refund came after the charge that timed out".
`consecutive=True` requires the steps to follow one another with none
of those bindings' events between.

A tape is never cleared. Where a mock suite reaches for `reset_mock()`
to discard setup calls before the act step, wrapture opens the timeline
around the part that counts. Timelines nest, and an inner `timeline()`
with no arguments records only what happens inside it while the outer
one keeps the whole run.

```{cell-insert}
:id: insert-nested
:path: {{ notebook }}
:tags: [nested]
:run: true
with wrapture.timeline(connect, close) as whole:
    repository = Repository(Database())
    repository.count("products")

    with wrapture.timeline() as act:
        repository.find("products", 1)
        connect.events.assert_once()
        inner = len(act.all)

len(whole.all), inner
```

Inside the inner block `connect.events` reads the innermost tape, so
the assertion sees one connect even though the outer tape holds four
events. The same scoping is how a phased test keeps each phase's
counts apart: one timeline per phase, the same bindings applied on
entry and removed on exit each time.

```{verify}
:id: scoped
:label: The exact order failed as expected and the inner timeline saw the act step alone
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-nested; cell-executed nested
"actual timeline" in order_failure and inner == 2 and len(whole.all) == 4
```
