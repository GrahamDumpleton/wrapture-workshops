---
title: Testing the class
requires: [verify:class-tests-pass]
---

# Testing the class

Testability is a deliberate property of the shape. A package's own
tests construct the class, call `apply()` with a trigger name and the
imported module, and call `remove()` afterwards, with none of
wrapture's hook machinery involved; these are the same base-class
methods wrapture's own dispatch calls, so the two paths cannot
drift apart. Constructing the class runs the settings validation, so
a test can assert that a bad setting is refused, with the same
messages the config gave.

For the whole path through wrapture, `wrapture.instrumentation()`
scopes an application of the class to a block, the form the Flask
tests used, taking the class itself or the reference string the
config would, and its settings as keyword arguments. Triggers already
imported apply on entry, and the plugin's `tape` fixture catches what
the bindings record. A test of an application running under the
instrumentation reaches the bindings a hook applied through
`find_binding()`, by location or label, and gets the real one; once
the scope has ended the lookup is a `NoBindingError` rather than a
stale handle.

```{file-write}
:id: write-tests
:path: test_hookline_support.py
:open: true
import pytest
import wrapture

import hookline.client
from wrapture_local.hookline_support import HooklineInstrumentation

pytest_plugins = ["wrapture.pytest_plugin"]

URL = "https://acme.example/hooks"


def test_deliveries_are_external_leaves(tape):
    instrumentation = HooklineInstrumentation()
    instrumentation.apply("hookline.client", hookline.client)
    try:
        hookline.client.Client().deliver(URL, {"order": 1})
    finally:
        instrumentation.remove("hookline.client", hookline.client)

    delivery = tape.where(category="external").assert_once()[0]
    assert delivery.path == "hookline.client:Client.deliver"
    tape.where(label="hookline:connect").assert_never()


def test_a_bad_setting_is_refused():
    with pytest.raises(wrapture.ConfigError, match="unknown settings \\['internal'\\]"):
        HooklineInstrumentation(internal=True)

    with pytest.raises(wrapture.ConfigError, match="expects a boolean"):
        HooklineInstrumentation(internals="yes")


def test_the_whole_path_through_wrapture(tape):
    with wrapture.instrumentation(HooklineInstrumentation, internals=True):
        deliver = wrapture.find_binding(hookline.client.Client, "deliver")
        hookline.client.Client().deliver(URL, {"order": 1})
        deliver.events.assert_once()

    with pytest.raises(wrapture.NoBindingError):
        wrapture.find_binding(hookline.client.Client, "deliver")

    assert [event.label or event.path for event in tape.all] == [
        "hookline.client:Client.deliver",
        "hookline:connect",
        "hookline:write",
    ]
```

```{execute}
:id: run-tests
:session: shell
:wait: prompt
pytest -q test_hookline_support.py
```

Three pass. The first applied one trigger by hand and removed it in
a `finally`, which is the shape for testing a hook in isolation; the
third applied the whole class through wrapture, found the binding
the hook made, and saw it gone on exit; an event shows under its
label when it has one and its path otherwise, which is what the
tape's own output and `where()` use. Removal restores each patched
location and deactivates the wrapper, so a copy of it the library
took by from-import while the instrumentation was applied goes quiet
rather than recording on. The plugin's leak sweep would fail a test
that applied a binding and forgot to remove it, and the cleanup
callbacks are what keep this class out of that report.

```{verify}
:id: class-tests-pass
:label: The three tests of the class pass
:substrate: shell
:trigger: after:run-tests
out=$(.venv/bin/python -m pytest -q --color=no test_hookline_support.py 2>&1) && printf '%s\n' "$out" | grep -q '3 passed' && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check runs the tests with the venv's own interpreter and
expects three passes. A `ConfigError` about a trigger the class does
not declare means the name passed to `apply()` is not
`hookline.client`; a `NoBindingError` inside the scope means the
hook did not fire, which happens when `hookline.client` was not yet
imported and no import followed; a leak failure means a
`remove()` was skipped.
```
