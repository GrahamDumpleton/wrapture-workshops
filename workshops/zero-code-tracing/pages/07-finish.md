---
title: Finish
requires: [quiz:deferral]
---

# Finish

The program never changed. Everything the previous workshop put in the
entry point moved into a file beside it, and two doors, the runner and
autowrapt, applied that file before the program ran.

- An `[[observe]]` entry names one exact target and its members, and
  `redact` keeps a parameter out of every sink; `[[sink]]` entries are
  the printer or the JSON Lines file, and several fan out.

- Applying a config imports nothing. Each entry waits for the
  application to import its module, which is why `report()` says
  `pending` before the import and `applied` after it.

- `python -m wrapture` owns the command line; `AUTOWRAPT_BOOTSTRAP`
  with autowrapt installed injects the same config where nothing does.
  `suspend()`, `resume()` and `revert()` operate the result without a
  restart.

- A JSON Lines file is a trace you can keep, read back with
  `load_events()`, and hand to the converters for Perfetto, a snapshot
  or a diagram.

```{quiz}
:id: deferral
:title: Pending entries
:shuffle: true
question: "The first report in operate.py listed every observe entry as pending, even though the config had already been applied. Why?"
options:
  - { text: "Applying a config registers a post-import hook per target and imports nothing; the bindings land when the application imports shop itself", correct: true }
  - { text: "autowrapt applies the config lazily, on the first call through an observed method", explanation: "autowrapt fires the bootstrap at interpreter startup and the config is applied there in full. What waits is each entry's binding, on the import of its target module." }
  - { text: "The report was printed before the sink was registered, so nothing could be applied yet", explanation: "The same report shows the sink already in place. Sinks resolve when the file loads, because a sink must exist before events flow; observe entries are the part that defers." }
  - { text: "Entries stay pending until the first orders.run() call proves the members exist", explanation: "Members are resolved when the target module is imported, not when they are called. The second report, printed before any order was placed, already listed them as applied." }
explanation: Observe entries defer so the application's import order is never changed by observing it. Each registers a hook that fires when its target module is imported, immediately if it already was, and the applied record's pending view names the entries still waiting.
```

The Finish button below says where to go next.
