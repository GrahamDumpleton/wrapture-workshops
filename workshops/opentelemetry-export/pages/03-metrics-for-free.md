---
title: Metrics for free
requires: [verify:metrics-exported]
---

# Metrics for free

The traces signal exports events individually. The metrics signal
aggregates the same events instead, and both have been on since the
server started, because the default is all signals. Request durations
go into the semantic-convention `http.server.request.duration`
histogram, attributed by method, route and status code, and observed
calls go into a per-path `wrapture.call.duration` histogram whose
error series split out by exception type.

The config set the export interval to two seconds, and each export
prints one large JSON document with every histogram in it in the
server's terminal. The command waits out one interval, so the last
export is one made after the four requests, and `spans.py metrics`
then picks the attribute sets out of it, with the count of operations
behind each.

```{execute}
:id: run-metrics
:session: client
:title: Wait one export interval, then read the last export
:wait: prompt
sleep 3; .venv/bin/python spans.py metrics
```

```
http.server.request.duration: 4 data points
    1 {"http.request.method": "GET", "http.route": "/quote/<item>", "http.response.status_code": 200}
    1 {"http.request.method": "POST", "http.route": "/order", "http.response.status_code": 200}
    1 {"http.request.method": "POST", "http.route": "/order", "http.response.status_code": 402}
    1 {"http.request.method": "GET", "http.route": "/quote/<item>", "http.response.status_code": 500, "error.type": "KeyError"}
wrapture.call.duration: 9 data points
    1 {"wrapture.path": "flask:render_template"}
    1 {"wrapture.path": "webshop:quote"}
    1 {"wrapture.path": "shop:Gateway.charge"}
    1 {"wrapture.path": "shop:Ledger.record"}
    1 {"wrapture.path": "shop:OrderService.place"}
    2 {"wrapture.path": "webshop:order"}
    1 {"wrapture.path": "shop:Gateway.charge", "error.type": "CardDeclined"}
    1 {"wrapture.path": "shop:OrderService.place", "error.type": "CardDeclined"}
    1 {"wrapture.path": "webshop:quote", "error.type": "KeyError"}
```

So per-endpoint latency and error rate read straight off the
histogram with no code involved. The reason the bound path is safe as
a metric attribute where a raw URL would not be is that the config
chose the bindings, so the set of values is closed; requests are
attributed by route pattern for the same reason, never by URL. The
design is the `Aggregate` collector from the previous workshop with
the aggregation handed to the SDK: bounded memory, no values captured,
nothing retained.

```{verify}
:id: metrics-exported
:label: The request histogram has a data point per route and status, the 500 with its error type
:substrate: shell
:trigger: after:run-metrics
out=$(.venv/bin/python -c "import spans; p = spans.histogram_points('http.server.request.duration'); assert p, 'no metrics export in spans.log yet: the exporter runs every two seconds, so wait and check again'; sets = [(x['attributes']['http.route'], x['attributes']['http.response.status_code'], x['attributes'].get('error.type')) for x in p]; want = [('/quote/<item>', 200, None), ('/order', 200, None), ('/order', 402, None), ('/quote/<item>', 500, 'KeyError')]; missing = [w for w in want if w not in sets]; assert not missing, f'no request data point yet for {missing}'; calls = spans.histogram_points('wrapture.call.duration'); assert any(x['attributes'].get('wrapture.path') == 'shop:Gateway.charge' and x['attributes'].get('error.type') == 'CardDeclined' for x in calls), 'no error series for the declined charge on wrapture.call.duration'; print(f'{len(p)} request data points by route and status, the 500 with its error type, and {len(calls)} call data points by path')" 2>&1) && { printf '%s\n' "$out"; exit 0; }; printf '%s\n' "$out" | tail -n 1; exit 1
```

```{hint}
:title: If the check fails
The check reads the last metrics export in `spans.log` and expects a
request data point for each of the four requests, attributed by route
and status, and an error series for the declined charge. No export
at all means the server was started without
`OTEL_METRICS_EXPORTER=console`; a missing data point means its
request was not sent, or the export since it was sent has not
happened yet.
```

The next page runs a different pair of programs, so stop the server.
The action sends Ctrl-C to its terminal; `tee` survives it and writes
the last spans and the final metrics export to the file before the
prompt comes back.

```{interrupt}
:id: stop-server
:session: shell
:title: Stop the server
```
