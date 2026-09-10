---
title: Operating a traced process
requires: [verify:operated]
---

# Operating a traced process

Once injected, the process is still operable. The bootstrap keeps its
record of what was applied on `wrapture.bootstrap.applied`, and from
a console, a debugger or a signal handler that record answers what is
installed and lets you switch it off and on without a restart. The
script below does what you would do at a `python -i` prompt: ask for
the report before and after the shop is imported, then run the orders
suspended and again resumed.

```{file-write}
:id: write-operate
:path: operate.py
:open: true
import wrapture.bootstrap

applied = wrapture.bootstrap.applied
print(applied.report())

import orders

print(applied.report())

applied.suspend()
orders.run()
print("suspended: three orders placed")

applied.resume()
orders.run()
print("resumed: three orders placed")
```

```{execute}
:id: run-operate
:session: shell
:wait: prompt
AUTOWRAPT_BOOTSTRAP=wrapture python operate.py
```

```
sink: Printer()
applied: none
pending:
  shop:OrderService
  shop:Gateway
  shop:Ledger
sink: Printer()
applied:
  shop:OrderService.place
  shop:Gateway.charge
  shop:Ledger.record
suspended: three orders placed
shop:OrderService.place(amount=500, card='<redacted>', tenant='acme')
  shop:Gateway.charge(amount=500, card='<redacted>')
  ...
shop:OrderService.place -> {'id': 'ch_120', 'amount': 120} [113us]
resumed: three orders placed
```

The first report is the deferral from two pages ago made visible: the
config has been applied, the sink is listening, and every observe
entry is still pending because nothing has imported `shop` yet. The
`import orders` line brings `shop` in, the hooks fire, and the second
report lists the three bindings as applied. While suspended, the
wrappers stay in place and the calls pass straight through, so the
first `orders.run()` printed nothing; after `resume()` the second
printed the full trace. `revert()` would take the whole intervention
down, restoring the patched locations, and an entry that fires while
the record is suspended arrives suspended too.

```{verify}
:id: operated
:label: The report shows the deferral, and suspend silences the trace
:substrate: shell
:trigger: after:run-operate
out=$(AUTOWRAPT_BOOTSTRAP=wrapture .venv/bin/python operate.py 2>&1) && printf '%s\n' "$out" | grep -q '^applied: none$' && printf '%s\n' "$out" | grep -q '^  shop:Ledger.record$' && [ "$(printf '%s\n' "$out" | grep -c '^shop:OrderService.place(')" -eq 3 ] && printf '%s\n' "$out" | grep -q '^suspended: three orders placed$' && { echo "Three entries pending, then applied; one run traced out of two"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check runs `operate.py` under `AUTOWRAPT_BOOTSTRAP=wrapture` and
looks for `applied: none` in the first report, `shop:Ledger.record`
in the second, and exactly three `OrderService.place` opening lines,
the resumed run's. Six opening lines mean `suspend()` did not happen
before the first run; an `AttributeError` on `None` means the script
was run without the variable, so nothing was bootstrapped.
```
