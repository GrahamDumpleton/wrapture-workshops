---
title: The decorator form
requires: [verify:all-green]
---

# The decorator form

A binding declares a target without touching it, so the four bindings
in the error path test could be declared up front and read like a cast
list. For a test that binds its targets around its whole body there is
a decorator form that says the same thing without the nesting. The
bindings arrive as keyword arguments, and expectations declared on the
decorator are verified when the test finishes.

The decorators want a tape to record on. wrapture's pytest plugin
provides one as a fixture, sweeps for leaked patches after every test,
and attaches the tape's tree to any failure report. Turn it on from a
`conftest.py`.

```{file-write}
:id: write-conftest
:path: conftest.py
:open: true
pytest_plugins = ["wrapture.pytest_plugin"]
```

Now the error path test again, with the assertions moved to the top as
a contract and a body that only performs the action.

```{file-write}
:id: write-decorator-test
:path: test_orders.py
:mode: append
:open: true



@wrapture.bound(Ledger, "record").on_call.raises(OSError("disk full"))
@wrapture.bound(Gateway, "refund").expect_once()
@wrapture.bound(Notifier, "send").expect_never()
def test_error_path_with_decorators(tape, record, refund, send):
    with pytest.raises(OSError):
        OrderService().place(500)
```

Run the whole file.

```{execute}
:id: run-all
:session: shell
:wait: prompt
pytest -q test_orders.py
```

Ten pass: four with mock, six with wrapture. Each decorator names a
target and one phase of behaviour or an expectation, and the test
function receives the bindings by the target's name. An expectation
with nothing recording is an error rather than a silent pass.

```{verify}
:id: all-green
:label: All ten tests pass, with the plugin loaded
:substrate: shell
:trigger: after:run-all
out=$(.venv/bin/python -m pytest -q --color=no test_orders.py 2>&1) && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: The leak sweep
A patch that leaks changes the behaviour of every test that runs after
it. With the plugin loaded, a test that leaves a binding applied fails
by name, and the binding is removed so the tests after it are
unaffected. Try it: add a test that calls `apply()` on a binding and
never removes it.
```
