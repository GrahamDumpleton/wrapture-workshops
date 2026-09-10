---
title: Finish
requires: [quiz:completion-order]
---

# Finish

The trace outlived the process:

- A `jsonlines` sink in the config streamed one object per completed
  event, from both worker threads, never blocking the program.

- `python -m wrapture.tools convert` rendered the file as Chrome
  trace JSON for Perfetto, one lane per thread, and as a canonical
  tree.

- The canonical tree, saved as a golden file, made a test that fails
  on a refactor which changes what calls what, with a diff.

- A path template and `rotate=` turned one file into a series, with
  the directories created and the last file flushed at exit.

```{quiz}
:id: completion-order
:title: The order of the lines
question: "In trace.jsonl a store line appears before the process line that contains it. Why?"
options:
  - { text: "A line is written when an event closes, and the inner call closes first; seq and parent_id rebuild the tree", correct: true }
  - { text: "The writer thread reorders lines to keep the file small", explanation: "The writer drains a queue in the order lines were queued. The order is completion order because that is when a line is queued." }
  - { text: "Roots are written last so a reader can tell the trace is complete", explanation: "Nothing is held back. Each event is written as it closes, and a root closes after everything beneath it." }
  - { text: "Each thread writes its own section of the file", explanation: "Lines from both threads interleave in one file, in completion order, with thread_name on each line." }
explanation: Every line carries the outcome and the timing, which are only known when the event closes, so children come before the operation that contains them. Sorting by seq with nesting rebuilt from parent_id recovers the tree, which is what the converters do.
```

The Finish button below says where to go next.
