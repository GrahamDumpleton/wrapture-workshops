---
title: Three bindings and a sink
requires: [verify:first-trace]
---

# Three bindings and a sink

The entry point is a new file, `main.py`. It applies a binding to each
of the three methods that matter and registers a `Printer`, the
simplest sink wrapture ships: it prints each event to standard error
as it happens. Then it runs the orders.

```{file-write}
:id: write-main
:path: main.py
:open: true
import wrapture

from shop import Gateway, Ledger, OrderService
import orders

wrapture.binding(OrderService, "place").apply()
wrapture.binding(Gateway, "charge").apply()
wrapture.binding(Ledger, "record").apply()

wrapture.add_sink(wrapture.Printer())

orders.run()
```

There is no `timeline()` anywhere in that. The bindings are applied for
the life of the process, the sink is registered for the life of the
process, and events flow from one to the other.

```{execute}
:id: run-first-trace
:session: shell
:wait: prompt
python main.py
```

```
shop:OrderService.place(amount=500, card='4111-1111-1111-1111', tenant='acme')
  shop:Gateway.charge(amount=500, card='4111-1111-1111-1111')
  shop:Gateway.charge -> {'id': 'ch_500', 'amount': 500} [8us]
  shop:Ledger.record(entry={'id': 'ch_500', 'amount': 500})
  shop:Ledger.record -> 'led_ch_500' [6us]
shop:OrderService.place -> {'id': 'ch_500', 'amount': 500} [245us]
shop:OrderService.place(amount=250, card='4000-0000-0000-0000', tenant='globex')
  shop:Gateway.charge(amount=250, card='4000-0000-0000-0000')
  shop:Gateway.charge !! CardDeclined [5us]
shop:OrderService.place !! CardDeclined [62us]
shop:OrderService.place(amount=120, card='5555-4444-3333-2222', tenant='globex')
  shop:Gateway.charge(amount=120, card='5555-4444-3333-2222')
  shop:Gateway.charge -> {'id': 'ch_120', 'amount': 120} [4us]
  shop:Ledger.record(entry={'id': 'ch_120', 'amount': 120})
  shop:Ledger.record -> 'led_ch_120' [4us]
shop:OrderService.place -> {'id': 'ch_120', 'amount': 120} [118us]
```

Each operation gets a line when it begins, indented by how deeply it is
nested, and a closing line with the outcome and how long it took. A
`->` marks a return value and `!!` marks an exception, so the declined
card is visible at a glance, and so is the fact that `Ledger.record`
never ran for that order. These are the real arguments and the real
results, with the same markers `tape.tree()` uses in a test, only
arriving live rather than reconstructed afterwards.

The obvious worry about leaving bindings applied in a program is what
they cost when nothing is being traced. The recording gate is not "is
there a timeline" but "is anything listening", and when nothing is, an
applied binding constructs no event at all: the wrapped method runs
with only wrapt's own dispatch on top. That is what makes it reasonable
to bind the interesting methods once, in the entry point, and let the
sink decide whether anything is recorded.

```{verify}
:id: first-trace
:label: The trace shows all three orders, with the declined card
:substrate: shell
:trigger: after:run-first-trace
out=$(.venv/bin/python main.py 2>&1) && [ "$(printf '%s\n' "$out" | grep -c '^  shop:Gateway.charge(')" -eq 3 ] && printf '%s\n' "$out" | grep -q '^  shop:Gateway.charge !! CardDeclined' && [ "$(printf '%s\n' "$out" | grep -c "^  shop:Ledger.record -> ")" -eq 2 ] && { echo "Three charges, one declined, and two ledger writes on the trace"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check runs `main.py` itself and looks for three indented
`Gateway.charge` lines, one of them ending in `!! CardDeclined`, and
two `Ledger.record` results. What it printed is the message above.
`main.py` must be exactly the file the action wrote; write it again if
in doubt.
```
