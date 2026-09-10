---
title: Slow for whom
requires: [verify:server-up-tagged, verify:tagged]
---

# Slow for whom

An endpoint is often slow for one tenant, one account or one request
id, and the middleware cannot know which header carries that.
`annotate()` merges values into an in-flight event's data, and it is
unconditionally safe to call, doing nothing when nothing is recording,
which makes it reasonable to leave in application code permanently. In
the shop a `before_request` hook is the natural place, since the
request event is already open by the time it runs. This is the one
edit to the application in the whole tracing series.

One detail decides where the tag lands. The instrumentation observes
lifecycle callbacks, so by the time the hook's body runs the innermost
event in flight is the hook's own, and the bare `wrapture.annotate()`
would tag that. `current_event(kind="request")` aims past it at the
nearest enclosing request event, the same aiming the instrumentation
uses to note a caught exception against the request.

```{editor-replace}
:id: import-wrapture
:path: webshop.py
:match: from flask import Flask, jsonify, render_template, request
from flask import Flask, jsonify, render_template, request

import wrapture
```

```{editor-replace}
:id: add-hook
:path: webshop.py
:match: service = OrderService()
service = OrderService()


@app.before_request
def tag_tenant():
    wrapture.current_event(kind="request").annotate(tenant=request.headers.get("X-Tenant"))
```

Start the server again and send the same thirty requests; each order
in `traffic.py` already carries an `X-Tenant` header.

```{execute}
:id: restart-tagged
:session: shell
:title: Start the server again with the tenant hook
:wait: 3s
rm -f trace.jsonl stats.txt && python -m wrapture -m flask --app webshop run --port 5072
```

```{verify}
:id: server-up-tagged
:label: The server answers on port 5072 with the hook in place
:substrate: shell
:trigger: after:restart-tagged
curl -sf -o /dev/null http://127.0.0.1:5072/health && echo "The server answers on port 5072"
```

```{execute}
:id: send-tagged-traffic
:session: client
:wait: prompt
python3 traffic.py
```

The tag rides on the request event, so it is in the JSON Lines file
beside everything else, and the slow requests can be sliced by who
they were for. The hook itself appears in each tree too, as
`webshop:tag_tenant`, directly beneath the request line.

```{file-write}
:id: write-by-tenant
:path: by_tenant.py
:open: true
import wrapture

for record in wrapture.load_events("trace.jsonl"):
    if record["kind"] == "request" and record["data"].get("tenant"):
        print(record["data"]["tenant"], record["data"]["path"], f"{record['duration'] * 1000:.1f}ms")
```

```{execute}
:id: run-by-tenant
:session: client
:wait: prompt
.venv/bin/python by_tenant.py
```

```
acme /order 35.7ms
globex /order 1.1ms
acme /order 32.5ms
globex /order 1.0ms
...
```

The other tenant's orders were all declined at the gateway and never
reached the ledger, so they sit around a millisecond. The same
expression selects the request to assert on in a test, through
`events.matching()`, and a `Filter` around a printer narrows the live
view to one tenant's requests.

```{verify}
:id: tagged
:label: Every order carries its tenant, and only acme's are slow
:substrate: shell
:trigger: after:run-by-tenant
out=$(.venv/bin/python -c "import wrapture; r = wrapture.load_events('trace.jsonl'); orders = [x for x in r if x['kind'] == 'request' and x['data']['path'] == '/order']; assert orders, 'no order requests on the trace yet: run traffic.py from the client terminal'; untagged = [x for x in orders if not x['data'].get('tenant')]; assert not untagged, f'{len(untagged)} order requests carry no tenant: the before_request hook is missing, or the server was not restarted'; acme = [x['duration'] for x in orders if x['data']['tenant'] == 'acme']; globex = [x['duration'] for x in orders if x['data']['tenant'] == 'globex']; assert acme and globex, 'orders for only one tenant reached the server'; assert min(acme) > 0.025 and max(globex) < 0.02, f'acme fastest {min(acme) * 1000:.1f}ms, globex slowest {max(globex) * 1000:.1f}ms'; print(f'{len(acme)} acme orders, slowest {max(acme) * 1000:.1f}ms; {len(globex)} globex orders, slowest {max(globex) * 1000:.1f}ms')" 2>&1) && { printf '%s\n' "$out"; exit 0; }; printf '%s\n' "$out" | tail -n 1; exit 1
```

```{hint}
:title: If the check fails
The check reads the request events for `/order` in `trace.jsonl` and
expects a `tenant` tag on each, with every acme order slower than
25ms and every globex order under 20ms. Untagged orders mean the hook
is not in `webshop.py`, the server is still running the old code, or
the hook calls the bare `annotate()`, which tags the hook's own event
rather than the request; stop the server with Ctrl-C and start it
again.
```

Stop the server before finishing.

```{interrupt}
:id: stop-server-tagged
:session: shell
:title: Stop the server
```
