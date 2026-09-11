---
title: The same from a config file
requires: [verify:server-up, verify:summary-reports]
---

# The same from a config file

`ticking.py` had to import the shop and call `start()` itself. For
the Flask shop nothing is edited: windows are top-level `[[window]]`
tables in the config beside `[[sink]]`, the sink list being what
listens all the time and the window list what listens or collects
briefly. Contents go under `[[window.collect]]` in exactly the sink
grammar, `type` plus keys, gating keys included.

The config keeps the Flask instrumentation and the observe entries
from the earlier workshops and adds two things. A `jsonlines` sink
is the always-on stream, with a time variable in its path and
`rotate` so it moves to a new file every five seconds rather than
growing forever; the fifth page reads it. And a window named
`summary` runs back to back every five seconds, aligned to the
clock, writing one file per run into a directory named by the
schedule's start. The `filter` on its collect entry keeps the
request events out of the table, so the report is about the view
functions and the shop, and the request stream is left to the file.

```{file-write}
:id: write-config
:path: wrapture.toml
:open: true
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

[[sink]]
type = "jsonlines"
path = "traces/trace-{datetime}.jsonl"
rotate = "5s"

[[window]]
name = "summary"
every = "5s"
align = true
report = "reports/{window}-{first}/run-{run:02}.txt"

[[window.collect]]
type = "aggregate"
filter = { kind = "call" }
```

Inside a window three path variables join the usual ones: `{window}`
is the window's name, `{first}` is when the schedule's first run
opened, the same for every run of one schedule, and `{run}` is the
run number, `{run:02}` for zero padding. Each report is written whole
and then renamed into place, so a reader never sees half a file.

Start the server under the runner, in the terminal on the left. It
keeps that terminal until it is stopped.

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

Now the traffic, from the terminal on the right: twelve seconds of a
quote, an order, a declined order and a quote for an item that is not
in the catalog, round and round.

```{execute}
:id: run-load
:session: client
:title: Twelve seconds of traffic
:wait: prompt
.venv/bin/python load.py 12
```

```
1432 requests in 12s: 716 answered 200, 358 answered 402, 358 answered 500
```

While that ran, the window closed a run every five seconds and wrote
each one to a file.

```{execute}
:id: list-reports
:session: client
:wait: prompt
ls reports/summary-*/ && cat reports/summary-*/run-01.txt
```

```
run-01.txt
run-02.txt
aggregate "aggregate" run 1, 2026-09-10 18:35:25 to 18:35:30 +10:00 (5.0s), pid 14525
6 paths, 1,516 operations begun, 1,516 completed, 453 raised

calls   total    self  per-call   min    max  errors  path
  303  89.0ms  51.3ms     294us  188us  4.0ms          webshop:order
  303  37.7ms  35.7ms     124us   67us  1.7ms     151  shop:OrderService.place
  303  27.2ms  17.0ms      90us    2us  810us     151  webshop:quote
  152  10.2ms  10.2ms      67us   55us  124us          flask:render_template
  303   1.4ms   1.4ms       5us    4us   41us     151  shop:Gateway.charge
  152   565us   565us       4us    3us    6us          shop:Ledger.record
```

Each file is one period's table, and the picture emerges from
comparing them: which views the traffic reaches, how many quotes
fail, and whether `per-call` moves as the load does. The rows are the
view functions the Flask instrumentation observes and the shop's own
methods. There is no request row because the collect entry's
`filter = { kind = "call" }` admits only call events to the
collector, so the requests are left to the JSON Lines stream while
their views and the shop's methods, which are calls, still count; the
next page's window has no filter, and its report shows the request
row for contrast. The declined orders and the missing item
show as `errors` on the rows where they happened, and `self` time
puts the `order` view, which builds the response, above the service
call it makes.

```{verify}
:id: summary-reports
:label: The summary window wrote a report per run, about the calls and not the requests
:substrate: shell
:trigger: after:list-reports
count=$(ls reports/summary-*/run-*.txt 2>/dev/null | wc -l | tr -d ' '); [ "$count" -ge 2 ] || { echo "expected at least two run-*.txt files under reports/summary-*/, found $count: is the server running under the runner with the [[window]] entry, and did the traffic run?"; exit 1; }; grep -lq 'shop:OrderService.place' reports/summary-*/run-*.txt || { echo "no report mentions shop:OrderService.place: the observe entries are missing, or the traffic never reached the server"; exit 1; }; ! grep -q 'wsgi_app' reports/summary-*/run-*.txt || { echo "a report has a request row: the collect entry needs filter = { kind = \"call\" }"; exit 1; }; echo "$count reports so far, one per five seconds, with the shop's calls and no request row"
```

```{hint}
:title: If the check fails
The check counts the `run-*.txt` files under `reports/summary-*/`
and reads them. No files means the server is not running under the
runner with this config, or no run has closed yet: a run closes on
the five-second boundary, so wait a moment and check again. A file
with a `wsgi_app` row means the collect entry's `filter` is missing.
```

Leave the server running for now: the next page adds a window that
opens on demand.
