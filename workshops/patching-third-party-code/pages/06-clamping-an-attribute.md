---
title: Clamping an attribute
requires: [verify:timeout-clamped]
---

# Clamping an attribute

`Client.request` reads `self.timeout`, a plain class attribute. There
is no method to wrap for that, but an attribute binding intercepts the
read itself. On `apply()` it installs a descriptor on the class over
the existing default, and `on_get.transforms()` rewrites every value
an instance reads through it, whether the class default or an
instance override. Used as a context manager, it is a scoped clamp.

```{file-write}
:id: write-clamp
:path: clamp.py
:open: true
import wrapture

from transports import echo
from vendored_client import Client

client = Client("https://api.example", echo)

timeout = wrapture.binding(Client, "timeout")
print(timeout)
timeout.on_get.transforms(lambda value: min(value, 5))

with timeout:
    client.timeout = 120
    print(client.request("GET", "/orders"))

del client.timeout
print(client.request("GET", "/orders"))
```

```{execute}
:id: run-clamp
:session: shell
:wait: prompt
python clamp.py
```

```
<Binding 'vendored_client:Client.timeout' attribute unapplied>
{'method': 'GET', 'url': 'https://api.example/orders', 'headers': {}, 'timeout': 5}
{'method': 'GET', 'url': 'https://api.example/orders', 'headers': {}, 'timeout': 30}
```

The mode was detected from what was found at the target: `timeout` is
plain data, so the binding is in attribute mode and offers `on_get`,
`on_set` and `on_delete` instead of `on_call`. Inside the block even
an instance override of 120 was read as 5; outside it the class
default is back. One limit shapes where this applies: attribute
bindings intercept access through instances, so a library reading
`Client.timeout` off the class would not be affected.

```{verify}
:id: timeout-clamped
:label: The timeout read as 5 inside the block and 30 outside it
:substrate: shell
:trigger: after:run-clamp
out=$(.venv/bin/python clamp.py 2>&1) && printf '%s\n' "$out" | sed -n 1p | grep -q "attribute unapplied" && printf '%s\n' "$out" | sed -n 2p | grep -q "'timeout': 5}" && printf '%s\n' "$out" | sed -n 3p | grep -q "'timeout': 30}" && { echo "Attribute binding: 5 inside the block, 30 after it"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check expects the binding's repr to say `attribute`, the request
inside the block to show `'timeout': 5`, and the one after it to show
`'timeout': 30`. The transform must be on `on_get`, not `on_call`.
```
