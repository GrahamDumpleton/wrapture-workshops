---
title: Reports on a schedule
requires: [verify:ticking-reports]
---

# Reports on a schedule

The sinks workshop ended with `window()`, a with-block that collects
for as long as its body runs and hands back a report on exit. That
suits a script. For a service that runs all day the schedule has to
come from somewhere else, and `Window` is the scheduled form: the
same contents plus the triggers, and `start()` arms it.

`every=` on its own is the back-to-back shape. Each run lasts the
whole period and closes as the next opens, so the report at each
boundary covers exactly one period and the totals reset. Reports are
retained on the window, the last ten by default, and `on_report=`
hands each one to a callable the moment its run closes, from the
scheduler thread. An hour is too long to wait for in a workshop, so a
second stands in.

```{file-write}
:id: write-ticking
:path: ticking.py
:open: true
import wrapture

from orders import run_for
from shop import Gateway, Ledger, OrderService

service = wrapture.bindings(
    place=wrapture.binding(OrderService, "place"),
    charge=wrapture.binding(Gateway, "charge"),
    record=wrapture.binding(Ledger, "record"),
)
service.apply()

reports = []
ticking = wrapture.Window(
    name="ticking", every=1, collect=[wrapture.Aggregate()], on_report=reports.append
)
print(ticking.describe())

ticking.start()
run_for(OrderService(), 2.5)
ticking.stop()

for report in reports:
    print(
        f"run {report.run}: {report.data['begun']} begun, {report.data['raised']} raised,"
        f" {report.duration:.1f}s, cut short: {report.cut_short}"
    )

print()
print(reports[0].text)
```

```{execute}
:id: run-ticking
:session: shell
:wait: prompt
python ticking.py
```

```
every 1s, back to back
run 1: 990 begun, 180 raised, 1.0s, cut short: False
run 2: 935 begun, 170 raised, 1.0s, cut short: False
run 3: 495 begun, 90 raised, 0.5s, cut short: True

aggregate "aggregate" run 1, 2026-09-10 18:34:01 to 18:34:02 +10:00 (1.0s), pid 13248
3 paths, 990 operations begun, 990 completed, 180 raised

calls   total    self  per-call   min    max  errors  path
  360  18.5ms  16.0ms      51us  14us  3.3ms      90  shop:OrderService.place
  360   1.6ms   1.6ms       5us   2us   38us      90  shop:Gateway.charge
  270   776us   776us       3us   2us    8us          shop:Ledger.record
```

Runs 1 and 2 closed on schedule. The run open when `stop()` was
called was closed early, and its report says so with `cut_short`,
which is also what a clean shutdown does to a run in progress at
interpreter exit. The header of each report says which run it was,
when it opened and closed in local time, and whose process; the table
has one row per bound location sorted by self time; and the same
figures are on `report.data` for a dashboard or a test to read
without parsing the text. The `errors` column appears only when
something failed, and counts a declined card the shop caught the same
as an exception that escaped.

Two more keywords change the shape. `duration=` (`for` in a config
file) gives the sampled form, thirty seconds of every hour, say, so
the service pays nothing in between; `align=True` puts the openings
on the wall-clock boundary of the period, hourly on the hour.

```{verify}
:id: ticking-reports
:label: The window closed two runs on schedule and cut the third short at stop()
:substrate: shell
:trigger: after:run-ticking
out=$(.venv/bin/python ticking.py 2>&1) && printf '%s\n' "$out" | grep -q '^run 1: .* cut short: False$' && printf '%s\n' "$out" | grep -q '^run 2: .* cut short: False$' && printf '%s\n' "$out" | grep -q 'cut short: True$' && { printf '%s\n' "$out" | grep '^run '; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check runs `ticking.py` again and expects runs 1 and 2 to close
on schedule and the last run to be cut short. No `run` lines at all
means the window was never started, or `on_report` is not appending
to the list; a first run already cut short means `every` is longer
than the traffic, so the schedule never reached a boundary.
```
