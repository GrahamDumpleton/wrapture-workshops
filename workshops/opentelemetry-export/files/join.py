"""Line up the two halves of each trace.

Print the first eight characters of the trace id on every record in
client.jsonl and server.jsonl, with the file it came from, sorted, so
each order's client half and server half sit together.
"""

import wrapture

lines = []
for name in ("client.jsonl", "server.jsonl"):
    for record in wrapture.load_events(name):
        trace_id = record.get("trace", {}).get("w3c", {}).get("trace_id", "no id  ")
        lines.append(f"{trace_id[:8]} {name} {record['path']}")

print("\n".join(sorted(lines)))
