---
title: Clocks and restarts
requires: [quiz:batch-restart]
---

# Clocks and restarts

Everything is local time: `at`, `align`, and the `{date}` and
`{time}` variables, because "22:00" in a config is what an operator
means by 22:00 on that machine, and file names, report headers and
the machine's own logs then agree. There is no time zone setting;
each report states its start time with its offset so it is
unambiguous alone, and `{utc:...}` is the one UTC path variable.

Wall-clock triggers, `at` and an aligned `every`, are computed by
finding the next occurrence in local time afresh after each run,
never by adding seconds to the previous one. On the night the clocks
go forward a time that does not exist is skipped to the next day; on
the night they go back the repeated hour fires once. Relative
triggers, `after` and an unaligned `every`, and `for` are monotonic
durations, unaffected by clock steps.

Schedules live in the process and start afresh at apply, which the
previous page showed as the second `summary` directory. Nothing is
persisted or resumed: `after` and an unaligned `every` are measured
from apply, so a restart shifts that cadence; `at` waits for its next
occurrence; and `times` counts runs of this process. A schedule with
no batch to lose is restart-proof by construction: `every = "1h"`
with `align = true` simply waits for the next hour boundary and
carries on, each run named by its own timestamp. A clean shutdown
during an open run closes it, marks its report `cut_short` and
delivers it, which is what the last report in the `summary`
directory says; a hard kill loses it. Under a pre-fork server each
worker has its own windows, so put `{pid}` in the report path and
add `jitter` to spread the aligned openings.

```{quiz}
:id: batch-restart
:title: A batch and a restart
:shuffle: true
question: "A config has a window with at = \"22:00\", every = \"1h\" and times = 12, an overnight batch. The service is restarted at 01:30. What happens to the batch?"
options:
  - { text: "The remaining runs are not made: times counts runs of this process, and nothing is persisted or resumed", correct: true }
  - { text: "The new process resumes at 02:00 with the nine runs that were left", explanation: "Nothing is persisted. The new process knows only its config, and at waits for the next 22:00." }
  - { text: "The new process starts the batch again at once, so the reports overlap the old ones", explanation: "at opens the first run at the next local occurrence of the time, which is 22:00 that evening, and the old process is gone." }
  - { text: "wrapture refuses the config at startup because the batch is in progress", explanation: "A config knows nothing about a previous process. It is applied afresh, and the batch simply starts at the next 22:00." }
explanation: Reach for at plus times when the batch itself is the point, knowing a restart ends it early. The restart-proof shape is every with align, which waits for the next boundary and carries on.
```
