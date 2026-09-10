---
title: Finish
---

# Finish

The service was never edited, and never restarted for a question:

- `Window` with `every=` in code closed a run each period and handed
  each report to a callable, with the last one cut short at `stop()`.

- The same arrangement in the config file, `[[window]]` beside
  `[[sink]]`, wrote one file per run into a directory named by the
  schedule's start, with a `filter` keeping the requests out of the
  table.

- `on_signal` opened a run from outside the process, and its report
  landed beside the scheduled ones with the request row in it.

- The always-on `jsonlines` stream rotated into a file per period,
  and a restart began a new schedule rather than resuming the old.

The Finish button below says where to go next.
