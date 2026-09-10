---
title: The order of calls
requires: [verify:order]
---

# The order of calls

`assert_has_calls([...])` checks a contiguous run of calls on one
mock, and `mock_calls == [...]` the exact list; across several mocks,
ordering needs them attached to a parent mock whose `mock_calls` is
then compared by hand. wrapture asserts order on the tape, across any
bindings, with filtered logs saying which calls. Without a flag
`assert_order` is a subsequence check, other events allowed between;
`consecutive=True` is `assert_has_calls`, and `exact=True` is the
`mock_calls` comparison.

```{editor-replace}
:id: convert-order
:path: test_shop.py
:regex: true
:match: ^def test_order_of_calls_with_mock\(.*\n(?:    .*\n)+
def test_order_of_calls_with_wrapture():
    charge = wrapture.binding(Gateway, "charge")
    with wrapture.timeline(charge) as tape:
        service = OrderService()
        service.place(500, CARD, tenant="acme")
        service.place(250, CARD, tenant="globex")
        tape.assert_order(charge.events.with_args(amount=500), charge.events.with_args(amount=250), consecutive=True)

```

```{execute}
:id: run-order
:session: shell
:wait: prompt
pytest -q test_shop.py
```

Argument matching is by parameter name against the normalised call,
so `with_args(amount=500)` matches however the caller spelled it,
where `call(500, CARD)` had to match the exact positional shape. And
the binding here has no behaviour, so both orders really went through
the gateway, the ledger and the notifier; the mock version stubbed the
charge to get a recorder, and lost the real calls to check the order
of two of them.

```{verify}
:id: order
:label: The order test is converted and the suite is green
:substrate: shell
:trigger: after:run-order; file-saved test_shop.py
out=$(.venv/bin/python -m pytest -q --color=no test_shop.py 2>&1) && printf '%s\n' "$out" | grep -q '10 passed' && ! grep -q -E '^def (test_order_of_calls_with_mock)\(' test_shop.py && [ "$(grep -c -E '^def (test_order_of_calls_with_wrapture)\(' test_shop.py)" = "1" ] && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; grep -E '^def (test_order_of_calls_with_mock|test_order_of_calls_with_wrapture)\(' test_shop.py | sed 's/^/still in the file: /'; exit 1
```
