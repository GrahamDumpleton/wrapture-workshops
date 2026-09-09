---
title: A strict stub
requires: [verify:strict-stub]
---

# A strict stub

Stubbing a return value is the bread and butter of both tools, and on
the surface there is nothing to choose between them. The mock version
is the first test in the file.

```{editor-highlight}
:path: test_orders.py
:match: def test_stub_with_mock
:duration: 4s
```

The wrapture version names the same method on the class and gives it
one behaviour. First add the imports the wrapture tests need, in place
of the existing import line.

```{editor-replace}
:id: add-imports
:path: test_orders.py
:match: from orders import Gateway, OrderService
import wrapture

from orders import Gateway, Ledger, Notifier, OrderService
```

Now add the stub test, and beside it a second test that makes a call
the real method would reject.

```{file-write}
:id: write-stub-tests
:path: test_orders.py
:mode: append
:open: true



def test_stub_with_wrapture():
    with wrapture.binding(Gateway, "charge").on_call.returns({"id": "stub", "amount": 0}):
        assert OrderService().place(500)["id"] == "stub"


def test_drifted_call_with_wrapture():
    with wrapture.binding(Gateway, "charge").on_call.returns({"id": "stub"}):
        with pytest.raises(TypeError):
            Gateway().charge(500, bogus=True)
```

```{execute}
:id: run-strict
:session: shell
:wait: prompt
pytest -q test_orders.py
```

Six pass. Look at the two drifted-call tests together. The mock only
checks a stubbed call against the real signature if you asked for
`autospec=True`, so `charge(500, bogus=True)` returns the stub happily
and the test passes. A wrapture binding is strict by default: a call
that `returns()` would answer without reaching the real method is
checked against the method's signature first, and rejected as the real
call would reject it. The error names the site and the problem:

```
TypeError: orders:Gateway.charge (stubbed): got an unexpected keyword argument 'bogus'
```

A test that passes because the stub was more forgiving than the real
code is a test that will be wrong in production.

```{verify}
:id: strict-stub
:label: The wrapture stub answers, and rejects the drifted call
:substrate: shell
:trigger: after:run-strict
out=$(.venv/bin/python -m pytest -q --color=no test_orders.py -k "stub_with_wrapture or drifted_call_with_wrapture" 2>&1) && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: When a patch means to accept a different shape
`binding(Gateway, "charge", strict=False)` turns the signature check
off for that one binding. It is there for the rare patch that means
it, and the default is the direction that catches drift.
```
