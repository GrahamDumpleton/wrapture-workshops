---
title: Reconfiguring the live patch
requires: [verify:tenant-switched]
---

# Reconfiguring the live patch

Behaviour can be changed while the wrapper is installed, without
removing and re-applying it. Composing stages such as
`transforms_args()` accumulate in the order added, so switching the
tenant means dropping the current pipeline with `passes_through()`
and setting the new one. The patch itself never leaves the method,
and `explain()` says what the binding is set up to do at any moment.

```{file-write}
:id: write-reconfigure
:path: reconfigure.py
:open: true
import wrapture

from tenant import with_tenant
from transports import echo
from vendored_client import Client


def with_other_tenant(args, kwargs):
    headers = {**(kwargs.get("headers") or {}), "X-Tenant": "globex"}
    return args, {**kwargs, "headers": headers}


client = Client("https://api.example", echo)

request = wrapture.binding(Client, "request")
request.on_call.transforms_args(with_tenant)
request.apply()
print(client.request("GET", "/orders"))

request.on_call.passes_through().transforms_args(with_other_tenant)
print(client.request("GET", "/orders"))
print(request.explain())
```

```{execute}
:id: run-reconfigure
:session: shell
:wait: prompt
python reconfigure.py
```

```
{'method': 'GET', 'url': 'https://api.example/orders', 'headers': {'X-Tenant': 'acme'}, 'timeout': 30}
{'method': 'GET', 'url': 'https://api.example/orders', 'headers': {'X-Tenant': 'globex'}, 'timeout': 30}
on_call  transforms args: with_other_tenant
```

One stage in the pipeline, the new one. If calls may be in flight on
other threads while you reconfigure, `suspend()` first, reconfigure,
then `resume()`, so no call sees a half-built pipeline.

```{verify}
:id: tenant-switched
:label: The live patch now sends the other tenant, and only that
:substrate: shell
:trigger: after:run-reconfigure
out=$(.venv/bin/python reconfigure.py 2>&1) && printf '%s\n' "$out" | sed -n 1p | grep -q "'X-Tenant': 'acme'" && printf '%s\n' "$out" | sed -n 2p | grep -q "'X-Tenant': 'globex'" && printf '%s\n' "$out" | grep -q 'transforms args: with_other_tenant' && ! printf '%s\n' "$out" | grep -q 'transforms args: with_tenant$' && { echo "acme, then globex, with one transform left in the pipeline"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check expects the first request to carry `acme`, the second
`globex`, and `explain()` to list `with_other_tenant` alone. If both
tenants' transforms are listed, `passes_through()` is missing before
the second `transforms_args()`.
```
