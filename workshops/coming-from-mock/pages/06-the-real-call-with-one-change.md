---
title: The real call, with one change
requires: [verify:real-call]
---

# The real call, with one change

This is where substitution runs out of road. `Mock(wraps=real)`
forwards calls to the real method and records them, and that is all it
can do: it cannot modify the arguments the original receives and
cannot post-process its result, and `create_autospec(spec, wraps=real)`
accepts `wraps` and ignores it. The standard library has no way to say
"run the real method, but change one thing".

With wrapture that is the ordinary case. A binding with no behaviour
wraps and records the real call, including its real result, which a
mock never records; `transforms_result()` then pins the charge id for
a stable assertion while the real amount still comes from the real
method.

```{editor-replace}
:id: convert-wraps
:path: test_shop.py
:regex: true
:match: ^def test_real_charge_with_mock\(.*\n(?:    .*\n)+
def test_real_charge_with_wrapture():
    charge = wrapture.binding(Gateway, "charge")
    charge.on_call.transforms_result(lambda result: {**result, "id": "ch_TEST"})
    with wrapture.timeline(charge):
        result = OrderService().place(500, CARD, tenant="acme")
        charge.events.with_args(amount=500, card=CARD).assert_once()
        assert charge.events.first.result["amount"] == 500
        assert result["id"] == "ch_TEST"

```

```{execute}
:id: run-real-call
:session: shell
:wait: prompt
pytest -q test_shop.py
```

The mock version also had to patch a gateway instance and inject it,
because wrapping a method on the class with `wraps` needs a bound
method to forward to. The binding goes on the class and sees the call
whichever instance the service made it on; `with_instance()` narrows
to one object when that matters. `transforms_args()` is the same idea
on the way in.

```{verify}
:id: real-call
:label: The wraps test is converted and the suite is green
:substrate: shell
:trigger: after:run-real-call; file-saved test_shop.py
out=$(.venv/bin/python -m pytest -q --color=no test_shop.py 2>&1) && printf '%s\n' "$out" | grep -q '10 passed' && ! grep -q -E '^def (test_real_charge_with_mock)\(' test_shop.py && [ "$(grep -c -E '^def (test_real_charge_with_wrapture)\(' test_shop.py)" = "1" ] && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; grep -E '^def (test_real_charge_with_mock|test_real_charge_with_wrapture)\(' test_shop.py | sed 's/^/still in the file: /'; exit 1
```
