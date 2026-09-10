---
title: One table
requires: [verify:server-up, verify:spans-exported]
---

# One table

Export is switched on by a top-level `[otel]` table in the same config
file the Flask shop has been using. The presence of the table opts in,
a service name identifies the process, and each signal's tuning nests
beneath it. Three settings here are for the workshop's benefit. The
metrics export interval is shortened so the next page does not wait a
minute for a data point. `exceptions = "message"` sends the type and
message of an exception but not its stack trace, so the spans stay
readable in a terminal. And the environment table sets a default for
one of the SDK's own variables, the delay before the batch processor
sends the spans it holds, which is how a config file carries settings
the SDK reads from the environment; a variable set in the real
environment still wins.

```{file-write}
:id: write-config
:path: wrapture.toml
:open: true
[otel]
service_name = "webshop"
exceptions = "message"

[otel.metrics]
export_interval = 2

[otel.environment]
bsp_schedule_delay = 1000

[[instrument]]
name = "flask"
ignore_paths = ["/health"]

[[observe]]
target = "shop:OrderService"
name = "place"
redact = ["card"]

[[observe]]
target = "shop:Gateway"
name = "charge"
redact = ["card"]

[[observe]]
target = "shop:Ledger"
name = "record"
```

Where the spans go is decided by the standard OpenTelemetry
environment variables, so with a collector listening on the usual port
nothing more is needed. For a look without a collector, the console
exporters print the spans and the metrics to standard output instead.
The server's output is also copied to `spans.log` through `tee`, which
is what the checks read; its `-i` keeps `tee` alive through the Ctrl-C
that stops the server, so the spans flushed at exit reach the file
too.

```{execute}
:id: start-server
:session: shell
:title: Start the server under the runner with the console exporters
:wait: 3s
OTEL_TRACES_EXPORTER=console OTEL_METRICS_EXPORTER=console python -m wrapture -m flask --app webshop run --port 5073 | tee -i spans.log
```

```{verify}
:id: server-up
:label: The server answers on port 5073
:substrate: shell
:trigger: after:start-server
curl -sf -o /dev/null http://127.0.0.1:5073/health && echo "The server answers on port 5073"
```

Now the same four requests as in the earlier workshops, from the
terminal on the right: a quote, an order, a declined order, and the
item that is not in the catalog.

```{execute}
:id: curl-quote
:session: client
:wait: prompt
curl http://127.0.0.1:5073/quote/widget
```

```{execute}
:id: curl-order
:session: client
:wait: prompt
curl -X POST -H 'Content-Type: application/json' -d '{"amount": 500, "card": "4111-1111-1111-1111", "tenant": "acme"}' http://127.0.0.1:5073/order
```

```{execute}
:id: curl-declined
:session: client
:wait: prompt
curl -X POST -H 'Content-Type: application/json' -d '{"amount": 250, "card": "4000-0000-0000-0000", "tenant": "globex"}' http://127.0.0.1:5073/order
```

```{execute}
:id: curl-missing
:session: client
:wait: prompt
curl http://127.0.0.1:5073/quote/missing
```

One event becomes one span. A request becomes a SERVER span, a call or
a block becomes an INTERNAL span beneath it, and the tree the printer
drew in the earlier workshops is the tree the backend receives. Each
span is printed as a JSON document when its batch is sent, a second or
so after the request, so the server's terminal fills up quickly.
`spans.py` reads the file back and prints one line per span, indented
by parent; the command waits a couple of seconds first, so the last
batch has been sent.

```{execute}
:id: run-spans
:session: client
:title: Wait for the last batch, then read the spans back
:wait: prompt
sleep 2; .venv/bin/python spans.py
```

```
    INTERNAL 'flask:render_template'
  INTERNAL 'quote'
SERVER 'GET /quote/<item>'
      INTERNAL 'shop:Gateway.charge'
      INTERNAL 'shop:Ledger.record'
    INTERNAL 'shop:OrderService.place'
  INTERNAL 'order'
SERVER 'POST /order'
      INTERNAL 'shop:Gateway.charge' ERROR CardDeclined
    INTERNAL 'shop:OrderService.place' ERROR CardDeclined
  INTERNAL 'order'
SERVER 'POST /order'
  INTERNAL 'quote' ERROR KeyError
SERVER 'GET /quote/<item>' ERROR KeyError
```

Children print before their parents because a span is exported when
it closes, and the request closes last. For the quote of an item that
is not in the catalog, the view's span arrives with error status and
the exception recorded on it. Trimmed to the parts that matter, from
the server's terminal:

```
{
    "name": "quote",
    "context": {
        "trace_id": "0x02f1fd262a7817d4f8b42fb0f6a30db3",
        "span_id": "0x5b94b62db087bbc9"
    },
    "kind": "SpanKind.INTERNAL",
    "parent_id": "0xfba0a55ab3a322f0",
    "status": {
        "status_code": "ERROR",
        "description": "KeyError"
    },
    "attributes": {
        "wrapture.path": "webshop:quote",
        "wrapture.kind": "call",
        "wrapture.arg.item": "missing"
    },
    "events": [
        {
            "name": "exception",
            "attributes": {
                "exception.type": "KeyError",
                "exception.message": "'missing'",
                "exception.escaped": "True"
            }
        }
    ]
}
```

And the request span it is parented under:

```
{
    "name": "GET /quote/<item>",
    "context": {
        "trace_id": "0x02f1fd262a7817d4f8b42fb0f6a30db3",
        "span_id": "0xfba0a55ab3a322f0"
    },
    "kind": "SpanKind.SERVER",
    "parent_id": null,
    "status": {
        "status_code": "ERROR"
    },
    "attributes": {
        "http.request.method": "GET",
        "url.path": "/quote/missing",
        "http.route": "/quote/<item>",
        "http.response.status_code": 500,
        "wrapture.data.endpoint": "quote",
        "wrapture.data.remote": "127.0.0.1"
    },
    "events": [
        {
            "name": "exception",
            "attributes": {
                "exception.type": "KeyError",
                "exception.message": "'missing'",
                "exception.escaped": "False"
            }
        }
    ]
}
```

A few things in there are worth pointing at. The request span is named
`GET /quote/<item>`, by the route pattern rather than the URL, because
the Flask instrumentation annotates the request with its matched route
once routing has run, and the exporter reads that as the
semantic-convention `http.route`. A backend then groups by endpoint
rather than seeing every URL as a distinct operation. The captured
arguments and anything added with `annotate()` become span attributes
under `wrapture.arg.*` and `wrapture.data.*`, with the card number
already redacted before it got anywhere near the exporter. And the
`KeyError` appears on both spans, once as the exception that escaped
the view and once as the one noted against the request after Flask
caught it, so the request span shows the 500, the error status and
the reason together rather than a status with no explanation.

```{verify}
:id: spans-exported
:label: The failed request is a SERVER span named by its route, in error with its KeyError, with the view span beneath it
:substrate: shell
:trigger: after:run-spans
out=$(.venv/bin/python -c "import spans; s = spans.spans(); assert s, 'no spans in spans.log yet: send the four requests from the client terminal and wait a second'; failed = [x for x in s if x['name'] == 'GET /quote/<item>' and x['status']['status_code'] == 'ERROR']; assert failed, 'no request span named GET /quote/<item> with error status yet: the request for /quote/missing has not been exported'; request = failed[-1]; assert any(e['attributes']['exception.type'] == 'KeyError' for e in request['events']), 'the failed request span carries no KeyError event'; views = [x for x in s if x['name'] == 'quote' and x['parent_id'] == request['context']['span_id']]; assert views and views[0]['status']['status_code'] == 'ERROR', 'no quote span in error beneath the failed request span'; places = [x for x in s if x['name'] == 'shop:OrderService.place']; assert places and all(x['attributes'].get('wrapture.arg.card') == '<redacted>' for x in places), 'the place spans do not carry the card argument redacted'; print(f'{len(s)} spans exported; the failed request is a SERVER span named by its route, in error with its KeyError, and the quote span sits beneath it')" 2>&1) && { printf '%s\n' "$out"; exit 0; }; printf '%s\n' "$out" | tail -n 1; exit 1
```

```{hint}
:title: If the check fails
The check reads `spans.log`, the copy of the server's output that
`tee` writes, and looks for the request span for `/quote/missing`
with error status and a `KeyError` event, the `quote` span beneath
it, and the redacted card on the `place` spans. No spans at all means
the server was started without the console exporter variables or
without `tee`; a missing request means its `curl` did not reach the
server, or its batch has not been sent yet, so wait a second and
check again.
```

Leave the server running: the next page reads the metrics it is
exporting from the same requests.
