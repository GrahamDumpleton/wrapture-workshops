---
title: The identity on the way out
requires: [verify:one-id-across-both]
---

# The identity on the way out

On the way out, instrumentation injects the identity into outbound
traffic. The client's config observes the order flow, and its
`[[instrument]]` entry names an `Instrumentation` class that ships
with this workshop in {open}`wrapture_local/urllib_support.py`, the
stand-in for what a urllib instrumentation package would provide.
Its hook binds the opener's choke point, so every outbound request
records as a call and carries the current tree's id in its
`traceparent` header. The `pythonpath` key makes the package next to
the config importable, anchored to the config file's own directory.

```{file-write}
:id: write-client-config
:path: client.toml
:open: true
pythonpath = "."

[[observe]]
target = "frontend"
match = "*"

[[instrument]]
name = "wrapture_local.urllib_support:UrllibInstrumentation"

[[sink]]
type = "printer"

[[sink]]
type = "jsonlines"
path = "client.jsonl"
```

Now the client, from the terminal on the right: three orders, the
last for an item the service does not know.

```{execute}
:id: run-client
:session: client
:title: Place three orders under the runner
:wait: prompt
rm -f client.jsonl && .venv/bin/python -m wrapture --config client.toml client.py
```

```
frontend:place_order(item='widget')
  frontend:fetch_quote(item='widget')
    block: request-quote
      urllib.open(fullurl='http://127.0.0.1:5076/quote/widget', data=None, timeout='<object object at 0x103fb07a0>')
      urllib.open -> '<http.client.HTTPResponse object at 0x104b78670>' [2.9ms]
    request-quote [17.2ms]
    block: consume-reply
    consume-reply [77us]
  frontend:fetch_quote -> "<dict {'item': 'widget', 'price': 25}>" [18.0ms]
frontend:place_order -> 'widget: 25' [18.1ms]
...
widget: 25
gadget: 120
missing: no quote (404)
```

Each order is one tree here, and in the terminal on the left each
request printed as one tree there, at the moment the client's
`urllib.open` line was in flight. The join needs no backend at all.
`join.py` prints the first eight characters of the trace id from
every record in both files, with the file it came from, sorted, so
each order's two halves sit together.

```{execute}
:id: run-join
:session: client
:wait: prompt
.venv/bin/python join.py
```

```
0b2ad016 server.jsonl backend:app
0b2ad016 server.jsonl backend:quote
93063c99 client.jsonl frontend:fetch_quote
93063c99 client.jsonl frontend:fetch_quote
93063c99 client.jsonl frontend:place_order
93063c99 client.jsonl urllib.request:OpenerDirector.open
93063c99 server.jsonl backend:app
93063c99 server.jsonl backend:quote
f3e1f697 client.jsonl frontend:fetch_quote
f3e1f697 client.jsonl frontend:fetch_quote
f3e1f697 client.jsonl frontend:fetch_quote
f3e1f697 client.jsonl frontend:place_order
f3e1f697 client.jsonl urllib.request:OpenerDirector.open
f3e1f697 server.jsonl backend:app
f3e1f697 server.jsonl backend:quote
...
```

Each order is one id across both files, client half and server half
of one distributed trace. The repeated `fetch_quote` lines are the
two blocks the client marks inside that function, which record under
its path, and the server-only pair at the top is the previous page's
request, which arrived with no header. The order for the missing
item has one block fewer, because `urlopen()` raised before
`consume-reply` was entered, and its server half answered 404.

```{verify}
:id: one-id-across-both
:label: Every trace the client minted continues in the server's file
:substrate: shell
:trigger: after:run-join
out=$(.venv/bin/python -c "import wrapture; client = wrapture.load_events('client.jsonl'); server = wrapture.load_events('server.jsonl'); ids = lambda records: {r['trace']['w3c']['trace_id'] for r in records if 'trace' in r}; minted = ids(client); assert len(minted) == 3, f'{len(minted)} trace ids in client.jsonl, not one per order: run client.py from the client terminal'; assert 'urllib.request:OpenerDirector.open' in {r['path'] for r in client}, 'no urllib request events in client.jsonl: client.toml has no [[instrument]] entry for the local class'; joined = minted & ids(server); assert joined == minted, f'{len(minted - joined)} of the client trace ids never reached server.jsonl: the traceparent header was not sent, or not parsed at the boundary'; print(f'{len(minted)} orders, {len(minted)} trace ids, each in both files; the server minted {len(ids(server) - minted)} of its own for requests that arrived with no header')" 2>&1) && { printf '%s\n' "$out"; exit 0; }; printf '%s\n' "$out" | tail -n 1; exit 1
```

```{hint}
:title: If the check fails
The check collects the trace ids from `client.jsonl` and expects each
of the three to appear in `server.jsonl` too. Missing ids mean the
quote service is not running under the runner with `server.toml`, so
the header was never parsed, or the client ran without `client.toml`,
so it was never sent. No urllib events at all means the
`[[instrument]]` entry or the `pythonpath` line is missing.
```
