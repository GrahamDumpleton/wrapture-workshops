---
title: The leak sweep
requires: [verify:leak-named, verify:leak-fixed]
---

# The leak sweep

Here is the mistake the scoping styles exist to prevent: a test that
applies a binding and never removes it. Nothing about the test itself
fails. The stub stays on the class, and the next test, which expects
the real gateway, is the one that breaks.

```{file-write}
:id: write-leak
:path: test_leak.py
:open: true
import wrapture

from shop import Gateway, OrderService

CARD = "4111-1111-1111-1111"


def test_leaves_a_binding_applied():
    wrapture.binding(Gateway, "charge").on_call.returns({"id": "leaked", "amount": 0}).apply()
    assert OrderService().place(500, CARD, tenant="acme")["id"] == "leaked"


def test_the_next_test_sees_the_real_gateway():
    assert OrderService().place(500, CARD, tenant="acme")["id"] == "ch_500"
```

```{execute}
:id: run-leak
:session: shell
:wait: prompt
pytest -q test_leak.py
```

One passes and one fails, and it is the wrong one: the second test
reports `'leaked' == 'ch_500'` and nothing points at the first. In a
suite of hundreds the culprit could be in another file entirely.

wrapture ships a pytest plugin for exactly this. It is deliberately
not auto-loaded; activate it from a `conftest.py`.

```{file-write}
:id: write-conftest
:path: conftest.py
:open: true
pytest_plugins = ["wrapture.pytest_plugin"]
```

```{execute}
:id: run-leak-again
:session: shell
:wait: prompt
pytest -q test_leak.py
```

Now both bodies pass, and the first test errors at teardown, by name,
with the binding it left behind. The binding is removed, which is why
the second test sees the real gateway this time:

```
wrapture: bindings left applied after the test: shop:Gateway.charge (removed now, so later tests are unaffected)
```

The sweep only flags bindings applied during the test. A module or
session scoped fixture that deliberately holds a patch across tests is
respected, because its binding was already applied when each test
began.

```{verify}
:id: leak-named
:label: The sweep names the leaking test and the next test passes
:substrate: shell
:trigger: after:run-leak-again
out=$(.venv/bin/python -m pytest -q --color=no test_leak.py 2>&1); printf '%s\n' "$out" | grep -q 'bindings left applied after the test: shop:Gateway.charge' && printf '%s\n' "$out" | grep -q '2 passed, 1 error' && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check runs `test_leak.py` and expects two passes and one error at
teardown naming `shop:Gateway.charge`. Two passes and no error mean
the leaking test has already been fixed; one pass and one failure
mean the plugin is not loaded, so check that `conftest.py` is in this
directory with the `pytest_plugins` line.
```

The fix is any of the styles from the earlier pages. Give the
binding an owner with the with-block, and run the file once more.

```{editor-replace}
:id: fix-leak
:path: test_leak.py
:regex: true
:match: ^    wrapture\.binding\(Gateway, "charge"\)\.on_call\.returns\(\{"id": "leaked", "amount": 0\}\)\.apply\(\)\n    assert (.*)$
:expand: true
    with wrapture.binding(Gateway, "charge").on_call.returns({"id": "leaked", "amount": 0}):
        assert $1
```

```{execute}
:id: run-leak-fixed
:session: shell
:wait: prompt
pytest -q test_leak.py
```

```{verify}
:id: leak-fixed
:label: Both tests pass with the binding scoped
:substrate: shell
:trigger: after:run-leak-fixed; file-saved test_leak.py
out=$(.venv/bin/python -m pytest -q --color=no test_leak.py 2>&1) && printf '%s\n' "$out" | grep -q '2 passed' && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; exit 1
```
