---
title: Fixtures and shared declarations
requires: [verify:fixtures-pass]
---

# Fixtures and shared declarations

A yield fixture gives the same guarantee as the with-block with reuse
across tests, and because the fixture yields the binding, a test can
reconfigure it in flight: a failure for the first call, a recovery
for the second. The fixture stays function scoped, the pytest
default; a session or module scoped fixture would leave the patch
applied across every test in between, which is the leak the fixture
exists to prevent.

Creating a binding does not patch, so a declaration can also live at
module scope and be shared, with each test applying and removing it.
Two things follow. Behaviour persists across apply and remove cycles,
so a stub configured in one test is still configured when the next
test applies the same binding, and the next test either configures
what it needs or clears the channel with `reset()`. And a shared
binding can be applied once at a time, which also makes it unsafe
under a parallel runner with two workers patching the same target in
one process.

```{file-write}
:id: write-fixtures
:path: test_fixtures.py
:open: true
import pytest
import wrapture

from shop import Gateway, Ledger, OrderService

CARD = "4111-1111-1111-1111"


@pytest.fixture
def stub_charge():
    with wrapture.binding(Gateway, "charge").on_call.returns({"id": "stub", "amount": 0}) as stub:
        yield stub


def test_order_uses_stub(stub_charge):
    assert OrderService().place(500, CARD, tenant="acme")["id"] == "stub"


def test_gateway_recovers(stub_charge):
    stub_charge.on_call.raises(TimeoutError("down"))
    with pytest.raises(TimeoutError):
        OrderService().place(500, CARD, tenant="acme")

    stub_charge.on_call.returns({"id": "retry", "amount": 0})
    assert OrderService().place(500, CARD, tenant="acme")["id"] == "retry"


record = wrapture.binding(Ledger, "record")


def test_ledger_write_fails():
    record.on_call.raises(OSError("disk full"))
    with record:
        with pytest.raises(OSError):
            OrderService().place(500, CARD, tenant="acme")


def test_ledger_write_succeeds():
    record.on_call.reset()
    with record:
        assert OrderService().place(500, CARD, tenant="acme")["id"] == "ch_500"
```

```{execute}
:id: run-fixtures
:session: shell
:wait: prompt
pytest -q test_fixtures.py
```

Four pass. The second test reconfigured the fixture's binding twice
without touching its lifecycle, and the fourth cleared the failure the
third had configured on the shared declaration before applying it.

```{verify}
:id: fixtures-pass
:label: The four fixture tests pass
:substrate: shell
:trigger: after:run-fixtures
out=$(.venv/bin/python -m pytest -q --color=no test_fixtures.py 2>&1) && printf '%s\n' "$out" | grep -q '4 passed' && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: See the behaviour persist
Delete the `record.on_call.reset()` line and run the file again. The
last test now fails with the `OSError` the test before it configured,
because `remove()` restores the target but keeps the behaviour. Put
the line back before moving on.
```
