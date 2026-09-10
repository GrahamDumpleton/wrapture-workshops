---
title: A terminal node
requires: [verify:leaf-declared]
---

# A terminal node

`tree=True` drops an operation and everything beneath it. The related
shape is to keep the operation's own event and drop everything
beneath it: a client library's entry point is worth seeing, the calls
it makes internally are not, and the entry point's duration should
cover them. That binding is a terminal node of the tree, and
`leaf=True` says so. `Gateway.charge` calls `Gateway.authorise`, so
with both bound, the leaf declaration decides whether the
authorisation appears.

`category=` is the other half of declaring what a target is: the kind
of operation its events are, one of `"external"`, `"database"`,
`"datastore"`, `"messaging"`, `"task"`, `"server"`, `"consumer"` or
`"template"`, carried on every event the binding records as a field
of its own and never changed afterwards.

```{file-write}
:id: write-leaf
:path: leaf.py
:open: true
import sys

import wrapture

from shop import Gateway, OrderService
import orders

wrapture.binding(OrderService, "place").apply()
authorise = wrapture.binding(Gateway, "authorise").apply()
wrapture.binding(Gateway, "charge", leaf=True, category="external").apply()

printer = wrapture.add_sink(wrapture.Printer(sys.stdout, timing=False))
orders.run()
wrapture.remove_sink(printer)

print("authorise calls filtered:", authorise.filtered_calls)

with wrapture.timeline() as tape:
    orders.run()

print(tape.where(category="external"))
```

```{execute}
:id: run-leaf
:session: shell
:wait: prompt
python leaf.py
```

```
shop:OrderService.place(amount=500, card='4111-1111-1111-1111', tenant='acme', channel='email')
  shop:Gateway.charge(amount=500, card='4111-1111-1111-1111')
  shop:Gateway.charge -> {'id': 'ch_500', 'amount': 500}
shop:OrderService.place -> {'id': 'ch_500', 'amount': 500}
...
authorise calls filtered: 0
<EventLog external: 3 event(s)>
    shop:Gateway.charge(amount=500, card='4111-1111-1111-1111')
    shop:Gateway.charge(amount=250, card='4000-0000-0000-0000')
    shop:Gateway.charge(amount=120, card='5555-4444-3333-2222')
```

No `authorise` line anywhere, though the binding is applied and the
method ran. Unlike a `tree=True` decline, a leaf counts nothing on
the bindings beneath it: the silence is structural, declared with the
binding, and visible on the tape by construction, since the leaf
event is there and has no children. Behaviour still applies beneath
it; only recording stops.

The category is for programs, not for the printed tree. It is
selected on everywhere events are selected: `of_category()` narrows
an event log, `tape.where(category=)` selects across bindings, a
`Filter` predicate reads `event.category`, a config's `filter` table
takes `category`, the JSON Lines record carries it as a key, and the
OpenTelemetry export uses it for the span kind.

```{verify}
:id: leaf-declared
:label: The charge is a leaf with a category, and the authorisation beneath it is silent
:substrate: shell
:trigger: after:run-leaf
out=$(.venv/bin/python leaf.py 2>&1) && [ "$(printf '%s\n' "$out" | grep -c '^  shop:Gateway.charge(')" -eq 3 ] && ! printf '%s\n' "$out" | grep -q 'authorise(' && printf '%s\n' "$out" | grep -q '^authorise calls filtered: 0$' && printf '%s\n' "$out" | grep -q '^<EventLog external: 3 event(s)>$' && { echo "Three charges printed, no authorise lines, and three external events on the tape"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check expects three indented `Gateway.charge` lines and no line
mentioning `authorise(`, a filtered count of zero, and an event log
of three `external` events. `leaf=True` and `category="external"`
both go on the charge binding.
```
