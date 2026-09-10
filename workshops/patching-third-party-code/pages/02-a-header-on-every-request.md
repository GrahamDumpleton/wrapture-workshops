---
title: A header on every request
requires: [verify:header-injected]
---

# A header on every request

A binding names the method and holds behaviour for it.
`transforms_args()` receives the call as the caller made it, as
`(args, kwargs)`, and returns what the real method should receive.
The transform lives in a module of its own, since later pages reuse
it.

```{file-write}
:id: write-tenant
:path: tenant.py
:open: true
def with_tenant(args, kwargs):
    headers = {**(kwargs.get("headers") or {}), "X-Tenant": "acme"}
    return args, {**kwargs, "headers": headers}
```

The script prints the binding and a request before and after
`apply()`.

```{file-write}
:id: write-header
:path: header.py
:open: true
import wrapture

from tenant import with_tenant
from transports import echo
from vendored_client import Client

client = Client("https://api.example", echo)

request = wrapture.binding(Client, "request")
request.on_call.transforms_args(with_tenant)
print(request)
print(client.request("GET", "/orders"))

request.apply()
print(request)
print(client.request("GET", "/orders"))
print(client.request("GET", "/orders", headers={"Accept": "text/csv"}))
```

```{execute}
:id: run-header
:session: shell
:wait: prompt
python header.py
```

```
<Binding 'vendored_client:Client.request' callable unapplied configured>
{'method': 'GET', 'url': 'https://api.example/orders', 'headers': {}, 'timeout': 30}
<Binding 'vendored_client:Client.request' callable active configured>
{'method': 'GET', 'url': 'https://api.example/orders', 'headers': {'X-Tenant': 'acme'}, 'timeout': 30}
{'method': 'GET', 'url': 'https://api.example/orders', 'headers': {'Accept': 'text/csv', 'X-Tenant': 'acme'}, 'timeout': 30}
```

Creating and configuring the binding patched nothing: the first repr
says `unapplied`, and the first request went out bare. After
`apply()` every call through the class picks up the header, merged
with whatever the caller passed. The real `request()` still runs;
only the `headers` keyword is different by the time it does, and the
library's own signature was never re-declared anywhere.

```{verify}
:id: header-injected
:label: The header appears only once the binding is applied
:substrate: shell
:trigger: after:run-header
out=$(.venv/bin/python header.py 2>&1) && [ "$(printf '%s\n' "$out" | sed -n 2p)" = "{'method': 'GET', 'url': 'https://api.example/orders', 'headers': {}, 'timeout': 30}" ] && printf '%s\n' "$out" | sed -n 3p | grep -q 'active configured' && [ "$(printf '%s\n' "$out" | grep -c "'X-Tenant': 'acme'")" -eq 2 ] && printf '%s\n' "$out" | grep -q "'Accept': 'text/csv', 'X-Tenant': 'acme'" && { echo "One bare request, then two with the tenant header"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check runs `header.py` and expects the second line to be a
request with empty headers, the third to show the binding `active`,
and the two requests after `apply()` to carry `X-Tenant`. What it
printed is the message above. `tenant.py` must define `with_tenant`
exactly as written.
```
