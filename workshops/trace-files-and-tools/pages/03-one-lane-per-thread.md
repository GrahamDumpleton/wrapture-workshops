---
title: One lane per thread
requires: [verify:converted]
---

# One lane per thread

Three exporters render a trace for existing tools rather than a
viewer of wrapture's own, and `python -m wrapture.tools convert` runs
them from a shell without writing any code; bare
`python -m wrapture.tools` lists the commands. `chrome` renders Chrome
trace JSON, the format the Perfetto UI opens directly.

```{execute}
:id: run-convert
:session: shell
:wait: prompt
python -m wrapture.tools convert --format chrome -o trace.json trace.jsonl
```

```{execute}
:id: read-chrome
:session: shell
:wait: prompt
python -c "import json; entries = json.load(open('trace.json'))['traceEvents']; print(len(entries), 'entries;', sum(e['ph'] == 'X' for e in entries), 'slices on threads', sorted(e['args']['name'] for e in entries if e['name'] == 'thread_name'))"
```

```
35 entries; 32 slices on threads ['ThreadPoolExecutor-0_0', 'ThreadPoolExecutor-0_1']
```

One complete slice per event and a metadata entry naming each
thread. Download `trace.json` from the file browser (right-click the
file and choose Download) and drop it onto
[ui.perfetto.dev](https://ui.perfetto.dev): the trace becomes a
navigable timeline, one lane per thread, one slice per event, nested
slices for nested events, with widths proportional to duration.
Clicking a slice shows the captured arguments and result in the
detail pane. The gaps between slices are unobserved time, which for a
deliberately sparse trace is itself information, and a generator's
slice spans creation to close with its accumulated body time
alongside.

The other two formats are `mermaid`, a sequence diagram that renders
on GitHub and in most documentation tooling, which the analysis
workshop drew from a notebook, and `canonical`, which the next page
puts to work.

```{verify}
:id: converted
:label: trace.json holds one slice per event and both thread names
:substrate: shell
:trigger: after:read-chrome
out=$(.venv/bin/python -c "import json; entries = json.load(open('trace.json'))['traceEvents']; print(len(entries), 'entries;', sum(e['ph'] == 'X' for e in entries), 'slices on threads', sorted(e['args']['name'] for e in entries if e['name'] == 'thread_name'))" 2>&1) && [ "$out" = "35 entries; 32 slices on threads ['ThreadPoolExecutor-0_0', 'ThreadPoolExecutor-0_1']" ] && { echo "$out"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
`trace.json` must be converted from the one-run `trace.jsonl` of the
previous page: 32 slices plus three metadata entries, naming two
threads. Convert again after any change to the trace file.
```
