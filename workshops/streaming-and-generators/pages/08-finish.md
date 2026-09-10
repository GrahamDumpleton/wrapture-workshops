---
title: Finish
requires: [quiz:fresh-proxy]
---

# Finish

The generator stayed real, and two layers told the story a canned
list cannot:

- A binding on a generator method records one event per iteration,
  with `items` counting what the consumer pulled and a `MISSING`
  result when it stopped early.

- `iterator()` builds a proxy with no target: `on_item` to validate or
  transform each item, `on_finish`, `on_abandon` and `on_error` for
  how the iteration ended, applied through `transforms_result()` on
  the producer or `transforms_args()` on the consumer.

- An item stage that raises fails the stream at exactly that page, and
  the event records the exception the consumer saw.

- The same pieces make a pytest test, with the proxy built inside the
  test and the binding scoped by the timeline.

```{quiz}
:id: fresh-proxy
:title: One proxy per test
question: "Why does the pytest test build its own flaky proxy rather than sharing one with the notebook?"
options:
  - { text: "The fail_at counter counts items through the proxy, so a shared proxy would fail at a different page on its second iteration", correct: true }
  - { text: "A proxy can only be applied to one generator", explanation: "One factory can wrap any number of iterators. It is the counter inside fail_at that carries state across them." }
  - { text: "A proxy is removed when the timeline exits, like a binding", explanation: "A proxy has no lifecycle to remove; it acts only at the moment it is applied to an iterator. The timeline scopes the binding, not the proxy." }
  - { text: "The notebook's proxy is on the consumer side and the test needs the producer side", explanation: "The same factory works on either side. The test wants a fresh counter, not a different attachment point." }
explanation: Behaviour is snapshotted when the factory wraps an iterator, and the counter in fail_at lives in the check, not in any generator, so it keeps counting across iterations. A proxy built with it is good for one iteration.
```

The Finish button below says where to go next.
