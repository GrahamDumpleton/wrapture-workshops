---
title: Numbers, not events
requires: [verify:collected]
---

# Numbers, not events

Not every question needs the events themselves; often a number is
the answer. Two collectors keep numbers and nothing else, so they are
safe to leave running for a whole test suite or a long-lived process.
`Counter()` counts operations as they begin, failures included.
`Aggregate()` keeps one row per path: how many operations began,
completed and raised, and the total, self, fastest and slowest times
of the completed ones. Memory is bounded by the number of bound
locations, however many events flow.

Both are sinks, so `add_sink()` registers them and their attributes
can be read directly. Both are also collectors in the scheduled
tracing sense: placed in a window they accumulate while a run is
open and hand back a report when it closes.

```{file-write}
:id: write-numbers
:path: numbers.py
:open: true
import wrapture

from shop import Gateway, Ledger, OrderService
import orders

wrapture.binding(OrderService, "place").apply()
wrapture.binding(Gateway, "charge").apply()
wrapture.binding(Ledger, "record").apply()

counter = wrapture.add_sink(wrapture.Counter())
orders.run(times=10)
wrapture.remove_sink(counter)
print("operations begun:", counter.count)

with wrapture.window(collect=[wrapture.Aggregate()]) as run:
    orders.run(times=10)

print(run.reports[0].text)
```

```{execute}
:id: run-numbers
:session: shell
:wait: prompt
python numbers.py
```

```
operations begun: 80
aggregate "aggregate" run 1, ... (0.0s), pid ...
3 paths, 80 operations begun, 80 completed, 20 raised

calls   total    self  per-call    min    max  errors  path
   30   ...      ...        ...    ...    ...      10  shop:OrderService.place
   30   ...      ...        ...    ...    ...      10  shop:Gateway.charge
   20   ...      ...        ...    ...    ...          shop:Ledger.record
```

`self` is the figure profilers rank by, and the table is sorted by
it: the time spent in the operation itself, excluding the time its
observed children account for. wrapture computes it from the parent
links as events close, retaining nothing. Both collectors declare
`"none"` on both capture axes, which matters: when no other active
sink asks for more, recording skips value capture entirely, including
signature binding, the dominant cost of recording a call. A counter
over a hot method costs a fraction of what a recording tape does,
which is what makes the query budget from the pytest workshop cheap
enough to leave under a whole suite.

```{verify}
:id: collected
:label: The counter and the aggregate report agree on eighty operations
:substrate: shell
:trigger: after:run-numbers
out=$(.venv/bin/python numbers.py 2>&1) && printf '%s\n' "$out" | grep -q '^operations begun: 80$' && printf '%s\n' "$out" | grep -q '^3 paths, 80 operations begun, 80 completed, 20 raised$' && printf '%s\n' "$out" | grep -Eq '^ +30 .* 10 +shop:OrderService.place$' && printf '%s\n' "$out" | grep -Eq '^ +20 .* shop:Ledger.record$' && { echo "80 counted, 3 paths aggregated with 20 raised, 10 of them on the order"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check expects the counter at 80, the report's second line to
name 3 paths and 20 raised, a row of 30 calls with 10 errors for
`OrderService.place`, and a row of 20 calls for `Ledger.record`.
Both runs must place the orders ten times.
```
