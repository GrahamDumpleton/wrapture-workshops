---
title: Less at the binding
requires: [verify:one-tenant]
---

# Less at the binding

At the binding, `when=` takes a predicate that is consulted before any
event exists. A falsey answer means no event is constructed, no
arguments are captured and nothing is delivered, which is the cheap
way to narrow a hot call site. The method still runs, and any
behaviour on the binding still applies; only recording is skipped.

Here it records orders for one tenant only. The bindings get names
now, since the next page asks them a question, and the sink goes back
to a plain `Printer` so the whole tree shows.

```{file-write}
:id: write-when
:path: main.py
:open: true
import wrapture

from shop import Gateway, Ledger, OrderService
import orders


def acme_only(instance, args, kwargs):
    return kwargs.get("tenant") == "acme"


place = wrapture.binding(OrderService, "place", when=acme_only, capture=wrapture.redact("card")).apply()
charge = wrapture.binding(Gateway, "charge", capture=wrapture.redact("card")).apply()
record = wrapture.binding(Ledger, "record").apply()

wrapture.add_sink(wrapture.Printer())

orders.run()
```

```{execute}
:id: run-when
:session: shell
:wait: prompt
python main.py
```

```
shop:OrderService.place(amount=500, card='<redacted>', tenant='acme')
  shop:Gateway.charge(amount=500, card='<redacted>')
  shop:Gateway.charge -> {'id': 'ch_500', 'amount': 500} [8us]
  shop:Ledger.record(entry={'id': 'ch_500', 'amount': 500})
  shop:Ledger.record -> 'led_ch_500' [6us]
shop:OrderService.place -> {'id': 'ch_500', 'amount': 500} [307us]
shop:Gateway.charge(amount=250, card='<redacted>')
shop:Gateway.charge !! CardDeclined [9us]
shop:Gateway.charge(amount=120, card='<redacted>')
shop:Gateway.charge -> {'id': 'ch_120', 'amount': 120} [6us]
shop:Ledger.record(entry={'id': 'ch_120', 'amount': 120})
shop:Ledger.record -> 'led_ch_120' [4us]
```

The globex orders are gone, but their gateway and ledger calls are
not. A `when=` decline skips exactly one event, the declined
operation's own, and whatever records beneath it still records, now
with nothing above it, so each inner call turns up as a root of its
own with no `place` to explain it. Sometimes that is exactly right: a
binding whose only job is to intervene in a call should not silence
what runs beneath it.

When the intent is "nothing from here down", `tree=True` says so.

```{editor-replace}
:id: add-tree
:path: main.py
:match: when=acme_only,
when=acme_only, tree=True,
```

```{execute}
:id: run-tree
:session: shell
:wait: prompt
python main.py
```

```
shop:OrderService.place(amount=500, card='<redacted>', tenant='acme')
  shop:Gateway.charge(amount=500, card='<redacted>')
  shop:Gateway.charge -> {'id': 'ch_500', 'amount': 500} [8us]
  shop:Ledger.record(entry={'id': 'ch_500', 'amount': 500})
  shop:Ledger.record -> 'led_ch_500' [6us]
shop:OrderService.place -> {'id': 'ch_500', 'amount': 500} [269us]
```

Now the decline covers the whole extent of the declined operation, and
the trace is one tenant's orders and nothing else. `tree=True` needs a
`when=` to act on, and `when=False, tree=True` silences a subtree
unconditionally, for a noisy library call whose internals are never
worth seeing.

```{verify}
:id: one-tenant
:label: The trace is one tenant's order, with everything beneath it
:substrate: shell
:trigger: after:run-tree
out=$(.venv/bin/python main.py 2>&1) && [ "$(printf '%s\n' "$out" | wc -l | tr -d ' ')" -eq 6 ] && ! printf '%s\n' "$out" | grep -q 'globex\|ch_250\|ch_120\|amount=250\|amount=120' && printf '%s\n' "$out" | grep -q "^  shop:Ledger.record -> 'led_ch_500'" && { echo "Six lines: the acme order and its gateway and ledger calls, nothing from globex"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
Twelve lines with `Gateway.charge` at the left margin means `when=` is
in place but `tree=True` is not yet on the `place` binding. Eighteen
lines means `main.py` is still the earlier version. The message above
is what the check saw.
```
