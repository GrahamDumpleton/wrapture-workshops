---
title: Welcome
requires: [verify:env-ready, verify:mock-suite-green]
---

# Converting a mock test suite

`unittest.mock` substitutes objects: a patched attribute becomes a
`Mock`, and the test asserts against what the `Mock` recorded.
wrapture defaults to the opposite strategy: wrap the real code and
intervene in flight, with call signatures checked, real return values
recorded, and order and nesting kept across everything observed. A
suite written with mock does not have to be rewritten in one go. Each
idiom has a spelling on the other side, and this workshop converts a
small module one test at a time, running the suite after each step so
it is green throughout.

The code under test is {open}`shop.py`, the order service from the
earlier workshops with a few things added for the tests to reach: the
gateway logs a warning when it declines a card, each charge carries
the currency named by the `SHOP_CURRENCY` environment variable, the
notifier delivers through a transport it is handed, and
`place_with_retry()` retries an order while the gateway times out.

The tests are in {open}`test_shop.py`, ten of them, written entirely
with `unittest.mock` and pytest's `monkeypatch` and `caplog`. Each
page converts one or two of them in place.

## An environment for the tests

wrapture is not installed in this JupyterLab, so make a virtual
environment in this directory and install wrapture and pytest into it.
The commands run in the workshop terminal, under the editor, which
stays activated for the rest of the workshop.

```{execute}
:id: create-venv
:session: shell
:title: Create and activate a virtual environment
:wait: prompt
python3 -m venv .venv && . .venv/bin/activate
```

```{execute}
:id: install-deps
:session: shell
:title: Install wrapture and pytest
:wait: prompt
pip install wrapture==1.0.0b1 pytest
```

```{verify}
:id: env-ready
:label: wrapture and pytest are installed in .venv
:substrate: shell
:trigger: after:install-deps
.venv/bin/python -c "import wrapture, pytest; print('wrapture', wrapture.__version__, 'and pytest', pytest.__version__)"
```

```{hint}
:title: If the check fails
The virtual environment must be at `.venv` in this directory, with
wrapture and pytest installed into it. Run the two commands above
again; creating the environment a second time does no harm.
```

Run the suite as it stands.

```{execute}
:id: run-mock-suite
:session: shell
:wait: prompt
pytest -q test_shop.py
```

Ten pass. That count is the invariant for the rest of the workshop:
every page replaces a test with its wrapture version, and the count
never drops.

```{verify}
:id: mock-suite-green
:label: The ten mock tests pass
:substrate: shell
:trigger: after:run-mock-suite
out=$(.venv/bin/python -m pytest -q --color=no test_shop.py 2>&1) && printf '%s\n' "$out" | grep -q '10 passed' && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; exit 1
```
