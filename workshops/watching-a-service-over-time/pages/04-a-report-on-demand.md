---
title: A report on demand
requires: [verify:server-up-again, verify:kick-report, verify:new-schedule]
---

# A report on demand

Something looks odd at 15:40 and the hourly report is twenty minutes
away. `on_signal` and `on_file` open a run from outside the process,
with no restart and no code: `kill -USR1 <pid>`, or `touch` a path
the window watches. Either can be the only trigger, or sit beside
`every`, where kicks add runs to the schedule. Append a second window
to the config: it collects for three seconds after each signal, with
no filter this time, so the request rows are in it.

```{file-write}
:id: add-kick
:path: wrapture.toml
:mode: append
:open: true


[[window]]
name = "kick"
on_signal = "SIGUSR1"
for = "3s"
report = "reports/{window}-{datetime}.txt"

[[window.collect]]
type = "aggregate"
```

A signal during the three seconds is refused rather than overlapping,
since runs never do. Without `for` a kick would toggle instead: one
signal to start collecting, another to report and start over. The
handler is installed when the window starts, on the main thread, and
any handler already there is called after wrapture's. `SIGUSR1` does
not exist on Windows, where `on_file` is the equivalent, and it is
also the one to use under a server that owns the signal handlers.

The server reads its config at startup, so stop it and start it
again. The action sends Ctrl-C to the server's terminal.

```{interrupt}
:id: stop-server
:session: shell
:title: Stop the server
```

```{execute}
:id: restart-server
:session: shell
:title: Start the server again under the new config
:wait: 3s
python -m wrapture -m flask --app webshop run --port 5075
```

```{verify}
:id: server-up-again
:label: The server answers on port 5075 again
:substrate: shell
:trigger: after:restart-server
curl -sf -o /dev/null http://127.0.0.1:5075/health && echo "The server answers on port 5075"
```

From the terminal on the right, send the signal to the server and put
eight seconds of traffic through it, so the three-second run has
something to count and the restarted schedule closes a run of its
own.

```{execute}
:id: kick-server
:session: client
:title: Open a run with a signal, then send traffic
:wait: prompt
kill -USR1 "$(pgrep -f 'flask --app webshop run --port 5075')" && .venv/bin/python load.py 8
```

```{execute}
:id: list-kick
:session: client
:wait: prompt
ls reports && cat reports/kick-*.txt
```

```
kick-2026-09-10T18-35-39.txt
summary-2026-09-10T18-35-25
summary-2026-09-10T18-36-40
aggregate "aggregate" run 1, 2026-09-10 18:35:36 to 18:35:39 +10:00 (3.0s), pid 14525
7 paths, 1,232 operations begun, 1,232 completed, 352 raised

calls    total     self  per-call    min    max  errors  path
  352  286.7ms  222.5ms     815us  367us  3.3ms      88  flask.app:Flask.wsgi_app
  176   48.5ms   25.4ms     276us  195us  1.0ms          webshop:order
  176   23.1ms   22.0ms     131us   69us  844us      88  shop:OrderService.place
  176   15.7ms    9.7ms      89us    2us  298us      88  webshop:quote
   88    6.0ms    6.0ms      68us   53us  121us          flask:render_template
  176    772us    772us       4us    4us   15us      88  shop:Gateway.charge
   88    322us    322us       4us    3us    6us          shop:Ledger.record
```

The kick report sits beside the scheduled ones, timestamped, and this
time the request row is at the top: every request the Flask
instrumentation recorded, with the 500s counted as its errors,
because the note the instrumentation makes against a failed request
counts as one.

```{verify}
:id: kick-report
:label: The signal opened a three-second run and its report includes the request row
:substrate: shell
:trigger: after:list-kick
file=$(ls reports/kick-*.txt 2>/dev/null | tail -n 1); [ -n "$file" ] || { echo "no reports/kick-*.txt yet: the signal did not reach the server, or the three seconds have not passed"; exit 1; }; grep -q 'wsgi_app' "$file" && grep -q '^aggregate "aggregate" run 1' "$file" && { echo "$file: one run opened by the signal, requests included"; exit 0; }; echo "$file has no request row: the kick window's collect entry should carry no filter"; exit 1
```

```{hint}
:title: If the check fails
The check looks for a `reports/kick-*.txt` file with a request row
in it. No file means the server was not restarted after the window
was added, so it never installed the handler, or `pgrep` found no
server to signal. The report is written three seconds after the
signal, so check again if it is only just late.
```

There are now two `summary` directories, and that is the restart
showing. Schedules live in the process and start afresh at apply:
nothing is persisted or resumed, so the new process opened a new
schedule, named by its own first run, and the directory appeared
when that run closed.

```{verify}
:id: new-schedule
:label: The restarted server opened a new summary schedule with a directory of its own
:substrate: shell
:trigger: after:list-kick
count=$(ls -d reports/summary-*/ 2>/dev/null | wc -l | tr -d ' '); [ "$count" -ge 2 ] && { echo "$count summary schedules: one per server process, each named by its first run"; exit 0; }; echo "only $count summary directory: the server has not been restarted, or its first run has not closed yet"; exit 1
```
