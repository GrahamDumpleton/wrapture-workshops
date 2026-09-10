---
title: Finish
requires: [quiz:capture-negotiation]
---

# Finish

Events went where you sent them:

- A sink is three notifications and a flush. It runs inline, cannot
  take the application down, and declares how much of each event it
  needs.

- A timeline is a scoped sink and cannot hear a thread; a process
  sink hears everything. A bound method with nobody listening
  constructs no event.

- `Fanout`, `Filter`, `Depth` and `Sample` compose sinks, with
  sampling decided once per tree.

- `Counter` and `Aggregate` keep numbers and nothing else, and report
  from a window.

- `leaf=True` keeps an event and silences everything beneath it;
  `category=` says what kind of operation it is; resolvers decide
  the label, category and tags per operation.

```{quiz}
:id: capture-negotiation
:title: What a counter costs
:shuffle: true
question: "Why does a Counter over a hot method cost a fraction of what a recording tape does?"
options:
  - { text: "It declares no capture on either axis, so when it is the only listener recording skips value capture and signature binding entirely", correct: true }
  - { text: "It samples one operation in a hundred", explanation: "A counter counts every operation as it begins. Sampling is a combinator, and a different choice." }
  - { text: "It runs on a background thread rather than inline", explanation: "Every sink is notified inline, on the thread that ran the operation. The saving is in what is not captured." }
  - { text: "It hears only on_enter, so the operation's completion is never recorded", explanation: "The completion still happens and is still delivered to any sink that wants it. The counter's cheapness comes from asking for no values." }
explanation: The effective capture level for an event is the highest any active sink declares. A collector declaring "none" on both axes, alone, lets recording skip binding the arguments to the signature, which dominates the cost of recording a call.
```

The Finish button below says where to go next.
