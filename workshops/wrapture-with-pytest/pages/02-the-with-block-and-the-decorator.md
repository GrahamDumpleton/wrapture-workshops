---
title: The with-block and the decorator
requires: [verify:scoping-passes]
---

# The with-block and the decorator

The simplest pattern, and the right default for a patch needed in
exactly one test, is the with-block: applied on entry, removed on
exit, including when the body raises. For a test that binds one or two
statically addressable targets around its whole body, `bound()` says
the same thing without the nesting level. It takes the same addressing
arguments as `binding()` and mirrors its fluent chain, and the binding
it builds arrives in the test as a keyword argument named after the
slot, the way a fixture would. `taped()` opens a timeline around the
call and injects the tape.

```{file-write}
:id: write-scoping
:path: test_scoping.py
:open: true
import pytest
import wrapture

from shop import Gateway, Ledger, OrderService

CARD = "4111-1111-1111-1111"


def test_charge_is_stubbed():
    with wrapture.binding(Gateway, "charge").on_call.returns({"id": "stub", "amount": 0}):
        assert OrderService().place(500, CARD, tenant="acme")["id"] == "stub"


@wrapture.taped()
@wrapture.bound(Gateway, "charge").on_call.raises(TimeoutError("down"))
@wrapture.bound(Ledger, "record").expect_never()
def test_failed_charge_never_reaches_the_ledger(tape, charge, record):
    with pytest.raises(TimeoutError):
        OrderService().place(500, CARD, tenant="acme")

    charge.events.assert_once()
    assert len(tape.all) == 1


@wrapture.bound(Gateway, "charge")
def test_one_owner_per_binding(charge):
    with pytest.raises(wrapture.AlreadyAppliedError):
        with charge:
            pass
```

```{execute}
:id: run-scoping
:session: shell
:wait: prompt
pytest -q test_scoping.py
```

Three pass. Read a stack of decorators as a top-to-bottom sequence of
statements about the test below, not as nested wrappers. Each call of
the test constructs a fresh binding, so every parametrize case gets a
clean history, and removal is owned by the decorator, so it cannot be
forgotten. The expectation on `record` rides the chain and is verified
when the decorator removes the binding after a passing body; with
nothing recording it would be a loud error rather than a silent pass.

The third test is the rule the rest of the workshop follows: one owner
for each binding's lifecycle. The decorator applied `charge`, so
entering it again as a context manager raises `AlreadyAppliedError`
rather than letting the inner scope remove the outer scope's patch.
Whoever owns a binding, the test only reconfigures it through the
handle it was given, and never applies, removes or enters it itself.

```{verify}
:id: scoping-passes
:label: The three scoping tests pass
:substrate: shell
:trigger: after:run-scoping
out=$(.venv/bin/python -m pytest -q --color=no test_scoping.py 2>&1) && printf '%s\n' "$out" | grep -q '3 passed' && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: What the chain does not carry
The chain carries one phase's worth of behaviour: stages plus at most
one terminal per channel. `then()` and `advance()` are deliberately
not part of it; how behaviour changes over time is the test's script,
and it is configured in the body through the injected handle, where
the phase markers can be named. A target born inside the test body,
or a recording that must start partway through, keeps the with-block.
```
