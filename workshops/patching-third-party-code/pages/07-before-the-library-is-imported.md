---
title: Before the library is imported
requires: [verify:hook-fired]
---

# Before the library is imported

A binding resolves its target when created, so the module must
already be imported. wrapt's deferred form, a trailing `?` on the
module name that registers a post-import hook instead, is refused,
because a binding must hold the wrapper it applied in order to
remove, suspend and report on it.

What is supported is running the binding code from a post-import
hook. `wrapture.when_imported` registers a callback against a module
name; the callback runs with the module as its argument the moment
that module is first imported, or immediately if it already was. The
script registers the hook before it imports the client, and keeps the
applied binding in a module-level list so it can be removed later.

```{file-write}
:id: write-hook
:path: hook.py
:open: true
import sys

import wrapture

from tenant import with_tenant
from transports import echo

try:
    wrapture.binding("vendored_client?", "Client.request")
except wrapture.DeferredTargetError as exc:
    print("refused:", str(exc).split(":")[0])

installed = []


@wrapture.when_imported("vendored_client")
def install(module):
    request = wrapture.binding(module.Client, "request")
    request.on_call.transforms_args(with_tenant)
    installed.append(request.apply())


print("imported yet:", "vendored_client" in sys.modules, installed)

import vendored_client

print("imported yet:", "vendored_client" in sys.modules, installed)
print(vendored_client.Client("https://api.example", echo).request("GET", "/orders"))
```

```{execute}
:id: run-hook
:session: shell
:wait: prompt
python hook.py
```

```
refused: deferred patching is not supported
imported yet: False []
imported yet: True [<Binding 'vendored_client:Client.request' callable active configured>]
{'method': 'GET', 'url': 'https://api.example/orders', 'headers': {'X-Tenant': 'acme'}, 'timeout': 30}
```

The hook created the binding after the import it depends on, by
construction, and the patch was in place before any caller could
reach `request()`. Because it runs on the first import of that module
wherever that import happens, the application only has to register
the hook early, in its own package `__init__` or a startup module,
and no longer cares which of its modules imports the client first.
Registering after the module is already imported is harmless: the
hook simply runs at once.

```{verify}
:id: hook-fired
:label: The hook applied the patch on import, and the first request carried the header
:substrate: shell
:trigger: after:run-hook
out=$(.venv/bin/python hook.py 2>&1) && printf '%s\n' "$out" | grep -q '^refused: deferred patching is not supported' && printf '%s\n' "$out" | grep -q '^imported yet: False \[\]$' && printf '%s\n' "$out" | grep -q "^imported yet: True \[<Binding 'vendored_client:Client.request' callable active configured>\]$" && printf '%s\n' "$out" | tail -n 1 | grep -q "'X-Tenant': 'acme'" && { echo "Deferred form refused, hook fired on import, header on the first request"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
`hook.py` must not import `vendored_client` before the hook is
registered; `tenant` and `transports` are safe to import first since
neither imports the client. The check expects the list to be empty
before the import and to hold one active binding after it.
```
