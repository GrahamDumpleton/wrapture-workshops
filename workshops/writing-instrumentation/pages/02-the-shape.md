---
title: The shape
requires: [verify:deliveries-recorded]
---

# The shape

One class per target, subclassing `wrapture.Instrumentation`, with
class data for everything static and one decorated hook method per
trigger module. `target` is the import path of the module tree the
class covers, and every trigger a hook declares must live at or under
it: wrapture refuses a class claiming a module outside its target the
moment the class is defined, and two enabled entries whose targets
overlap are a config error, which is what stops one module being
patched twice. `removable = True` is the class's claim that it can
undo itself, false by default, so say it. `settings` declares every
key an `[[instrument]]` entry may carry, each a `Setting(default,
description)`; the next pages use them.

The hook is the door. It is called as `method(self, name, module)`
when its trigger module is imported, or at once if it already was,
with the module object in hand, so the class never imports the
library itself. Inside it, build the bindings against the module
handed in, apply them, and register the undo with `on_cleanup()`.
The deliveries are declared as what they are: `leaf=True` makes each
one a terminal node, so the library's own connect and write steps
stay out of the tree unless a setting asks for them, and
`category="external"` says what kind of operation it is, one of the
words a tracing backend and the OpenTelemetry export understand.
The headers a delivery sends can carry a signature, so they are
redacted unless a setting asks for them too.

```{directory-create}
:id: create-local
:path: wrapture_local
```

```{file-write}
:id: write-package
:path: wrapture_local/__init__.py
"""Operator code reached only by the reference in wrapture.toml."""
```

```{file-write}
:id: write-support
:path: wrapture_local/hookline_support.py
:open: true
import wrapture


class HooklineInstrumentation(wrapture.Instrumentation):
    """Delivery and dispatch tracing for hookline."""

    target = "hookline"
    removable = True
    settings = {
        "headers": wrapture.Setting(False, "record the headers sent with each delivery"),
        "internals": wrapture.Setting(False, "record the connect and write steps beneath each delivery"),
    }

    @wrapture.instrumentation_hook("hookline.client")
    def client(self, name, module):
        policy = None if self.settings["headers"] else wrapture.redact("headers")

        deliver = wrapture.binding(
            module.Client,
            "deliver",
            leaf=not self.settings["internals"],
            category="external",
            capture_args=policy,
        )
        connect = wrapture.binding(module.Client, "_connect", label="hookline:connect")
        write = wrapture.binding(module.Client, "_write", label="hookline:write", capture_args=policy)

        group = wrapture.bindings(deliver=deliver, connect=connect, write=write)
        group.apply()

        self.on_cleanup(group.remove)
```

The config names the class by reference, with `pythonpath` making
the package next to the file importable, anchored to the file's own
directory. A printer sink shows what the class records.

```{file-write}
:id: write-config
:path: wrapture.toml
:open: true
pythonpath = "."

[[instrument]]
name = "wrapture_local.hookline_support:HooklineInstrumentation"

[[sink]]
type = "printer"
```

```{execute}
:id: run-shape
:session: shell
:wait: prompt
python -m wrapture app.py
```

```
hookline.client:Client.deliver(url='https://acme.example/hooks', payload={'order': 42}, headers='<redacted>')
hookline.client:Client.deliver -> {'url': 'https://acme.example/hooks', 'status': 202, 'bytes': 13} [3.2ms]
hookline.client:Client.deliver(url='https://globex.example/down', payload={'order': 42}, headers='<redacted>')
hookline.client:Client.deliver !! DeliveryError [4.0ms]
delivery failed: https://globex.example/down: connection refused
emailed ann@example.com
None
failures: [('order.failed', ValueError('no handler for card declined'))]
```

Two deliveries, each a leaf with its headers masked, and nothing yet
from the dispatcher. The class was imported when the config loaded,
which is why its module must import only wrapture; the hook ran when
`app.py` imported `hookline`, which imported `hookline.client`; and
the bindings on the connect and write steps are applied but
silenced beneath the leaf, so they cost almost nothing.

```{verify}
:id: deliveries-recorded
:label: Each delivery records as an external leaf with its headers redacted
:substrate: shell
:trigger: after:run-shape
out=$(.venv/bin/python -m wrapture app.py 2>&1) && [ "$(printf '%s\n' "$out" | grep -c "^hookline.client:Client.deliver(url=.*headers='<redacted>')")" = 2 ] && printf '%s\n' "$out" | grep -q '^hookline.client:Client.deliver !! DeliveryError' && ! printf '%s\n' "$out" | grep -q 'hookline:connect' && { echo "Two deliveries recorded as leaves, headers redacted, one raising DeliveryError"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check runs `app.py` under the runner and expects two delivery
lines with `headers='<redacted>'`, a `!! DeliveryError` line, and no
`hookline:connect` line. No delivery lines means the config was not
found or the `pythonpath` line is missing; a connect line means the
leaf is off, because `internals` defaulted to true or `leaf=` was
left out; unmasked headers mean the capture policy is missing.
```
