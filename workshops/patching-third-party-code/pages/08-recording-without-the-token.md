---
title: Recording without the token
requires: [verify:token-redacted]
---

# Recording without the token

An installed patch is also an observation point, and the honest way to
check what a library is doing is to listen. `request()` takes a bearer
token, so record it with a capture policy that redacts that parameter
by name. The token also comes back out inside the `Authorization`
header of the echoed result, so capture the result as a type name
only. A `Printer` sink shows each call as it happens.

```{file-write}
:id: write-audit
:path: audit.py
:open: true
import sys

import wrapture

from transports import echo
from vendored_client import Client

client = Client("https://api.example", echo)

audited = wrapture.binding(
    Client, "request",
    capture_args=wrapture.redact("token"),
    capture_result="types",
)
printer = wrapture.add_sink(wrapture.Printer(sys.stdout, timing=False))

with audited:
    client.request("GET", "/orders", token="s3cr3t")
    client.request("GET", "/orders", None, "s3cr3t")

wrapture.remove_sink(printer)
```

```{execute}
:id: run-audit
:session: shell
:wait: prompt
python audit.py
```

```
vendored_client:Client.request(method='GET', path='/orders', headers=None, token='<redacted>')
vendored_client:Client.request -> '<dict>'
vendored_client:Client.request(method='GET', path='/orders', headers=None, token='<redacted>')
vendored_client:Client.request -> '<dict>'
```

Redaction matches by parameter name against the normalised call, so
it covers the token however the caller spelt the argument, by keyword
or positionally. Everything not named is captured at the reference
level unless `redact(..., level=)` says otherwise. Behaviour and
capture policy live on the same binding, so the tenant transform and
the redaction can be one object.

```{verify}
:id: token-redacted
:label: Both calls are recorded with the token redacted and the result as a type
:substrate: shell
:trigger: after:run-audit
out=$(.venv/bin/python audit.py 2>&1) && [ "$(printf '%s\n' "$out" | grep -c "token='<redacted>'")" -eq 2 ] && [ "$(printf '%s\n' "$out" | grep -c -- "-> '<dict>'")" -eq 2 ] && ! printf '%s\n' "$out" | grep -q 's3cr3t' && { echo "Two calls traced, the token redacted in both, nothing of the result but its type"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check expects two opening lines with `token='<redacted>'`, two
closing lines with `'<dict>'`, and the string `s3cr3t` nowhere in the
output. The binding must be created with both `capture_args` and
`capture_result`.
```
