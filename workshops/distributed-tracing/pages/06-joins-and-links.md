---
title: Joins and links
requires: [quiz:join-or-link]
---

# Joins and links

Two relationships crossed a boundary in this workshop, and they are
deliberately not the same. On the second and third pages the server
joined the client's trace: the caller was still waiting, so the
server's request is part of the same operation, and the middleware
parsed the header at the boundary by exactly that rule. On the
previous page the thumbnails and the notification were linked: the
caller had moved on, so each became a trace of its own with a link
back to its origin.

The same two verbs are available to a boundary the middlewares do
not speak for. `block(name, joins=headers)` parses the identity a
synchronous ingress arrived with, an XML-RPC dispatcher or a raw
socket server say, and the block's tree becomes part of that
distributed trace by the middleware rules: joining at a root,
shading a subtree when nested, minting as usual when the mapping
carries nothing valid. `block(name, links=[headers])` is the
consuming side of a queue, where the producer is not waiting. A
mapping with no valid `traceparent` contributes nothing to either,
so the headers of an untraced message are safe to pass, and links
belong to roots: `links=` on a block nested inside an in-flight
operation is dropped with a warning, because a nested block is that
operation's child.

```{quiz}
:id: join-or-link
:title: Join or link
question: "A worker takes a job off a queue an hour after a request put it there, and the job's tree should relate to that request. Which spelling is right, and why?"
options:
  - { text: "block(..., links=[headers]): the request moved on long ago, so the job is a trace of its own with a link back", correct: true }
  - { text: "block(..., joins=headers): the job is part of the request's operation, so it should share its trace", explanation: "joins= says the caller is still waiting. A request that returned an hour ago is not waiting, and joining would make its trace a lie." }
  - { text: "Neither: the worker should call propagate() so the job nests under the request", explanation: "propagate() copies a context within one process for a thread the caller waits on. A queue crosses a process boundary and the caller is gone." }
  - { text: "Either, since both parse the same traceparent header", explanation: "They parse the same header but mean different things: joins= continues the trace, links= starts a new one that points back." }
explanation: Links are for hand-offs, where the producer has moved on; joins are for a server answering a waiting caller. The header is the same, the relationship it records is not.
```
