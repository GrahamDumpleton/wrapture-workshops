---
title: Calls an object makes to itself
requires: [verify:self-call]
---

# Calls an object makes to itself

The mock approach to testing `OrderService` is to inject a `MagicMock`
as the gateway and assert on what it recorded. That is the third test
in the file. Ask the mock what it actually saw.

```{execute}
:id: show-mock-calls
:session: shell
:wait: prompt
python -c "from unittest.mock import MagicMock; from orders import OrderService; g = MagicMock(); OrderService(gateway=g).place(500); print(*g.mock_calls, sep='\n')"
```

The `charge()` call is there, followed by a trail of fabricated chains
as the service reached into a return value that was never a real
dictionary. What is not there, and cannot be, is `_take_payment()`. The
call from `place()` to `_take_payment()` never crosses the seam the
mock sits behind. And patching `_take_payment` instead replaces it, so
the real payment logic does not run. Either the method is invisible or
it is gone.

A binding goes on the class, so a call the object makes to itself
passes through the wrapper like any other. This test records two
bindings on one timeline and asks how the calls nested.

```{file-write}
:id: write-self-call-test
:path: test_orders.py
:mode: append
:open: true



def test_self_call_with_wrapture():
    take_payment = wrapture.binding(OrderService, "_take_payment")
    charge = wrapture.binding(Gateway, "charge")

    with wrapture.timeline(take_payment, charge) as tape:
        OrderService().place(500)

        take_payment.events.with_args(amount=500).assert_once()
        assert tape.parent_of(charge.events.first) is take_payment.events.first

    print(tape.tree())
```

The last line prints the tape's call tree. Run the test with `-s` so
pytest shows it.

```{execute}
:id: run-self-call
:session: shell
:wait: prompt
pytest -q -s test_orders.py -k self_call_with_wrapture
```

The charge happened inside the payment step, which is what the
`parent_of()` assertion says and what the tree shows. The arguments are
real, normalised against the real signature, so the `currency` default
appears though nobody passed it, and the return values are real too,
nested the way the calls actually nested.

```{verify}
:id: self-call
:label: The private method was seen, with the charge inside it
:substrate: shell
:trigger: after:run-self-call
out=$(.venv/bin/python -m pytest -q --color=no test_orders.py -k self_call_with_wrapture 2>&1) && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; exit 1
```
