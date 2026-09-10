---
title: Work the caller does not wait for
requires: [verify:linked-not-nested]
---

# Work the caller does not wait for

Nesting says one operation ran inside another, and on a single
thread that is always the truth. A hand-off breaks that rule: a
request that starts a thread and returns, a pool worker that runs a
job long after its submitter finished, a consumer that processes a
message some other process put on a queue. The work was caused by an
operation but is not contained by it, and drawing it as a child
would make the parent's duration a lie and leave the child with
nothing to attach to once the parent has closed. wrapture spells the
relationship with a link: a root event carrying, on `event.links`,
the identity of the operation that handed it off, without being
nested under it.

{open}`uploads.py` has both shapes. `handle_upload()` stores the file
and fans thumbnail generation out to a pool with `detach()`, the
sibling of `propagate()`: where `propagate()` copies the recording
context so the thread's events nest under the caller's, `detach()`
clears the in-flight stack in the copy and remembers the origin, so
the thread's work becomes a root of its own, minting its own trace,
with a link back. It also enqueues a notification: `handoff()`
captures the in-flight event as the origin, its `headers()` are the
same `traceparent` pairs as `trace_headers()`, and the consumer
thread's `block(links=...)` names them, so the notification tree
links to the request the way it would across a broker. Neither call
records anything itself. The config lists the members to observe
rather than matching `*`, because the consumer loop must not be
observed: as a root on its thread it would contain every consumer
block, and links belong to roots.

```{file-write}
:id: write-uploads-config
:path: uploads.toml
:open: true
[[observe]]
target = "uploads"
match = ["handle_upload", "store", "generate_thumbnails", "resize", "notify"]

[[sink]]
type = "printer"

[[sink]]
type = "jsonlines"
path = "uploads.jsonl"
```

```{execute}
:id: run-uploads
:session: shell
:title: Three uploads under the runner
:wait: prompt
rm -f uploads.jsonl && python -m wrapture --config uploads.toml main.py
```

```
uploads:handle_upload(name='cat.png')
  uploads:store(name='cat.png')
  uploads:store -> None [11.3ms]
uploads:generate_thumbnails(name='cat.png')  <- trace d9c07130e2f13b8147af5c2a9f098706
  uploads:resize(name='cat.png', size=32)
block: notify-upload  <- trace d9c07130e2f13b8147af5c2a9f098706
  uploads:notify(name='cat.png')
uploads:handle_upload -> 'accepted' [12.3ms]
  uploads:notify -> None [6.7ms]
notify-upload [6.8ms]
  uploads:resize -> 'cat.png@32' [27.7ms]
  uploads:resize(name='cat.png', size=64)
...
```

Three threads interleave in the printer, and the roots that were
handed off carry the trace id of the request they came from. The
upload answered in twelve milliseconds, its own time, while the
thumbnails took eighty on the pool thread. `links.py` reads the file
back and prints each root with what it links to.

```{execute}
:id: run-links
:session: shell
:wait: prompt
python links.py
```

```
call uploads:handle_upload (trace d9c07130)
call uploads:generate_thumbnails (trace 3c2fecf6) <- seq 1 uploads:handle_upload in trace d9c07130
block uploads:notifier (trace 896a842c) <- an operation elsewhere in trace d9c07130
call uploads:handle_upload (trace 359f7d1c)
call uploads:generate_thumbnails (trace a2e2df9d) <- seq 8 uploads:handle_upload in trace 359f7d1c
block uploads:notifier (trace 39e2b595) <- an operation elsewhere in trace 359f7d1c
...
```

Nine roots for three uploads. The thumbnail root's link carries the
origin's `seq`, since the origin ran in this process, while the
notification block's link has only the ids, exactly what a message
would carry through a real broker, and the block is named by its
path in the file rather than by its label. Every renderer carries
the relationship: the canonical form appends the origin's path to a
root handed off within the same trace, the Chrome trace joins the
lanes with a flow arrow, and an OpenTelemetry sink turns the links
into span links on a span that exists.

```{execute}
:id: run-canonical
:session: shell
:wait: prompt
python -m wrapture.tools convert --format canonical uploads.jsonl
```

```
call uploads:handle_upload
  call uploads:store
call uploads:generate_thumbnails <- uploads:handle_upload
  call uploads:resize
  call uploads:resize
  call uploads:resize
block uploads:notifier
  call uploads:notify
...
```

```{verify}
:id: linked-not-nested
:label: Each upload is three roots, the thumbnails and the notification linked back to it
:substrate: shell
:trigger: after:run-links
out=$(.venv/bin/python -c "import wrapture; records = wrapture.load_events('uploads.jsonl'); roots = [r for r in records if r['parent_id'] is None]; uploads = [r for r in roots if r['path'] == 'uploads:handle_upload']; assert len(uploads) == 3, f'{len(uploads)} handle_upload roots, not three: run main.py under the runner with uploads.toml'; thumbs = [r for r in roots if r['path'] == 'uploads:generate_thumbnails']; assert len(thumbs) == 3 and all(any(l.get('seq') == u['seq'] for u in uploads) for r in thumbs for l in r.get('links') or []), 'the thumbnail work is not a root linked to its upload: detach() is missing from the pool submission'; assert all(r.get('links') for r in thumbs), 'a thumbnail root carries no link'; blocks = [r for r in roots if r['kind'] == 'block']; assert len(blocks) == 3 and all(r.get('links') and 'seq' not in r['links'][0] for r in blocks), 'the notification blocks are not roots linked by the message headers'; assert not any(r['path'] == 'uploads:notifier' and r['kind'] == 'call' for r in records), 'the notifier loop was observed, so the blocks nest under it: list the members rather than matching *'; print(f'{len(roots)} roots: 3 uploads, 3 thumbnail trees linked by seq, 3 notification blocks linked by headers')" 2>&1) && { printf '%s\n' "$out"; exit 0; }; printf '%s\n' "$out" | tail -n 1; exit 1
```

```{hint}
:title: If the check fails
The check reads `uploads.jsonl` and expects nine roots: three
uploads, three thumbnail trees whose link names an upload's `seq`,
and three notification blocks whose link carries only ids. Fewer
roots means the work nested instead, because `detach()` or the
`links=` on the block is missing; a `notifier` call event means the
config observed the consumer loop.
```
