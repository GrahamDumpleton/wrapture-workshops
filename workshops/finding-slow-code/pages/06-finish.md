---
title: Finish
requires: [quiz:self-versus-total]
---

# Finish

The stopwatch never went in. The trace already had the times, and the
parent links turned them into an answer:

- Every closing line carries the operation's duration, and reading a
  request's tree from the bottom up says which layers only wait for
  the ones beneath them.

- Self time is the duration minus the observed children's time, the
  figure a profiler ranks by, and `tape.self_time()` asserts on it in
  a test with the Flask instrumentation applied to the block.

- `Aggregate` in a `[[window]]` gives one table for a whole run of the
  server, sorted by self time, with nothing retained.

- `annotate()` in a `before_request` hook, aimed at the request with
  `current_event(kind="request")`, tags every request with its tenant,
  and the tag rides on the event into the file, the live view and a
  test.

```{quiz}
:id: self-versus-total
:title: Slow itself, or slow because of a child
question: "In the aggregate report, webshop:order had a total of 369.8ms over twenty calls and a self time of 5.7ms. What does that say about the view?"
options:
  - { text: "The view is slow only because of what it calls; its own work is a few hundred microseconds per call", correct: true }
  - { text: "The view is slow in its own right and the layers beneath it are fast", explanation: "That would show as a large self time on the view. Self time is what is left after the observed children's time is taken out, and almost nothing was left." }
  - { text: "The report double-counted the ledger's time under the view", explanation: "Totals do include children's time, which is why a parent's total is at least its children's. Self time is the column that removes the overlap, and it is what the table is sorted by." }
  - { text: "The view was measured on twenty different requests, so the numbers cannot be compared", explanation: "The row is one bound location across twenty operations. The min and max columns show the spread, and the self time is summed across them the same way the total is." }
explanation: A large total with a small self time means the operation's time belongs to its children. The ledger's row has the same total and self time, because nothing observed runs beneath it, and it is where the time actually went.
```

The Finish button below says where to go next.
