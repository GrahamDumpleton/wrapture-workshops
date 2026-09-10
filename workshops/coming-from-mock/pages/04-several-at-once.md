---
title: Several at once
requires: [verify:group]
---

# Several at once

`patch.multiple()` patches several attributes of one object, each
becoming its own `Mock` to configure separately, and the ledger
failure test nests a third patch inside it. With wrapture several
bindings are a group: one object, one lifecycle, each member carrying
its own behaviour, and the members need not be on the same class.

```{editor-replace}
:id: convert-group
:path: test_shop.py
:regex: true
:match: ^def test_ledger_failure_with_mock\(.*\n(?:    .*\n)+
def test_ledger_failure_with_wrapture():
    group = wrapture.bindings(
        charge=wrapture.binding(Gateway, "charge"),
        refund=wrapture.binding(Gateway, "refund"),
        record=wrapture.binding(Ledger, "record"),
    )
    group.charge.on_call.returns({"id": "ch_500", "amount": 500})
    group.record.on_call.raises(OSError("disk full"))
    with wrapture.timeline(group):
        with pytest.raises(OSError):
            OrderService().place(500, CARD, tenant="acme")
        group.refund.events.with_args(charge_id="ch_500").assert_once()

```

```{execute}
:id: run-group
:session: shell
:wait: prompt
pytest -q test_shop.py
```

Two things here have no mock equivalent. The `refund` member has no
behaviour at all: it stays the real method and is there to be
observed, so inside a timeline the group mixes stubbed, failing and
purely watched methods in one declaration, and the assertion reads
the real refund's arguments by parameter name. And the group never
half-applies: if any member fails to apply, the ones already applied
are removed again, where a stack of `patch.object` managers that
fails midway unwinds only through the ordinary context manager
machinery.

```{verify}
:id: group
:label: The ledger failure test is converted and the suite is green
:substrate: shell
:trigger: after:run-group; file-saved test_shop.py
out=$(.venv/bin/python -m pytest -q --color=no test_shop.py 2>&1) && printf '%s\n' "$out" | grep -q '10 passed' && ! grep -q -E '^def (test_ledger_failure_with_mock)\(' test_shop.py && [ "$(grep -c -E '^def (test_ledger_failure_with_wrapture)\(' test_shop.py)" = "1" ] && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; grep -E '^def (test_ledger_failure_with_mock|test_ledger_failure_with_wrapture)\(' test_shop.py | sed 's/^/still in the file: /'; exit 1
```
