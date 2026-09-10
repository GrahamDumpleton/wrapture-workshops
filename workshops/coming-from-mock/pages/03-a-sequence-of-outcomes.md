---
title: A sequence of outcomes
requires: [verify:sequence]
---

# A sequence of outcomes

mock's `side_effect` also takes a list, consumed one entry per call,
with exceptions raised and anything else returned. The retry test
uses it for two timeouts and then a success. wrapture keeps values and
exceptions apart: `returns_from()` hands out successive values from an
iterable, and `then()` adds a phase that takes over, on a count with
`after=`, on a condition with `until=`, or when a sequence runs out.
Here the first phase raises and the phase after two calls returns.

```{editor-replace}
:id: convert-sequence
:path: test_shop.py
:regex: true
:match: ^def test_retry_with_mock\(.*\n(?:    .*\n)+
def test_retry_with_wrapture():
    charge = wrapture.binding(Gateway, "charge")
    charge.on_call.raises(TimeoutError("down"))
    charge.on_call.then(after=2).returns({"id": "ch_500", "amount": 500})
    with wrapture.timeline(charge):
        assert place_with_retry(OrderService(), 500, CARD, tenant="acme")["id"] == "ch_500"
        charge.events.assert_times(3)
        charge.events.raising(TimeoutError).assert_times(2)

```

```{execute}
:id: run-sequence
:session: shell
:wait: prompt
pytest -q test_shop.py
```

More lines for the same three outcomes, but each phase says what it
is, and the same shape covers what a list cannot: a phase that ends
on a condition seen in the calls, `advance()` from the test, and
`in_phase(n)` on the recording to say which regime a call ran under.
The `call_count` assertion became `assert_times(3)` on the events,
and gained the one beside it that mock has no words for: two of the
three calls raised.

```{verify}
:id: sequence
:label: The retry test is converted and the suite is green
:substrate: shell
:trigger: after:run-sequence; file-saved test_shop.py
out=$(.venv/bin/python -m pytest -q --color=no test_shop.py 2>&1) && printf '%s\n' "$out" | grep -q '10 passed' && ! grep -q -E '^def (test_retry_with_mock)\(' test_shop.py && [ "$(grep -c -E '^def (test_retry_with_wrapture)\(' test_shop.py)" = "1" ] && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; grep -E '^def (test_retry_with_mock|test_retry_with_wrapture)\(' test_shop.py | sed 's/^/still in the file: /'; exit 1
```
