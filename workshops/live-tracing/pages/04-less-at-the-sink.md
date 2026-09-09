---
title: Less at the sink
requires: [verify:roots-only]
---

# Less at the sink

Three orders is a readable trace. Three thousand is not, and the answer
is rarely to bind fewer things, because the point of binding the layers
is to have them there when a question comes up. The tools for seeing
less sit either at the sink or at the binding. This page takes the
sink.

Combinators wrap a sink and gate what reaches it. `Depth(1, ...)`
forwards only the roots of each call tree, which turns the trace into
one opening and one closing line per order.

```{editor-replace}
:id: add-depth
:path: main.py
:match: wrapture.add_sink(wrapture.Printer())
wrapture.add_sink(wrapture.Depth(1, wrapture.Printer()))
```

```{execute}
:id: run-depth
:session: shell
:wait: prompt
python main.py
```

```
shop:OrderService.place(amount=500, card='<redacted>', tenant='acme')
shop:OrderService.place -> {'id': 'ch_500', 'amount': 500} [273us]
shop:OrderService.place(amount=250, card='<redacted>', tenant='globex')
shop:OrderService.place !! CardDeclined [63us]
shop:OrderService.place(amount=120, card='<redacted>', tenant='globex')
shop:OrderService.place -> {'id': 'ch_120', 'amount': 120} [55us]
```

The gateway and ledger calls still happen and are still recorded; the
combinator drops them on the way to the printer. `Depth(2, ...)` would
keep roots and their direct children, `Filter(predicate, sink)` keeps
whatever a function of the event says, and `Sample(rate, sink)` keeps
a fraction of whole trees. They nest, so one registration can feed a
counter everything and a printer the top of the tree.

Narrowing here is cheap to write but not free to run: by the time a
combinator declines an event, the event has been built and its
arguments captured. The next page narrows before any of that exists.

```{verify}
:id: roots-only
:label: The trace is the three place calls and nothing beneath them
:substrate: shell
:trigger: after:run-depth
out=$(.venv/bin/python main.py 2>&1) && [ "$(printf '%s\n' "$out" | wc -l | tr -d ' ')" -eq 6 ] && ! printf '%s\n' "$out" | grep -q '^ ' && { echo "Six lines, all at the root: one opening and one closing line per order"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check expects exactly six lines from `main.py`, none of them
indented. Indented lines mean the `Depth(1, ...)` wrapper is missing
from the `add_sink()` line; more or fewer root lines mean `orders.py`
or the bindings have changed.
```
