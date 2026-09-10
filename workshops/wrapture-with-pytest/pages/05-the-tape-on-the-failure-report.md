---
title: The tape on the failure report
requires: [verify:tape-attached, verify:tape-test-passes]
---

# The tape on the failure report

The plugin's second gift is a `tape` fixture: a recording scope
spanning the whole test, so bindings applied any way at all record
onto it, and when a test that used it fails, the tape's tree is
attached to the failure report. The output then shows what actually
ran, not just the assertion that tripped. This test asserts on an
amount nobody charged.

```{file-write}
:id: write-tape-test
:path: test_tape.py
:open: true
import wrapture

from shop import Gateway, Ledger, OrderService

CARD = "4111-1111-1111-1111"


def test_order_flow(tape):
    with wrapture.binding(Gateway, "charge") as charge, wrapture.binding(Ledger, "record") as record:
        OrderService().place(500, CARD, tenant="acme")

        charge.events.with_args(amount=999).assert_once()

    assert len(tape.all) == 2
```

```{execute}
:id: run-tape-test
:session: shell
:wait: prompt
pytest -q test_tape.py
```

The failure has two parts worth reading. The assertion itself says
what the filter kept and, under `filtered from:`, what it discarded,
which is how an over-narrowed filter explains itself:

```
AssertionError: expected exactly 1 event(s), got 0
<EventLog shop:Gateway.charge[amount=999]: 0 event(s)>
    (no events)
  filtered from:
    <EventLog shop:Gateway.charge: 1 event(s)>
        shop:Gateway.charge(amount=500, card='4111-1111-1111-1111')
```

And below it, under a `wrapture tape` heading, the tree of everything
the test recorded, with both calls and their results:

```
-------------------------------- wrapture tape ---------------------------------
shop:Gateway.charge(amount=500, card='4111-1111-1111-1111')  -> {'id': 'ch_500', 'amount': 500}
shop:Ledger.record(entry={'id': 'ch_500', 'amount': 500})  -> 'led_ch_500'
```

The plugin also rewrites plain `assert` statements that compare an
event log, so `assert charge.events.with_args(amount=999)` prints the
events the same way rather than a bare object repr.

```{verify}
:id: tape-attached
:label: The failure report carries the filtered-from events and the tape
:substrate: shell
:trigger: after:run-tape-test
out=$(.venv/bin/python -m pytest -q --color=no test_tape.py 2>&1); printf '%s\n' "$out" | grep -q 'filtered from:' && printf '%s\n' "$out" | grep -q 'wrapture tape' && printf '%s\n' "$out" | grep -q "shop:Ledger.record(entry={'id': 'ch_500', 'amount': 500})  -> 'led_ch_500'" && { echo "The report shows the one charge the filter discarded and the tape with both calls"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check runs `test_tape.py` and expects a failure whose report
shows `filtered from:` and a `wrapture tape` section listing the
ledger write. A pass means the amount has already been corrected; a
failure without those sections means the plugin is not loaded, so
check `conftest.py`.
```

Correct the amount and the test passes.

```{editor-replace}
:id: fix-amount
:path: test_tape.py
:match: with_args(amount=999)
with_args(amount=500)
```

```{execute}
:id: run-tape-test-again
:session: shell
:wait: prompt
pytest -q test_tape.py
```

```{verify}
:id: tape-test-passes
:label: The tape test passes
:substrate: shell
:trigger: after:run-tape-test-again; file-saved test_tape.py
out=$(.venv/bin/python -m pytest -q --color=no test_tape.py 2>&1) && printf '%s\n' "$out" | grep -q '1 passed' && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: What the fixture does not do
The fixture's timeline is given no bindings, so it applies none and
verifies no declared expectations itself. A `bound()` decorator's
binding verifies its own, and for a with-block binding with
expectations, open `timeline(...)` inside the test.
```
