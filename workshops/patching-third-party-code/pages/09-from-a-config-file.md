---
title: From a config file
requires: [verify:config-applies, verify:typo-refused, verify:config-restored]
---

# From a config file

Everything so far ran in a process that already had the library
imported and the patch code beside it. To install the header patch at
startup, without the application mentioning wrapture, put the binding
in an `Instrumentation` class next to a `wrapture.toml`. The
`pythonpath` key makes the companion code importable, anchored to the
config file's own directory, and any key on the `[[instrument]]`
entry other than `name` is one of the settings the class declares.

```{directory-create}
:id: create-local
:path: wrapture_local
```

```{file-write}
:id: write-patches
:path: wrapture_local/patches.py
:open: true
import wrapture


class ClientInstrumentation(wrapture.Instrumentation):
    """Stamp the tenant header on every vendored client request."""

    target = "vendored_client"
    removable = True
    settings = {"tenant": wrapture.Setting("", "the tenant to send")}

    @wrapture.instrumentation_hook("vendored_client")
    def client(self, name, module):
        tenant = self.settings["tenant"]

        def with_tenant(args, kwargs):
            headers = {**(kwargs.get("headers") or {}), "X-Tenant": tenant}
            return args, {**kwargs, "headers": headers}

        request = wrapture.binding(module.Client, "request")
        request.on_call.transforms_args(with_tenant)
        request.apply()

        self.on_cleanup(request.remove)
```

```{file-write}
:id: write-config
:path: wrapture.toml
:open: true
pythonpath = "."

[[instrument]]
name = "wrapture_local.patches:ClientInstrumentation"
tenant = "acme"
```

The hook receives the freshly imported `vendored_client` module, so
`module.Client` is the real class, and the module defining the class
imports only wrapture, so naming it from the config never causes the
library to be imported ahead of time. Registering the binding's
`remove()` with `on_cleanup()` is what puts the patch inside what the
config can undo.

Run the application through the launcher. `app.py` is unchanged from
the first page.

```{execute}
:id: run-config
:session: shell
:wait: prompt
python -m wrapture app.py
```

```
{'method': 'GET', 'url': 'https://api.example/orders', 'headers': {'X-Tenant': 'acme'}, 'timeout': 30}
```

```{verify}
:id: config-applies
:label: The launcher applied the header patch to the unchanged application
:substrate: shell
:trigger: after:run-config
out=$(.venv/bin/python -m wrapture app.py 2>&1) && printf '%s\n' "$out" | grep -q "'X-Tenant': 'acme'" && { echo "The header patch came from wrapture.toml"; exit 0; }; printf '%s\n' "$out"; exit 1
```

Because the class declares its settings, a typo in the file is an
error at load rather than a silently ignored key. Misspell the tenant
setting and run again.

```{editor-replace}
:id: break-config
:path: wrapture.toml
:match: tenant = "acme"
tenat = "acme"
```

```{execute}
:id: run-typo
:session: shell
:wait: prompt
python -m wrapture app.py
```

```
wrapture: instrument entry 'wrapture_local.patches:ClientInstrumentation': unknown settings ['tenat']; the declared settings are ['tenant']
```

```{verify}
:id: typo-refused
:label: The misspelt setting is refused when the config loads
:substrate: shell
:trigger: after:run-typo
out=$(.venv/bin/python -m wrapture app.py 2>&1); printf '%s\n' "$out" | grep -q "unknown settings \['tenat'\]; the declared settings are \['tenant'\]" && { echo "Refused at load: unknown setting tenat"; exit 0; }; printf '%s\n' "$out"; exit 1
```

Put the setting back and confirm the patch applies again.

```{editor-replace}
:id: restore-config
:path: wrapture.toml
:match: tenat = "acme"
tenant = "acme"
```

```{execute}
:id: run-restored
:session: shell
:wait: prompt
python -m wrapture app.py
```

Loading a config runs the code it names, so the trust boundary is
write access to the file. Without `--config`, `python -m wrapture`
looks in `WRAPTURE_CONFIG`, then `wrapture.toml` in the current
directory, then a `[tool.wrapture]` table in `pyproject.toml`. Where
the command line is not yours, autowrapt applies the same file at
interpreter startup, as the zero-code tracing workshop showed.

```{verify}
:id: config-restored
:label: The corrected config applies the patch again
:substrate: shell
:trigger: after:run-restored
out=$(.venv/bin/python -m wrapture app.py 2>&1) && printf '%s\n' "$out" | grep -q "'X-Tenant': 'acme'" && { echo "Back to a tenant header on every request"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If a check fails
`wrapture_local/patches.py` and `wrapture.toml` must both be in this
directory, and the config's `name` must point at
`wrapture_local.patches:ClientInstrumentation`. The second check
expects the file to say `tenat` and the third `tenant`; open
`wrapture.toml` to see which it says now.
```
