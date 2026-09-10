---
title: The whole surface
requires: [verify:headers-only-when-recording]
---

# The whole surface

Open {open}`wrapture_local/urllib_support.py` and look at how little
it needs. The hook runs when `urllib.request` is imported, binds
`OpenerDirector.open` with a `transforms_args` stage, and in that
stage adds whatever `wrapture.trace_headers()` returns to the
request's headers. That function is the whole public surface such an
instrumentation needs: it returns the pairs an outbound message made
right now should carry, whatever minted or parsed the identity, and
it returns nothing when nothing is being recorded, so injecting it is
always safe to attempt. `wrapture.current_trace()` is its
carrier-agnostic sibling, for a transport with no header concept,
such as trace context in a SQL comment.

```{file-write}
:id: write-headers
:path: headers.py
:open: true
import wrapture

print("outside any recording:", wrapture.trace_headers())

wrapture.add_sink(wrapture.Printer())

with wrapture.block("nightly-report"):
    print("inside a block:", wrapture.trace_headers())
```

```{execute}
:id: run-headers
:session: client
:wait: prompt
.venv/bin/python headers.py
```

```
outside any recording: {}
block: nightly-report
inside a block: {'traceparent': '00-2f0890450381eb5030616981a79303df-92d11f555a87f217-01'}
nightly-report [20us]
```

With no sink registered the first call returns an empty mapping,
because with nothing listening no event exists and no identity was
minted. Inside the block, with a printer listening, the block is the
root of a trace and the header carries its id. That is also how a
process with no HTTP ingress gets its trace root: a cron job, CLI
command or queue worker wraps its operation in a block, the block
mints, and `trace_headers()` supplies the identity for whatever it
sends outward.

W3C trace context is the one wire format wrapture speaks, and one
invariant governs an identity it parses but nothing claims: never
break a trace you do not understand. An arriving identity keeps its
raw headers, and on the way out a slot no tracing sink has claimed
forwards those headers verbatim, so an upstream product sees this
service as a transparent hop and its trace stays connected. Headers
wrapture does not parse are never touched at all. Switching on
`[otel]` in both processes, as the export workshop's last page did,
changes nothing about the ids: the exporter claims the identity
wrapture minted, so the files, the wire and the spans agree.

```{verify}
:id: headers-only-when-recording
:label: trace_headers() is empty with nothing recording and carries traceparent inside a recorded block
:substrate: shell
:trigger: after:run-headers
out=$(.venv/bin/python headers.py 2>&1) && printf '%s\n' "$out" | grep -q '^outside any recording: {}$' && printf '%s\n' "$out" | grep -q "^inside a block: {'traceparent': '00-" && { printf '%s\n' "$out" | grep 'recording\|inside'; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check runs `headers.py` again and expects an empty mapping on
the first line and a `traceparent` header inside the block. A
non-empty first line means a sink was registered before the first
call; an empty second line means no sink is listening, so the block
never became a recorded event and minted nothing.
```

The quote service has done its part. Stop it before moving on; the
action sends Ctrl-C to its terminal.

```{interrupt}
:id: stop-server
:session: shell
:title: Stop the quote service
```
