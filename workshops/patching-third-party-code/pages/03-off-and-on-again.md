---
title: Off and on again
requires: [verify:patch-reversible]
---

# Off and on again

The patch stays visible as an object whose state can be queried at any
time. `applied` says whether you installed it, and `active` inspects
the target on every access, so if some other code replaced
`Client.request` wholesale the binding would say so.

`suspend()` makes the wrapper inert without removing it. This is the
safe way to switch a patch off in a live process: the wrapper keeps
its place in the chain, so it can be toggled while other parties have
wrapped the same method, and calls that pass through while suspended
are counted. `remove()` uninstalls the wrapper and restores the
original exactly. In between, the script bypasses the patch for one
call through the wrapt handle underneath.

```{file-write}
:id: write-lifecycle
:path: lifecycle.py
:open: true
import wrapture

from tenant import with_tenant
from transports import echo
from vendored_client import Client

client = Client("https://api.example", echo)

request = wrapture.binding(Client, "request")
request.on_call.transforms_args(with_tenant)
request.apply()
print(request.applied, request.active, request.suspended)

request.suspend()
print(request)
print(client.request("GET", "/orders"))
print("calls while suspended:", request.suspended_calls)

request.resume()
print(request)
print(client.request("GET", "/orders"))

print("bypassing the patch:", request.wrapper.__wrapped__(client, "GET", "/health"))

request.remove()
print(request)
print(client.request("GET", "/orders"))
```

```{execute}
:id: run-lifecycle
:session: shell
:wait: prompt
python lifecycle.py
```

```
True True False
<Binding 'vendored_client:Client.request' callable active suspended configured>
{'method': 'GET', 'url': 'https://api.example/orders', 'headers': {}, 'timeout': 30}
calls while suspended: 1
<Binding 'vendored_client:Client.request' callable active configured>
{'method': 'GET', 'url': 'https://api.example/orders', 'headers': {'X-Tenant': 'acme'}, 'timeout': 30}
bypassing the patch: {'method': 'GET', 'url': 'https://api.example/health', 'headers': {}, 'timeout': 30}
<Binding 'vendored_client:Client.request' callable unapplied configured>
{'method': 'GET', 'url': 'https://api.example/orders', 'headers': {}, 'timeout': 30}
```

While applied, the binding exposes its `wrapt.FunctionWrapper` as
`wrapper`, and the original function is that wrapper's `__wrapped__`,
so a call that must skip the patch entirely is a direct call to it.
`target` and `name` are the patch coordinates; anything core wrapt
can do with those three remains reachable, and if code outside
wrapture removes the wrapper behind your back, the repr changes to
`displaced` rather than pretending. After `remove()` the class is
exactly as it was, and the binding is back to `unapplied`, ready to
be applied again.

```{verify}
:id: patch-reversible
:label: The patch was suspended, resumed, bypassed and removed
:substrate: shell
:trigger: after:run-lifecycle
out=$(.venv/bin/python lifecycle.py 2>&1) && printf '%s\n' "$out" | sed -n 2p | grep -q 'active suspended configured' && printf '%s\n' "$out" | grep -q '^calls while suspended: 1$' && printf '%s\n' "$out" | grep -q "^bypassing the patch: {'method': 'GET', 'url': 'https://api.example/health', 'headers': {}" && printf '%s\n' "$out" | sed -n 8p | grep -q 'unapplied configured' && [ "$(printf '%s\n' "$out" | tail -n 1)" = "{'method': 'GET', 'url': 'https://api.example/orders', 'headers': {}, 'timeout': 30}" ] && { echo "Suspended with one call counted, resumed, bypassed once, and removed cleanly"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check runs `lifecycle.py` and reads the binding's repr after
`suspend()` and after `remove()`, the suspended call count, the
bypassed `/health` request without a tenant header, and a bare final
request. What it printed is the message above.
```
