---
title: The stream beside the reports
requires: [verify:stream-rotated]
---

# The stream beside the reports

Sometimes the individual events are wanted after all, for a query
over the afternoon's failures. The `jsonlines` sink has been running
since the server started, at the process tier, so it hears every
event from every thread and writes it as one JSON object per line
without blocking the observed call. The `{datetime}` in its path and
`rotate = "5s"` keep one file per period rather than one forever;
for a day in staging that would be `{date}` and `"1d"` with
`align = true`, so the file changes at local midnight.

```{execute}
:id: list-traces
:session: client
:wait: prompt
ls traces
```

```
trace-2026-09-10T18-35-24.jsonl
trace-2026-09-10T18-35-29.jsonl
trace-2026-09-10T18-35-34.jsonl
trace-2026-09-10T18-35-39.jsonl
trace-2026-09-10T18-36-40.jsonl
trace-2026-09-10T18-36-45.jsonl
```

Rotation is wrapture's own: on each interval the sink closes its
file, expands the template again and opens whatever that names, on
every platform, with no external mover, and the queued lines drain
to the old file first. Where the earlier workshops used `jq`, a short
one-liner over every file does the same job here.

```{execute}
:id: count-stream
:session: client
:wait: prompt
.venv/bin/python -c "import glob, wrapture; files = sorted(glob.glob('traces/*.jsonl')); events = [e for f in files for e in wrapture.load_events(f)]; print(len(files), 'files,', len(events), 'events,', sum(e['kind'] == 'request' for e in events), 'requests,', sum('exception' in e for e in events), 'raised')"
```

```
6 files, 9240 events, 2640 requests, 1980 raised
```

The `raised` count is the shop's own exceptions, a declined card at
the gateway and at the service above it, and the `KeyError` in the
quote view. A request that answered 500 is not in it: the request
event completed normally as far as the middleware could see, and the
`KeyError` sits on it as a note under `caught`, which the
`analysing-a-trace` workshop read.

```{verify}
:id: stream-rotated
:label: The stream rotated into several files and carries the failures
:substrate: shell
:trigger: after:count-stream
out=$(.venv/bin/python -c "import glob, wrapture; files = sorted(glob.glob('traces/*.jsonl')); events = [e for f in files for e in wrapture.load_events(f)]; assert len(files) >= 2, f'{len(files)} file(s) under traces/: the sink needs a time variable in its path and rotate = \"5s\"'; requests = sum(e['kind'] == 'request' for e in events); raised = sum('exception' in e for e in events); assert requests and raised, f'{len(events)} events but {requests} requests and {raised} raised: the traffic has not reached the server, or the lines have not been flushed yet'; print(len(files), 'files,', len(events), 'events,', requests, 'requests,', raised, 'raised')" 2>&1) && { printf '%s\n' "$out"; exit 0; }; printf '%s\n' "$out" | tail -n 1; exit 1
```

```{hint}
:title: If the check fails
The check reads every `traces/*.jsonl` file and expects at least two
of them, with request events and raised exceptions among the lines.
One file means the sink has no `rotate`; no requests means the
server is not running under the runner, or the traffic was sent
before it started.
```

Lines are queued to a writer thread, so a file is complete only once
the sink is flushed. At interpreter exit wrapture flushes every
process sink and closes any open window run, writing its report
marked `cut_short`; `wrapture.shutdown()` does the same on demand,
for hosts that tear the interpreter down without running atexit
callbacks. That is what the next page is about, so stop the server
now and watch the last report land.

```{interrupt}
:id: stop-server-again
:session: shell
:title: Stop the server
```
