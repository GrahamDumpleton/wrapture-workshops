---
title: The tree with times on it
requires: [verify:server-up, verify:ledger-time]
---

# The tree with times on it

The config already prints an elapsed time on every closing line, so
the first order through the server is most of the answer. Start the
server under the runner, in the terminal on the left.

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

Place one order from the terminal on the right.

```{execute}
:id: curl-order
:session: client
:wait: prompt
curl -X POST -H 'Content-Type: application/json' -d '{"amount": 500, "card": "4111-1111-1111-1111", "tenant": "acme"}' http://127.0.0.1:{{ server_port }}/order
```

```
POST /order (webshop.wsgi_app)
  order()
    shop:OrderService.place(amount=500, card='<redacted>', tenant='acme')
      shop:Gateway.charge(amount=500, card='<redacted>')
      shop:Gateway.charge -> {'id': 'ch_500', 'amount': 500} [8us]
      shop:Ledger.record(entry="<dict {'id': 'ch_500', 'amount': 500}>")
      shop:Ledger.record -> 'led_ch_500' [35.1ms]
    shop:OrderService.place -> {'id': 'ch_500', 'amount': 500} [35.9ms]
  order -> '<Response 29 bytes [200 OK]>' [36.3ms]
webshop.wsgi_app -> '200 OK' [37.3ms, body 10us over 1 chunk]
```

Reading up from the bottom, the request took 37.3ms, the view 36.3ms,
the service 35.9ms, and the ledger 35.1ms, with the gateway at 8us.
The figures are from one run, and they vary, but the shape does not.
The ledger accounts for essentially all of the service, which accounts
for essentially all of the view. The service and the view are slow
because of what they call. The ledger is slow in its own right.

That distinction, slow itself versus slow because of a child, is the
one a wall-clock timer around the service call cannot express, and it
has a name. Self time is an operation's duration minus the time its
observed children account for, and wrapture computes it from the
parent links as events close. The next page turns it into an
assertion.

```{verify}
:id: ledger-time
:label: The ledger accounts for the order's time
:substrate: shell
:trigger: after:curl-order
out=$(.venv/bin/python -c "import wrapture; r = wrapture.load_events('trace.jsonl'); places = [x for x in r if x['path'] == 'shop:OrderService.place']; assert places, 'no place event on the trace yet: send the order from the client terminal'; place = places[-1]; record = next((x for x in r if x['path'] == 'shop:Ledger.record' and x['parent_id'] == place['seq']), None); assert record is not None, 'the last order has no ledger write beneath it'; assert record['duration'] >= 0.025, f'the ledger write took {record[\"duration\"] * 1000:.1f}ms, not the slow write this shop plants'; assert place['duration'] - record['duration'] < 0.01, 'place spent more than 10ms outside the ledger write'; print(f'place {place[\"duration\"] * 1000:.1f}ms, of which the ledger write took {record[\"duration\"] * 1000:.1f}ms')" 2>&1) && { printf '%s\n' "$out"; exit 0; }; printf '%s\n' "$out" | tail -n 1; exit 1
```

```{hint}
:title: If the check fails
The check reads `trace.jsonl`, which the config's second sink writes,
takes the last `place` event and the ledger write beneath it, and
expects the write to take at least 25ms and to account for all but a
few milliseconds of the order. No file means the server is not
running under the runner from this directory.
```

The test on the next page does not need the server, and the page
after that changes the config, so stop it now. The action sends
Ctrl-C to the server's terminal.

```{interrupt}
:id: stop-server
:session: shell
:title: Stop the server
```
