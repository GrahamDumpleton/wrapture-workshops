---
title: One entry
requires: [verify:server-up, verify:four-trees]
---

# One entry

The Flask knowledge lives in an instrumentation package rather than in
the config. With wrapture-instrumentation installed alongside
wrapture, the config gains a single `[[instrument]]` entry naming
Flask, and keeps the observe entries for the shop's own methods from
the previous workshop. The printer shows each request as it arrives,
and a JSON Lines sink beside it keeps the trace, which is what the
checks on these pages read.

```{file-write}
:id: write-config
:path: wrapture.toml
:open: true
[[instrument]]
name = "flask"

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

[[sink]]
type = "printer"

[[sink]]
type = "jsonlines"
path = "trace.jsonl"
```

The development server runs under the runner exactly as a script did,
with everything after `-m flask` belonging to Flask. It keeps the
terminal on the left until it is stopped.

```{execute}
:id: start-server
:session: shell
:title: Start the development server under the runner
:wait: 3s
python -m wrapture -m flask --app webshop run --port {{ server_port }}
```

```{hint}
:title: If the port is already in use
The shop listens on port {{ server_port }}, which is the workshop
variable `server_port`. If starting it fails because another program has
that port, open the Variables dialog with the gear button in the panel
header, set `server_port` to a free port, and run the start action again.
The commands and checks on these pages follow the new value.
```

```{verify}
:id: server-up
:label: The server answers on port {{ server_port }}
:substrate: shell
:trigger: after:start-server
curl -sf -o /dev/null http://127.0.0.1:{{ server_port }}/health && echo "The server answers on port {{ server_port }}"
```

That check sent a request to `/health` to see that the server was up,
and the server printed a tree for it: the request line, the `health`
view beneath it, and the status when the body closed. Now, from the
terminal on the right, a quote, an order, a declined order and the
item that does not exist.

```{execute}
:id: curl-quote
:session: client
:wait: prompt
curl http://127.0.0.1:{{ server_port }}/quote/widget
```

```{execute}
:id: curl-order
:session: client
:wait: prompt
curl -X POST -H 'Content-Type: application/json' -d '{"amount": 500, "card": "4111-1111-1111-1111", "tenant": "acme"}' http://127.0.0.1:{{ server_port }}/order
```

```{execute}
:id: curl-declined
:session: client
:wait: prompt
curl -X POST -H 'Content-Type: application/json' -d '{"amount": 250, "card": "4000-0000-0000-0000", "tenant": "globex"}' http://127.0.0.1:{{ server_port }}/order
```

```{execute}
:id: curl-missing
:session: client
:wait: prompt
curl http://127.0.0.1:{{ server_port }}/quote/missing
```

In the server's terminal, interleaved with Flask's own access log
lines, each request arrives as one tree. The quote:

```
GET /quote/widget (webshop.wsgi_app)
  quote(item='widget')
    flask:render_template(template_name_or_list='quote.html', context='<context>')
    flask:render_template -> '<17 chars>' [1.5ms]
  quote -> '<p>widget: 25</p>' [1.6ms]
webshop.wsgi_app -> '200 OK' [2.3ms, body 5us over 1 chunk]
```

The request line opens the tree, the view sits beneath it labelled by
its endpoint, the template render sits beneath the view with the
template's name and its context masked, and the closing line carries
the status as the request's result along with the time to the last
byte of the body. The order, with the shop's own methods nesting
beneath the view because their bindings fire while the request is in
flight:

```
POST /order (webshop.wsgi_app)
  order()
    shop:OrderService.place(amount=500, card='<redacted>', tenant='acme')
      shop:Gateway.charge(amount=500, card='<redacted>')
      shop:Gateway.charge -> {'id': 'ch_500', 'amount': 500} [7us]
      shop:Ledger.record(entry="<dict {'id': 'ch_500', 'amount': 500}>")
      shop:Ledger.record -> 'led_ch_500' [4us]
    shop:OrderService.place -> {'id': 'ch_500', 'amount': 500} [205us]
  order -> '<Response 29 bytes [200 OK]>' [471us]
webshop.wsgi_app -> '200 OK' [922us, body 4us over 1 chunk]
```

The declined card, where the view caught the exception and answered
402, so the failure is on the gateway and the service but not on the
request. And the one this workshop wanted:

```
GET /quote/missing (webshop.wsgi_app)
  quote(item='missing')
  quote !! KeyError [4us]
webshop.wsgi_app -> '500 INTERNAL SERVER ERROR' !! KeyError [3.2ms, body 6us over 1 chunk]
```

The request line says two things at once. It answered 500, and the
`KeyError` was the reason. That second half is the part a reader would
not guess, because as far as the WSGI middleware recording the request
is concerned, the application returned normally. Flask caught the
exception on its way out of the view and handed it to
`handle_exception`, which built the 500 response and returned it, so
the request completed with a status and no exception. The only place
the failure can be seen is inside that handler, where the exception
arrives as an argument, and that is where the instrumentation looks. A
binding on `handle_exception` notes the exception against the nearest
enclosing request event, with the same `note_exception()` a test uses
for a failure the code handled itself, aimed past the handler's own
call with `current_event(kind="request")`. The view's event carries
the `KeyError` as the exception that escaped it, the request's event
carries it as a note, and both show on their lines because two scopes
failed for the same reason.

```{verify}
:id: four-trees
:label: Four requests recorded as four trees, the 500 with its KeyError
:substrate: shell
:trigger: after:curl-missing
out=$(.venv/bin/python -c "import wrapture; r = wrapture.load_events('trace.jsonl'); requests = [(x['data']['path'], x['result']) for x in r if x['kind'] == 'request']; want = [('/quote/widget', '200 OK'), ('/order', '200 OK'), ('/order', '402 PAYMENT REQUIRED'), ('/quote/missing', '500 INTERNAL SERVER ERROR')]; missing = [w for w in want if w not in requests]; assert not missing, f'no request event yet for {missing}: send the requests from the client terminal'; failed = [x for x in r if x['kind'] == 'request' and x['result'].startswith('500')]; assert any(c['type'] == 'KeyError' for x in failed for c in x.get('caught', [])), 'the 500 request carries no noted KeyError'; assert any(x['path'] == 'shop:Ledger.record' and x['depth'] == 3 for x in r), 'no ledger write nested beneath a request, a view and place'; print('Four requests as four trees: 200, 200, 402, and 500 with its KeyError noted on the request')" 2>&1) && { printf '%s\n' "$out"; exit 0; }; printf '%s\n' "$out" | tail -n 1; exit 1
```

```{hint}
:title: If the check fails
The check reads `trace.jsonl`, which the second `[[sink]]` entry
writes as requests complete, and looks for the four request events
with their statuses, a noted `KeyError` on the 500, and a ledger
write three levels beneath a request. A missing file means the server
is not running under the runner, or the config has no `jsonlines`
sink; a missing request means its `curl` did not reach the server.
```

The next page changes the config, and the server reads it only at
startup, so stop it now. The action sends Ctrl-C to the server's
terminal.

```{interrupt}
:id: stop-server
:session: shell
:title: Stop the server
```
