---
title: Keeping the trace
requires: [verify:trace-on-disk]
---

# Keeping the trace

A printer is for watching. For a program that runs longer than you are
willing to sit and look at it, the sink is a file. Swapping the
`[[sink]]` entry for a JSON Lines one is the only change.

```{editor-replace}
:id: swap-sink
:path: wrapture.toml
:match: type = "printer"
type = "jsonlines"
path = "trace.jsonl"
```

The sink appends across runs, so remove any earlier file first, then
run the program under the runner again.

```{execute}
:id: run-jsonl
:session: shell
:wait: prompt
rm -f trace.jsonl && python -m wrapture main.py
```

Nothing prints this time. Each completed event was written to
`trace.jsonl` as one JSON object per line, when the event closed, so
every line carries the outcome and the timing. The declined charge
from the second order looks like this, with the `seq` and `parent_id`
fields enough to rebuild the tree and a field that is absent meaning
it was not captured, so a call that returned `None` and a call whose
result was never recorded stay distinguishable:

```json
{"seq": 5, "parent_id": 4, "depth": 1, "kind": "call",
 "path": "shop:Gateway.charge", "started": 1150729.898723529,
 "duration": 4.197005182504654e-06,
 "arguments": {"amount": 250, "card": "<redacted>"},
 "exception": {"type": "CardDeclined", "message": "card ending 0000 declined"},
 "trace": {"w3c": {"trace_id": "12cd461196239288a8b50e265b6a0f1a", "sampled": true}}}
```

The format is the one `jq`, pandas and most log tooling read directly,
which means the questions you would otherwise have scrolled a terminal
to answer become a few lines of Python. `wrapture.load_events()` reads
the file back, sorted into recording order. Every call to the gateway,
with what it was given and what came back, and then everything that
raised:

```{file-write}
:id: write-reader
:path: read_trace.py
:open: true
import wrapture

records = wrapture.load_events("trace.jsonl")

print("gateway charges:")
for record in records:
    if record["path"] == "shop:Gateway.charge":
        print(" ", record["seq"], record["arguments"], record.get("result"), record.get("exception"))

print("raised:")
for record in records:
    if "exception" in record:
        print(" ", record["path"], record["exception"]["type"])
```

```{execute}
:id: run-reader
:session: shell
:wait: prompt
python read_trace.py
```

```
gateway charges:
  2 {'amount': 500, 'card': '<redacted>'} {'id': 'ch_500', 'amount': 500} None
  5 {'amount': 250, 'card': '<redacted>'} None {'type': 'CardDeclined', 'message': 'card ending 0000 declined'}
  7 {'amount': 120, 'card': '<redacted>'} {'id': 'ch_120', 'amount': 120} None
raised:
  shop:OrderService.place CardDeclined
  shop:Gateway.charge CardDeclined
```

The exception shows at the order that let it escape and at the
gateway that raised it, in recording order, since `place` began
before `charge` did. Two properties make this safe to leave running against
something real. The application never waits on the file: lines go
onto a bounded queue drained by a background thread, and if the queue
fills the line is dropped and counted rather than making the observed
call block. And the sink captures values as bounded summaries, so an
unserialisable argument becomes a short description rather than an
error, and no live object is retained.

```{verify}
:id: trace-on-disk
:label: trace.jsonl holds one run of the three orders
:substrate: shell
:trigger: after:run-jsonl
out=$(.venv/bin/python -c "import wrapture; r = wrapture.load_events('trace.jsonl'); paths = sorted({x['path'] for x in r}); raised = sorted(x['path'] for x in r if 'exception' in x); assert len(r) == 8, f'{len(r)} records in trace.jsonl, expected 8 from one run: remove the file and run main.py under the runner again'; assert paths == ['shop:Gateway.charge', 'shop:Ledger.record', 'shop:OrderService.place'], f'paths in the file: {paths}'; assert raised == ['shop:Gateway.charge', 'shop:OrderService.place'], f'paths that raised: {raised}'; assert '4000' not in str(r), 'a card number reached the file: redact is missing from an observe entry'; print('8 records, three paths, and the declined card raised at the gateway and again at the service')" 2>&1) && { printf '%s\n' "$out"; exit 0; }; printf '%s\n' "$out" | tail -n 1; exit 1
```

```{hint}
:title: If the check fails
The check reads `trace.jsonl` with `load_events()` and expects eight
records from one run: three `place`, three `charge` and two `record`,
with the declined card raised on a `charge` and a `place`. A missing
file means the `[[sink]]` entry still says `printer`, or the `path`
line is missing; sixteen records mean the file was not removed before
a second run.
```
