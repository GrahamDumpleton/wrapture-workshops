---
title: Finish
---

# Finish

Two processes, one trace, with nothing but wrapture on both ends:

- The WSGI middleware at the server's boundary minted an id for a
  request with no header and joined the client's trace for one that
  carried `traceparent`.

- An `Instrumentation` class on the client's opener put the current
  tree's id into every outbound request, with `trace_headers()` as
  its whole surface, empty when nothing is recording.

- The two JSON Lines files joined on the id with no backend anywhere.

- `detach()` and `handoff()` turned work the caller did not wait for
  into trees of their own with links back to the origin, and the
  consumer's `block(links=...)` did the same for a message.

The Finish button below says where to go next.
