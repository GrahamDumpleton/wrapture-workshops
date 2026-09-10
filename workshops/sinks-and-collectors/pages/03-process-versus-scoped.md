---
title: Process versus scoped
requires: [verify:thread-heard, verify:cost-measured]
---

# Process versus scoped

Sinks are registered on one of two tiers, and the difference is who
can hear. A timeline's tape is a scoped sink: it lives in a context
variable, is visible only to the context that opened it, and
propagates the way context does, into asyncio tasks but not into
threads. A process sink, registered with `add_sink()`, hears every
recorded event from every thread and task until `remove_sink()`. The
script runs the orders on a worker thread under each.

```{file-write}
:id: write-threads
:path: threads.py
:open: true
import threading
import warnings

import wrapture

from shop import Gateway, Ledger, OrderService
import orders

place = wrapture.binding(OrderService, "place").apply()
wrapture.binding(Gateway, "charge").apply()
wrapture.binding(Ledger, "record").apply()


def on_a_worker_thread():
    worker = threading.Thread(target=orders.run)
    worker.start()
    worker.join()


with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always", wrapture.RecordingGapWarning)
    with wrapture.timeline() as tape:
        on_a_worker_thread()

print("events on the tape:", len(tape.all))
print("calls the tape missed:", place.missed_calls)
print("warned about:", str(caught[0].message).split(": ")[0] if caught else "nothing")

counter = wrapture.add_sink(wrapture.Counter())
on_a_worker_thread()
wrapture.remove_sink(counter)
print("operations the process sink heard:", counter.count)
```

```{execute}
:id: run-threads
:session: shell
:wait: prompt
python threads.py
```

```
events on the tape: 0
calls the tape missed: 3
warned about: shop:OrderService.place
operations the process sink heard: 8
```

The tape heard nothing, and said so: each binding raised a
`RecordingGapWarning` and counted the calls on `missed_calls`, so a
shorter tape than expected is loud rather than silent. The process
sink heard all eight operations with nesting intact. The thread
limitation is a property of scoped recording, not of recording
itself; a thread can be opted in with `wrapture.propagate()` where a
test needs it.

```{verify}
:id: thread-heard
:label: The timeline missed the thread and the process sink heard it
:substrate: shell
:trigger: after:run-threads
out=$(.venv/bin/python threads.py 2>&1) && printf '%s\n' "$out" | grep -q '^events on the tape: 0$' && printf '%s\n' "$out" | grep -q '^calls the tape missed: 3$' && printf '%s\n' "$out" | grep -q '^warned about: shop:OrderService.place$' && printf '%s\n' "$out" | grep -q '^operations the process sink heard: 8$' && { echo "Tape: 0 events, 3 missed and a warning; process sink: 8 operations"; exit 0; }; printf '%s\n' "$out"; exit 1
```

## What listening costs

The obvious worry about leaving bindings applied is what they cost
when nothing is traced. Measure it: the same method unbound, bound
with nobody listening, and bound while a timeline records.

```{file-write}
:id: write-cost
:path: cost.py
:open: true
import time

import wrapture

from shop import Gateway

gateway = Gateway()
charge = wrapture.binding(Gateway, "charge")


def time_calls(label):
    started = time.perf_counter()
    for _ in range(20000):
        gateway.charge(1, "4111-1111-1111-1111")
    print(f"{label}: {(time.perf_counter() - started) * 1e6 / 20000:.2f}us per call")


time_calls("unbound")
with charge:
    time_calls("bound, nobody listening")
    with wrapture.timeline():
        time_calls("bound and recording")
```

```{execute}
:id: run-cost
:session: shell
:wait: prompt
python cost.py
```

The figures depend on the machine, but the shape does not: a bound
method with nobody listening pays wrapt's dispatch, a couple of
microseconds at most, and constructs no event; recording costs an
order of magnitude more, because that is when the arguments are
bound to the signature and captured. That gap is what makes it
reasonable to bind the interesting methods once, in the entry point,
and let the sinks decide whether anything is recorded.

```{verify}
:id: cost-measured
:label: All three timings were measured
:substrate: shell
:trigger: after:run-cost
out=$(.venv/bin/python cost.py 2>&1) && [ "$(printf '%s\n' "$out" | grep -c 'us per call$')" -eq 3 ] && printf '%s\n' "$out" | grep -q '^bound and recording:' && { printf '%s\n' "$out"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If a check fails
`threads.py` must run the orders on a `threading.Thread` inside the
timeline and again under the `Counter`. `cost.py` prints three lines
ending in `us per call`; the check reads the lines, not the numbers.
```
