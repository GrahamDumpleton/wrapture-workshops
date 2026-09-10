---
title: A value and a failure
requires: [verify:value-and-failure]
---

# A value and a failure

Both tools stub a return value well, and for a pure stub there is
little to choose between them. The mock version names the method on
the class and hands it a value; the wrapture version names the same
method and gives it one behaviour. Injecting a failure is the same
move with `side_effect` on one side and `raises()` on the other, and
in both versions the patched method itself never runs.

First the import the converted tests need, then the first two tests,
each replaced in place.

```{editor-replace}
:id: add-import
:path: test_shop.py
:match: import pytest
import pytest
import wrapture
```

```{editor-replace}
:id: convert-stub
:path: test_shop.py
:regex: true
:match: ^def test_stub_with_mock\(.*\n(?:    .*\n)+
def test_stub_with_wrapture():
    with wrapture.binding(Gateway, "charge").on_call.returns({"id": "stub", "amount": 0}):
        assert OrderService().place(500, CARD, tenant="acme")["id"] == "stub"

```

```{editor-replace}
:id: convert-failure
:path: test_shop.py
:regex: true
:match: ^def test_gateway_down_with_mock\(.*\n(?:    .*\n)+
def test_gateway_down_with_wrapture():
    with wrapture.binding(Gateway, "charge").on_call.raises(TimeoutError("down")):
        with pytest.raises(TimeoutError):
            OrderService().place(500, CARD, tenant="acme")

```

```{execute}
:id: run-value-and-failure
:session: shell
:wait: prompt
pytest -q test_shop.py
```

Still ten. The difference is everything around the stub. A mock
validates a stubbed call against the real signature only if
`autospec=True` was asked for; a binding is strict by default, so a
call that `returns()` or `raises()` would answer is bound to the
method's signature first and a drifted call raises `TypeError` as the
real one would. And in the failure test only the one bound method is
replaced: the ledger, the notifier and the refund path stay real, so
a test can go on to assert on what the rest of the system did about
the failure, which the mock version, with the rest of the pipeline
typically mocked too, cannot.

```{verify}
:id: value-and-failure
:label: The stub and the failure are converted and the suite is green
:substrate: shell
:trigger: after:run-value-and-failure; file-saved test_shop.py
out=$(.venv/bin/python -m pytest -q --color=no test_shop.py 2>&1) && printf '%s\n' "$out" | grep -q '10 passed' && ! grep -q -E '^def (test_stub_with_mock|test_gateway_down_with_mock)\(' test_shop.py && [ "$(grep -c -E '^def (test_stub_with_wrapture|test_gateway_down_with_wrapture)\(' test_shop.py)" = "2" ] && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; grep -E '^def (test_stub_with_mock|test_gateway_down_with_mock|test_stub_with_wrapture|test_gateway_down_with_wrapture)\(' test_shop.py | sed 's/^/still in the file: /'; exit 1
```

```{hint}
:title: If the check fails
The check expects ten passes with `test_stub_with_wrapture` and
`test_gateway_down_with_wrapture` in the file and the two mock
versions gone. If a replace found nothing to match, the test above
it has already been converted; a `NameError` on `wrapture` means the
import was not added.
```
