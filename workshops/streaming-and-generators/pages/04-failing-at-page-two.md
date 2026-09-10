---
title: Failing at page two
requires: [verify:failure-injected]
---

# Failing at page two

A canned list cannot fail between items; a proxy can. An item stage
that raises fails the iteration at that point: the wrapped generator
is closed, `on_error.notifies()` hooks see the exception, and it then
propagates to the consumer exactly as if `pages()` had raised while
producing that page. `fail_at()` in `helpers.py` is a small counter
that picks the item.

Give the binding this proxy instead of the watcher. `transforms_result`
stages accumulate, so `passes_through()` clears the earlier one first.
The swallowing exporter should report the two rows it wrote before
the failure and no more, and the timeline shows the iteration ending
in the injected error rather than exhaustion.

```{cell-insert}
:id: insert-flaky
:path: {{ notebook }}
:tags: [flaky]
:run: true
errors = []

flaky = wrapture.iterator()
flaky.on_item.validates_item(fail_at(2, OSError("connection reset")))
flaky.on_error.notifies(errors.append)

pages.on_call.passes_through().transforms_result(flaky)

with wrapture.timeline(pages) as tape:
    out = []
    written = Exporter().write(catalogue.pages(), out)
    failed = pages.events.raising(OSError).first

print(tape.tree())
written, out, errors, failed.items, failed.exception
```

`items` is 1: page two never reached the consumer, because the check
raised in its place. Either the `raising()` filter on the events or
the proxy's own error list can carry the assertion. A consumer that
does not catch the error, such as `collect_ids`, lets it propagate,
and a test asserts that with `pytest.raises(OSError)` as it would any
other failure.

```{verify}
:id: failure-injected
:label: The exporter kept two rows, the proxy reported the error, and the event carries it
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-flaky; cell-executed flaky
written == 2 and out == ["1,item-1", "2,item-2"] and len(errors) == 1 and isinstance(errors[0], OSError) and failed.items == 1 and isinstance(failed.exception, OSError)
```

```{hint}
:title: One proxy per iteration
The counter in `fail_at` counts items through the proxy, not through
any one generator, so a proxy built with it is good for one
iteration: run the cell again and the failure lands on a different
page. Make a fresh one per test rather than sharing.
```
