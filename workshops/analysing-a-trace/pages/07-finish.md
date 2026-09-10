---
title: Finish
requires: [quiz:self-time-quiz]
---

# Finish

Nothing on these pages needed wrapture beyond reading the file back.
The trace is data, and the questions were data questions:

- `load_events()` returns the records in recording order, and a
  DataFrame holds them with absent fields kept as missing values.

- `parent_id` rebuilds the tree, and self time is a groupby: the
  children's durations summed by parent, subtracted from the parent's
  own. `place` is slow only because of the ledger.

- Errors count by path, and the same failure shows where it was raised
  and where it escaped.

- The latency of an order is a distribution, and the tenant captured
  on each `place` names the slow tail.

- `mermaid()` and `canonical()` take the records as they take a tape,
  and one order's tree is the events sharing its trace id.

```{quiz}
:id: self-time-quiz
:title: Reading self time
:shuffle: true
question: "In the summary, place had the largest total time and the smallest self time. What does that combination say?"
options:
  - { text: "place is slow because of what it calls; the time is in the ledger and the gateway beneath it", correct: true }
  - { text: "place is slow in its own right, and the ledger and gateway are fast", explanation: "That would show as a large self time on place. Self time is the duration with the observed children's time taken out, and place had almost none left." }
  - { text: "The durations were recorded on different clocks and cannot be compared", explanation: "Every event is timed on the same clock, and the parent links are what make the subtraction meaningful. The figures on one tree add up." }
  - { text: "The file was written in completion order, so the children were counted twice", explanation: "Completion order is why the lines needed sorting by seq, and load_events() did that. The subtraction uses each row once, by its parent link." }
explanation: Self time is the figure a profiler ranks by, and the one a wall-clock timer around the service call cannot express. A large total with a small self time means the operation's time belongs to its children.
```

The Finish button below says where to go next.
