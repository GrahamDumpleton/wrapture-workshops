---
title: One trace across two processes
requires: [verify:one-id-across-both, verify:remote-parent]
optional: true
---

# One trace across two processes

A trace within one process is only half of what a tracing backend is
for. The second pair of programs is two processes: {open}`client.py`
places orders through {open}`frontend.py`, which fetches quotes over
HTTP, and {open}`server.py` serves them from {open}`backend.py`, a
WSGI application with no framework at all. Both are observed by
wrapture from a config of their own, {open}`client.toml` and
{open}`server.toml`, and both write JSON Lines files beside the
printer.

Every tree wrapture records carries a W3C trace id, minted at its
root. On the client side, the `[[instrument]]` entry for
`urllib.request` records each outbound request and puts the current
tree's id into its `traceparent` header. On the server side,
`mode = "wsgi"` on the application wraps it in the recording
middleware, which parses the header at the boundary, so that
process's trees join the client's trace instead of minting their own.
Both configs also switch on `[otel]` for the traces signal.

Start the quote service in the terminal on the left, with the console
exporter and its output copied to a file as before.

```{execute}
:id: start-quote-service
:session: shell
:title: Start the quote service under the runner
:wait: 3s
rm -f server.jsonl && OTEL_TRACES_EXPORTER=console python -m wrapture --config server.toml server.py | tee -i server-spans.log
```

```{hint}
:title: If the port is already in use
The quote service listens on port {{ quote_port }}, which is the workshop
variable `quote_port`. If starting it fails because another program has
that port, open the Variables dialog with the gear button in the panel
header, set `quote_port` to a free port, and run the start action again.
The commands and checks on these pages follow the new value.
```

```{verify}
:id: quote-service-up
:label: The quote service answers on port {{ quote_port }}
:substrate: shell
:trigger: after:start-quote-service
curl -sf http://127.0.0.1:{{ quote_port }}/quote/widget && echo "The quote service answers on port {{ quote_port }}"
```

That request came from the check, with no `traceparent` header, so
the service minted an id of its own for it. Now the client, from the
terminal on the right: three orders, the last for an item the service
does not know.

```{execute}
:id: run-client
:session: client
:title: Place three orders under the runner
:wait: prompt
rm -f client.jsonl && OTEL_TRACES_EXPORTER=console .venv/bin/python -m wrapture --config client.toml client.py | tee -i client-spans.log
```

The join needs no backend at all. `join.py` prints the first eight
characters of the trace id from every record in both files, with the
file it came from.

```{execute}
:id: run-join
:session: client
:wait: prompt
.venv/bin/python join.py
```

```
0b2ad016 server.jsonl backend:app
0b2ad016 server.jsonl backend:quote
8f19b8c6 client.jsonl frontend:fetch_quote
8f19b8c6 client.jsonl frontend:fetch_quote
8f19b8c6 client.jsonl frontend:fetch_quote
8f19b8c6 client.jsonl frontend:place_order
8f19b8c6 client.jsonl urllib.request:OpenerDirector.open
8f19b8c6 server.jsonl backend:app
8f19b8c6 server.jsonl backend:quote
b1a416b0 client.jsonl frontend:fetch_quote
...
```

Each order is one id across both files, client half and server half
of one distributed trace. The repeated `fetch_quote` lines are the two
blocks the client marks inside that function, which record under its
path, and the server-only pair at the top is the check's request,
which arrived with no header and minted an id of its own at the
boundary. The whole public surface the client instrumentation needed
for this was `wrapture.trace_headers()`, which returns the pairs an
outbound message made right now should carry, and is empty when
nothing is being recorded, so injecting it is always safe.

```{verify}
:id: one-id-across-both
:label: Every trace the client minted continues in the server's file
:substrate: shell
:trigger: after:run-join
out=$(.venv/bin/python -c "import wrapture; client = wrapture.load_events('client.jsonl'); server = wrapture.load_events('server.jsonl'); ids = lambda records: {r['trace']['w3c']['trace_id'] for r in records if 'trace' in r}; minted = ids(client); assert len(minted) == 3, f'{len(minted)} trace ids in client.jsonl, not one per order: run client.py from the client terminal'; assert 'urllib.request:OpenerDirector.open' in {r['path'] for r in client}, 'no urllib request events in client.jsonl: client.toml has no [[instrument]] entry for urllib.request'; joined = minted & ids(server); assert joined == minted, f'{len(minted - joined)} of the client trace ids never reached server.jsonl: the traceparent header was not parsed at the boundary'; print(f'{len(minted)} orders, {len(minted)} trace ids, each in both files; the server minted {len(ids(server) - minted)} of its own for the request that arrived with no header')" 2>&1) && { printf '%s\n' "$out"; exit 0; }; printf '%s\n' "$out" | tail -n 1; exit 1
```

```{hint}
:title: If the check fails
The check collects the trace ids from `client.jsonl` and expects each
of the three to appear in `server.jsonl` too. Missing ids mean the
quote service is not running under the runner with `server.toml`, so
the header was never parsed, or the client ran without `client.toml`,
so it was never sent.
```

Switching on `[otel]` in both processes changes nothing about the
ids. The exporter claims the identity wrapture minted rather than
minting one of its own, so the JSON Lines files, the outbound headers
and the exported spans all read the same trace id, and the server's
request span is created with the arrived identity as a remote parent.
In the console output in the server's terminal, the `GET /quote/widget`
span carries the client's trace id and names the client's
`urllib.request:OpenerDirector.open` span as its parent:

```
{
    "name": "GET /quote/widget",
    "context": {
        "trace_id": "0xcdde803e61b96f52e2eb3820c7004df0",
        "span_id": "0x9bb64b3bad9a6848"
    },
    "kind": "SpanKind.SERVER",
    "parent_id": "0x670e42eb0ac7690a",
    ...
}
```

And in the client's terminal, the span that made the request:

```
{
    "name": "urllib.request:OpenerDirector.open",
    "context": {
        "trace_id": "0xcdde803e61b96f52e2eb3820c7004df0",
        "span_id": "0x670e42eb0ac7690a"
    },
    "kind": "SpanKind.CLIENT",
    "parent_id": "0x0e06d5674120b1db",
    ...
}
```

In a viewer, each order is one distributed trace with the service's
request span attached beneath the outbound call that made it. One
invariant governs the header handling, and it is what makes this safe
to switch on in a service that sits between other people's systems:
never break a trace you do not understand. A header wrapture parses
but nothing claims is forwarded verbatim, so an upstream product sees
this service as a transparent hop, and headers wrapture does not parse
are never touched at all.

```{verify}
:id: remote-parent
:label: Each server request span is parented under the client span that made the request
:substrate: shell
:trigger: after:run-join
out=$(.venv/bin/python -c "import spans; client = spans.spans('client-spans.log'); server = spans.spans('server-spans.log'); opens = {x['context']['span_id']: x for x in client if x['name'] == 'urllib.request:OpenerDirector.open'}; assert len(opens) == 3, f'{len(opens)} urllib spans in client-spans.log, not three: run client.py with the console exporter'; requests = [x for x in server if x['kind'] == 'SpanKind.SERVER']; joined = [x for x in requests if x['parent_id'] in opens]; assert len(joined) == 3, f'{len(joined)} of the server request spans name a client span as their parent; the rest have not been exported yet, or arrived with no header'; assert all(x['context']['trace_id'] == opens[x['parent_id']]['context']['trace_id'] for x in joined), 'a server request span names a client parent from a different trace'; print('Three server request spans, each in the client trace and parented under the urllib span that made the request')" 2>&1) && { printf '%s\n' "$out"; exit 0; }; printf '%s\n' "$out" | tail -n 1; exit 1
```

```{hint}
:title: If the check fails
The check reads the two console logs and expects the three server
request spans to name, as their parent, a `urllib.request` span from
the client's log with the same trace id. The server's spans are sent
a second after each request, so check again if the count is short;
no client spans at all means the client ran without
`OTEL_TRACES_EXPORTER=console` or without `tee`.
```

Stop the quote service before finishing.

```{interrupt}
:id: stop-quote-service
:session: shell
:title: Stop the quote service
```
