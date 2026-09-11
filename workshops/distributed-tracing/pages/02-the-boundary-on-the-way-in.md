---
title: The boundary on the way in
requires: [verify:server-up, verify:minted-at-the-boundary]
---

# The boundary on the way in

The server's config wraps the WSGI application in the recording
middleware with `mode = "wsgi"` and observes the helper beneath it.
The middleware is where a distributed identity arrives: a request
carrying a `traceparent` header joins the caller's trace rather than
minting, its `tracestate` rides along untouched, and a request with
no recognised headers mints as any root does. A printer shows each
request as a tree in the server's terminal, and a JSON Lines sink
keeps the events with the id on every line, which is what the checks
read.

```{file-write}
:id: write-server-config
:path: server.toml
:open: true
[[observe]]
target = "backend"
name = "app"
mode = "wsgi"

[[observe]]
target = "backend"
name = "quote"

[[sink]]
type = "printer"

[[sink]]
type = "jsonlines"
path = "server.jsonl"
```

Start the quote service under the runner, in the terminal on the
left. It keeps that terminal until it is stopped.

```{execute}
:id: start-server
:session: shell
:title: Start the quote service under the runner
:wait: 3s
rm -f server.jsonl && python -m wrapture --config server.toml server.py
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
:id: server-up
:label: The quote service answers on port {{ quote_port }}
:substrate: shell
:trigger: after:start-server
curl -sf http://127.0.0.1:{{ quote_port }}/quote/widget && echo "The quote service answers on port {{ quote_port }}"
```

That request came from the check, with no `traceparent` header, so
the service minted an identity of its own for it at the boundary. The
tree printed in the server's terminal does not show the id, but the
line in `server.jsonl` does, under `trace`.

```{execute}
:id: show-minted
:session: client
:title: Read the trace id off the request the check sent
:wait: prompt
.venv/bin/python -c "import wrapture; [print(r['path'], r['trace']['w3c']['trace_id']) for r in wrapture.load_events('server.jsonl')]"
```

```
backend:quote 0b2ad016e1f0a5c8f7d3b9a2c4e6d8f0
backend:app 0b2ad016e1f0a5c8f7d3b9a2c4e6d8f0
```

Both events of the tree carry the same id: the request minted it,
and the helper call beneath it inherited it.

```{verify}
:id: minted-at-the-boundary
:label: The request that arrived with no header minted a trace id shared by its whole tree
:substrate: shell
:trigger: after:show-minted
out=$(.venv/bin/python -c "import wrapture; records = wrapture.load_events('server.jsonl'); requests = [r for r in records if r['kind'] == 'request']; assert requests, 'no request event in server.jsonl yet: is the service running under the runner with server.toml?'; ids = {r['trace']['w3c']['trace_id'] for r in records}; assert len(ids) == len(requests), f'{len(ids)} trace ids for {len(requests)} requests: the helper call did not inherit its request identity'; print(f'{len(requests)} request(s), each with one trace id shared by its tree')" 2>&1) && { printf '%s\n' "$out"; exit 0; }; printf '%s\n' "$out" | tail -n 1; exit 1
```

```{hint}
:title: If the check fails
The check reads `server.jsonl` and expects every record to carry a
trace id, one id per request tree. No file means the service is not
running under the runner with `server.toml`; a record without a
`trace` key means the identity mechanism has been switched off with
a `[trace]` table, which this config does not have.
```

Leave the service running: the client on the next page talks to it.
