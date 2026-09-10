---
title: The latency of an order
requires: [verify:by-tenant]
---

# The latency of an order

A mean hides a slow tenant among fast ones. The `place` rows are three
hundred durations, one per order, and a histogram shows the shape of
them.

```{cell-insert}
:id: insert-latency
:path: {{ notebook }}
:tags: [latency]
:run: true
place = df[df["path"] == "shop:OrderService.place"].copy()
place["ms"] = place["duration"] * 1000

ax = place["ms"].plot.hist(bins=40, title="Latency of place, per order")
ax.set_xlabel("milliseconds")
```

Most orders sit in a cluster at the fast end, and a long tail runs out
to several times that. The trace has the tenant on every `place` row,
in the captured arguments, so the tail can be named rather than
guessed at.

```{cell-insert}
:id: insert-by-tenant
:path: {{ notebook }}
:tags: [by-tenant]
:run: true
place["tenant"] = place["arguments"].str["tenant"]

place.groupby("tenant")["ms"].describe()[["count", "50%", "max"]]
```

The big spender's orders are the slow ones, because the ledger takes
longer the larger the amount it writes, and the median for each tenant
says so with no guessing. In a test the same question is one
`events.matching()` filter on the tape; here it is a groupby on a
column the bindings captured for free.

```{verify}
:id: by-tenant
:label: One tenant's orders are the slow ones
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-by-tenant; cell-executed by-tenant
set(place["tenant"]) == {"acme", "globex"} and place.groupby("tenant")["ms"].median()["acme"] > 2 * place.groupby("tenant")["ms"].median()["globex"]
```

```{hint}
:title: If the check fails
`place` must be the `place` rows of `df` with an `ms` column in
milliseconds and a `tenant` column read out of `arguments`. The check
expects acme's median to be more than twice globex's, which the
planted ledger latency guarantees. A `KeyError` on `tenant` means the
`arguments` column is missing the tenant, so the file was not written
by this workshop's config.
```
