---
title: Finish
requires: [quiz:who-minted-it]
---

# Finish

One table in the config, and the same events went to a backend:

- A request becomes a SERVER span named by its route, a call or a
  block an INTERNAL span beneath it, with captured arguments and
  annotations as `wrapture.arg.*` and `wrapture.data.*` attributes,
  the card already redacted.

- An exception ends its span in error status with an exception event,
  and one the framework caught is noted on the request span too, so
  the 500 arrives with its reason.

- The metrics signal aggregates the same events into the request
  duration histogram by route and status and a call duration
  histogram by path, with error series by exception type, nothing
  retained.

- A trace id minted at a tree's root travels in the `traceparent`
  header, is parsed at the WSGI boundary, and is claimed rather than
  replaced by the exporter, so the files, the headers and the spans
  agree, and a server's request span joins the client's trace as a
  remote child.

```{quiz}
:id: who-minted-it
:title: Who minted it
:shuffle: true
question: "On the last page, the quote service's request span carried the same trace id as the client's spans. Where was that id minted?"
options:
  - { text: "At the root of the client's tree, when place_order was recorded, before anything else was involved", correct: true }
  - { text: "By the urllib instrumentation, when it added the traceparent header", explanation: "The instrumentation only asked trace_headers() for the identity the current tree already had. It mints nothing, and returns nothing when no tree is recording." }
  - { text: "By the OpenTelemetry SDK, when the client's root span was exported", explanation: "The sink claims the identity wrapture minted rather than minting its own, which is why the JSON Lines file, written with no SDK involved, shows the same id." }
  - { text: "By the server's WSGI middleware, at the boundary", explanation: "The middleware parsed the id out of the header and joined the caller's trace. It mints an id only for a request that arrives without one, like the check's request at the top of the join." }
explanation: Every tree wrapture records mints a W3C trace id at its root. Everything after that, the header, the export and the boundary on the other side, carries or claims that one id.
```

The Finish button below says where to go next.
