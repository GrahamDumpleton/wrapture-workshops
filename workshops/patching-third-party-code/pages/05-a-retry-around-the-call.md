---
title: A retry around the call
requires: [verify:retried-once]
---

# A retry around the call

Adding a retry needs control of the whole call: run it, catch one
kind of failure, run it again. `decorates()` takes a function with
wrapt's wrapper signature and makes it the centre of the pipeline.
The tenant transform still wraps around it, because `transforms_*`
stages compose while `decorates()` replaces only the terminal stage.
The `DropsFirst` transport raises on its first call, so the retry has
something to do.

```{file-write}
:id: write-retry
:path: retry.py
:open: true
import wrapture

from tenant import with_tenant
from transports import DropsFirst
from vendored_client import Client


def retry_once(wrapped, instance, args, kwargs):
    try:
        return wrapped(*args, **kwargs)
    except ConnectionError:
        return wrapped(*args, **kwargs)


request = wrapture.binding(Client, "request")
request.on_call.transforms_args(with_tenant).decorates(retry_once)
request.apply()
print(request.explain())

flaky = Client("https://api.example", DropsFirst())
print(flaky.request("GET", "/orders"))
print("transport calls:", flaky.transport.calls)
```

```{execute}
:id: run-retry
:session: shell
:wait: prompt
python retry.py
```

```
on_call  transforms args: with_tenant
         decorates: retry_once
{'method': 'GET', 'url': 'https://api.example/orders', 'headers': {'X-Tenant': 'acme'}, 'timeout': 30}
transport calls: 2
```

The first attempt raised, the second went through, and the caller saw
one successful request with the tenant header on it. The same function
could carry a `@wrapt.decorator` in production code; `decorates()`
takes it undecorated.

```{verify}
:id: retried-once
:label: The dropped connection was retried inside the patch
:substrate: shell
:trigger: after:run-retry
out=$(.venv/bin/python retry.py 2>&1) && printf '%s\n' "$out" | grep -q 'decorates: retry_once' && printf '%s\n' "$out" | grep -q "'X-Tenant': 'acme'" && printf '%s\n' "$out" | grep -q '^transport calls: 2$' && { echo "Two transport calls, one result, tenant header intact"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check expects `explain()` to list `retry_once` as the decorator,
a successful result with the tenant header, and exactly two transport
calls. A `ConnectionError` traceback means the decorator is not in
the pipeline.
```
