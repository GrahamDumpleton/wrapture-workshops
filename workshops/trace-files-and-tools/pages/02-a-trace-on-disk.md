---
title: A trace on disk
requires: [verify:trace-written]
---

# A trace on disk

The config observes every function in `pipeline` and streams each
completed event to `trace.jsonl`. `JSONLines` writes one JSON object
per line, the format that `jq`, pandas and log tooling consume
directly, and a config sink is a process sink, so the worker threads
are heard with nesting intact.

```{file-write}
:id: write-config
:path: wrapture.toml
:open: true
[[observe]]
target = "pipeline"
match = "*"

[[sink]]
type = "jsonlines"
path = "trace.jsonl"
```

The sink appends across runs, so delete the file first for a clean
trace.

```{execute}
:id: run-traced
:session: shell
:wait: prompt
rm -f trace.jsonl && python -m wrapture main.py
```

Read the file back with `load_events()`, which returns the records
as dictionaries.

```{execute}
:id: read-trace
:session: shell
:wait: prompt
python -c "import wrapture; rows = wrapture.load_events('trace.jsonl'); print(len(rows), 'events on', len({row['thread_name'] for row in rows}), 'threads;', sum(row['parent_id'] is None for row in rows), 'roots')"
```

```
32 events on 2 threads; 4 roots
```

Four `process` roots, one per source, each with a `fetch` and three
`transform` and `store` pairs beneath it, spread over two threads. A
line is written when an event closes, exit and error alike, so every
line carries the outcome and the timing; lines therefore appear in
completion order, children before the operation that contains them,
and sorting by `seq` with nesting rebuilt from `parent_id` recovers
the tree. Every line has `seq`, `parent_id`, `depth`, `kind`, `path`
and the thread the operation began on; everything else appears only
when it was observed, so an absent `result` stays distinguishable
from a `null` one.

Two properties make the sink safe to leave running. The application
is never blocked on I/O: lines go onto a bounded queue drained by a
background writer thread, and when the queue is full the line is
dropped and counted rather than making the observed call wait. And
it declares `"summary"` capture, so it neither retains live objects
nor fails on unserialisable ones.

```{verify}
:id: trace-written
:label: The trace holds four roots from two threads
:substrate: shell
:trigger: after:read-trace
out=$(.venv/bin/python -c "import wrapture; rows = wrapture.load_events('trace.jsonl'); print(len(rows), 'events on', len({row['thread_name'] for row in rows}), 'threads;', sum(row['parent_id'] is None for row in rows), 'roots')" 2>&1) && [ "$out" = "32 events on 2 threads; 4 roots" ] && { echo "$out"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
`trace.jsonl` must hold exactly one run: 32 events from 4 roots on 2
threads. More events means the file was not deleted before a second
run; run the traced command again. Fewer means the config did not
apply, so check that `wrapture.toml` is in this directory and that
the program was started with `python -m wrapture`.
```
