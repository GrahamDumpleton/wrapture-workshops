---
title: Paths and rotation
requires: [verify:rotated]
---

# Paths and rotation

A process that runs for days cannot write one file forever, and there
are no built-in size caps. Growth is managed by putting a time
variable in the path and rotating on an interval. Every path wrapture
writes to is a template, expanded when the file is opened and never
per line: `{pid}` for pre-fork workers writing side by side, `{host}`
for fleets on shared storage, `{date}`, `{time}` and `{datetime}` in
local time, `{epoch}`, and `{now:%Y%m%d-%H}` for any `strftime`
format. A misspelt variable is an error where the path is given, not
an hour into a run, and the parent directories of the expanded path
are always created.

Rotation is wrapture's own. `rotate=` reopens the file on an interval
(`"15m"`, `"1h"`, `"1d"`, or a number of seconds), which with a time
variable in the path means moving on to a new file, on every platform
with no external mover. The interval here is two seconds so it can be
watched.

```{editor-replace}
:id: rotate-config
:path: wrapture.toml
:match: path = "trace.jsonl"
path = "traces/{date}/trace-{time}-{pid}.jsonl"
rotate = "2s"
```

Run forty rounds of the four sources, about six seconds of work. No
file needs deleting first: every run opens a file of its own.

```{execute}
:id: run-rotating
:session: shell
:wait: prompt
python -m wrapture main.py 40 && find traces -name '*.jsonl' | sort
```

```
processed 480 items from 160 sources
traces/2026-09-10/trace-13-43-56-27211.jsonl
traces/2026-09-10/trace-13-43-58-27211.jsonl
traces/2026-09-10/trace-13-44-00-27211.jsonl
traces/2026-09-10/trace-13-44-02-27211.jsonl
```

Every event landed in one of the files, none were lost at the
boundaries, and the last one was flushed at exit.

```{execute}
:id: count-rotated
:session: shell
:wait: prompt
python -c "import glob; files = sorted(glob.glob('traces/*/*.jsonl')); print(len(files), 'files,', sum(1 for path in files for _ in open(path)), 'events')"
```

```
4 files, 1280 events
```

`align=True` puts the interval on the wall-clock boundary in local
time, so hourly means on the hour and daily at midnight. For rotation
on demand, `reopen()` from a signal handler does the same thing once.
And for a file that will leave the machine, `exceptions=` says how
much of an exception it carries, since messages routinely embed
values: `"message"` keeps the type and message, `"type"` the type
alone.

```{verify}
:id: rotated
:label: The forty rounds were written across several rotated files
:substrate: shell
:trigger: after:count-rotated
out=$(.venv/bin/python -c "import glob; files = sorted(glob.glob('traces/*/*.jsonl')); print(len(files), 'files,', sum(1 for path in files for _ in open(path)), 'events')" 2>&1) && [ "${out%% *}" -ge 2 ] && printf '%s\n' "$out" | grep -q ' 1280 events$' && { echo "$out"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check expects at least two files under `traces/` holding 1280
events between them, forty rounds of 32. One file means the sink was
not given `rotate`; a different total means the run was interrupted
or run twice, so remove the `traces` directory and run again.
```
