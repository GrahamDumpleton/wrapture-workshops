---
title: Fan-out, sampling and filtering
requires: [verify:composed]
---

# Fan-out, sampling and filtering

Combinators make sinks compose like building blocks. Each is itself a
sink wrapping others, so they nest freely. `Fanout(*sinks)` delivers
every notification to several sinks, with one broken inner sink
counted and skipped while its siblings still hear the event.
`Filter(predicate, sink)` forwards only events the predicate accepts,
consulted once when the event enters so the inner sink always sees
properly paired notifications. `Depth(max_depth, sink)` forwards only
the top levels of the call tree. `Sample(rate, sink)` keeps a random
fraction of whole call trees, deciding once at the root, because
sampling per event would emit children whose parents were never seen.

One registration can therefore serve several needs at different
costs. The script seeds the random module so the sample is the same
each run.

```{file-write}
:id: write-compose
:path: compose.py
:open: true
import random

import wrapture

from shop import Gateway, Ledger, OrderService
import orders


class Paths(wrapture.Sink):
    """Remember the path of every event that reached this sink."""

    capture_args = "none"
    capture_result = "none"

    def __init__(self):
        self.seen = []

    def on_enter(self, event):
        self.seen.append(event.path)


wrapture.binding(OrderService, "place").apply()
wrapture.binding(Gateway, "charge").apply()
wrapture.binding(Ledger, "record").apply()

roots = Paths()
charges = Paths()
sampled = Paths()

random.seed(7)
fanout = wrapture.add_sink(wrapture.Fanout(
    wrapture.Depth(1, roots),
    wrapture.Filter(lambda event: event.path.endswith("Gateway.charge"), charges),
    wrapture.Sample(0.5, sampled),
))
orders.run(times=10)
wrapture.remove_sink(fanout)

print("at depth 1:", len(roots.seen), "events, all", set(roots.seen))
print("through the filter:", len(charges.seen), "events, all", set(charges.seen))
print("in the sample:", sampled.seen.count("shop:OrderService.place"), "of 30 trees,", len(sampled.seen), "events")
```

```{execute}
:id: run-compose
:session: shell
:wait: prompt
python compose.py
```

```
at depth 1: 30 events, all {'shop:OrderService.place'}
through the filter: 30 events, all {'shop:Gateway.charge'}
in the sample: 16 of 30 trees, 42 events
```

Eighty operations ran, and each inner sink heard the part it asked
for. A combinator declares the capture levels of what it wraps, with
`Fanout` taking the highest of its inner sinks', so capture
negotiation sees through the composition, and here every inner sink
asked for nothing.

Sink-side narrowing happens after an event has been constructed and
its values captured. When the point is to keep a hot binding cheap,
`when=` on the binding decides before any of that exists, as the live
tracing workshop showed.

```{verify}
:id: composed
:label: Depth, filter and sampler each heard their share of the fan-out
:substrate: shell
:trigger: after:run-compose
out=$(.venv/bin/python compose.py 2>&1) && printf '%s\n' "$out" | grep -q "^at depth 1: 30 events, all {'shop:OrderService.place'}$" && printf '%s\n' "$out" | grep -q "^through the filter: 30 events, all {'shop:Gateway.charge'}$" && printf '%s\n' "$out" | grep -q '^in the sample: 16 of 30 trees, 42 events$' && { echo "30 roots at depth 1, 30 charges through the filter, 16 whole trees sampled"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check expects thirty roots at depth 1, thirty charges through the
filter, and the sample size the seed gives. If the sample differs,
`random.seed(7)` must come right before `add_sink()`, since the
sampler draws from the module's generator.
```
