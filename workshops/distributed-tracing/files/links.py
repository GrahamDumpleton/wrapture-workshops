"""Print every root in uploads.jsonl, with the operation it links back to.

A root with a link is work that was caused by another operation but
not contained by it. The link carries the origin's trace and span
ids, and its seq when the origin ran in this process.
"""

import wrapture

events = wrapture.load_events("uploads.jsonl")
by_seq = {event["seq"]: event for event in events}

for event in events:
    if event["parent_id"] is not None:
        continue

    trace_id = event["trace"]["w3c"]["trace_id"][:8]
    line = f"{event['kind']} {event['path']} (trace {trace_id})"

    for link in event.get("links") or []:
        origin = by_seq.get(link.get("seq"))
        where = f"seq {link['seq']} {origin['path']}" if origin else "an operation elsewhere"
        line += f" <- {where} in trace {link['trace_id'][:8]}"

    print(line)
