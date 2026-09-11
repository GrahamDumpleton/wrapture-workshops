---
title: Across many requests
requires: [verify:server-up-again, verify:stats-written]
---

# Across many requests

One request is an anecdote. The `Aggregate` collector keeps one row
per bound location, with how many operations began and completed, how
many raised, and the total, self, fastest and slowest times, sorted by
self time, which is the column profilers rank by. It retains no
events, so its memory is bounded by the number of bindings however
much traffic flows, and it asks for no argument or result values.

It can be registered as a sink in code, but the shape wanted here is a
report for the whole run of the server, which is a window in the
config file. A window with no trigger and no duration is one run for
the whole process: opened when the config applies, closed at
interpreter exit, one report.

```{file-write}
:id: add-window
:path: wrapture.toml
:mode: append
:open: true

[[window]]
name = "stats"
report = "stats.txt"

[[window.collect]]
type = "aggregate"
```

Start the server again with a fresh trace file.

```{execute}
:id: restart-server
:session: shell
:title: Start the server again under the new config
:wait: 3s
rm -f trace.jsonl stats.txt && python -m wrapture -m flask --app webshop run --port {{ server_port }}
```

```{verify}
:id: server-up-again
:label: The server answers on port {{ server_port }} again
:substrate: shell
:trigger: after:restart-server
curl -sf -o /dev/null http://127.0.0.1:{{ server_port }}/health && echo "The server answers on port {{ server_port }}"
```

Now thirty requests from the terminal on the right: ten orders for one
tenant, ten declined orders for another, and ten quotes. The script is
standard library only, so the JupyterLab Python runs it.

```{execute}
:id: send-traffic
:session: client
:wait: prompt
python3 traffic.py
```

The trees scroll past in the server's terminal. The report is written
when the run closes, which for this window is when the process exits,
so stop the server.

```{interrupt}
:id: stop-server-again
:session: shell
:title: Stop the server
```

```{execute}
:id: show-stats
:session: client
:wait: prompt
cat stats.txt
```

```
aggregate "aggregate" run 1, 2026-09-01 14:57:29 to 14:57:31 +10:00 (1.6s), pid 87241
7 paths, 120 operations begun, 120 completed, 20 raised

calls    total     self  per-call     min     max  errors  path
   10  358.3ms  358.3ms    35.8ms  30.7ms  39.5ms          shop:Ledger.record
   30  385.2ms   11.9ms    12.8ms   534us  40.5ms          flask.app:Flask.wsgi_app
   20  369.8ms    5.7ms    18.5ms   296us  40.1ms          webshop:order
   20  364.1ms    5.7ms    18.2ms   105us  39.9ms      10  shop:OrderService.place
   10    2.2ms    2.2ms     223us    63us   1.6ms          flask:render_template
   10    3.5ms    1.3ms     354us   188us   1.8ms          webshop:quote
   20    106us    106us       5us     4us    11us      10  shop:Gateway.charge
```

The ledger is the top row by a wide margin. The order view and `place`
have large totals and small self times, which is the same story the
single tree told, now over twenty orders with a minimum and maximum
attached. The errors column shows the ten declined cards twice, once
where the gateway raised and once where the service let it escape. The
same report can be produced every hour on the hour with totals reset,
from the same file, by giving the window a schedule.

```{verify}
:id: stats-written
:label: The report ranks the ledger first by self time
:substrate: shell
:trigger: after:show-stats
[ -f stats.txt ] && row=$(awk 'f && NF { print; exit } /^calls/ { f = 1 }' stats.txt) && printf '%s\n' "$row" | grep -q 'shop:Ledger.record$' && printf '%s\n' "$row" | grep -q '^ *10 ' && { echo "Top row by self time: $row"; exit 0; }; echo "stats.txt is missing, or its first row is not ten calls of shop:Ledger.record"; cat stats.txt 2>/dev/null; exit 1
```

```{hint}
:title: If the check fails
`stats.txt` is written when the server exits, so it appears only
after the interrupt above, and it must list `shop:Ledger.record` on
the first row of the table with ten calls. No file means the server
was started before the window was added to `wrapture.toml`, or is
still running; a different top row means the traffic script did not
reach the server.
```
