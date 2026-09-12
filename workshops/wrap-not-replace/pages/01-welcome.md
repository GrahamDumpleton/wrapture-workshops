---
title: Welcome
requires: [verify:env-ready]
---

# Testing by wrapping, not replacing

`unittest.mock` substitutes: a patched attribute becomes a `Mock`, and
the test asserts against what the `Mock` recorded. wrapture wraps: the
real code keeps running, and the binding intervenes in flight. This
workshop writes the same tests both ways and stops at the four places
where the difference changes what a test can say.

The code under test is {open}`orders.py`: an order service that
takes a payment through a gateway, records it in a ledger and sends a
notification. If the ledger write fails, the payment is
refunded and the error propagates. The payment step goes through a
private method on the service itself.

The tests are in `test_orders.py`. Four are already written, with
`unittest.mock`. You add the wrapture version of each as you go.

```{file-open}
:id: open-tests
:path: test_orders.py
```

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

Run the four mock tests to see them pass.

```{execute}
:id: run-mock-tests
:session: shell
:wait: prompt
pytest -q test_orders.py
```

All four pass. Keep an eye on `test_drifted_call_with_mock`: it passes,
and the next page says why it should not.

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
