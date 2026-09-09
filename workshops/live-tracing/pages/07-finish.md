---
title: Finish
requires: [quiz:orphans]
---

# Finish

The whole intervention is a few lines in the program's entry point:
bind the methods that matter, register a sink, and the program
describes what it is doing as it runs, with real arguments and real
results, and costs next to nothing when nothing is listening.

- A `Printer` is a process sink: registered with `add_sink()`, it hears
  every recorded event until removed, with no timeline in sight.

- `redact()` on the binding keeps a named parameter out of the trace
  before the event exists, so nothing downstream ever sees it.

- `Depth(1, ...)` narrows at the sink, after the event is built and
  captured. `when=` narrows at the binding, before any of that, and
  skips one event; `tree=True` extends the decline to everything
  beneath it.

- `filtered_calls` on each binding counts what it declined, so a short
  trace is explained rather than guessed at.

```{quiz}
:id: orphans
:title: Orphaned calls
question: "With when=acme_only on the place binding and no tree=True, why did the globex orders' Gateway.charge lines appear at the left margin?"
options:
  - { text: "The decline skipped only the place event, so the charge events recorded with nothing above them and became roots", correct: true }
  - { text: "The Printer prints every event at the margin unless Depth is in use", explanation: "The printer indents by the event's depth. Those charge events had depth zero because no place event was recorded above them." }
  - { text: "The charge binding also had a when= predicate that declined them", explanation: "Only the place binding had when=. The charge binding recorded every call, which is why its events appeared at all." }
  - { text: "Gateway.charge is called from _take_payment, which is not bound, so it always records as a root", explanation: "Nesting follows what is recorded, not what is bound. Under the acme order the same charge call sat beneath place." }
explanation: A when= decline skips exactly one event, the declined operation's own. Whatever records beneath it still records, with no parent, so each inner call becomes a root. tree=True is the way to say nothing from here down.
```

The Finish button below says where to go next.
