---
title: Where the time goes
requires: [verify:charted]
---

# Where the time goes

A table answers the question; a chart makes it obvious to someone who
did not ask it. Two bars per path, total and self, side by side.

```{cell-insert}
:id: insert-time-chart
:path: {{ notebook }}
:tags: [time-chart]
:run: true
ax = summary.plot.barh(title="Where the time goes, by path")
ax.set_xlabel("seconds over the run")
ax.invert_yaxis()
```

The two bars for the ledger and the gateway are the same length. The
two for `place` are not, and the difference between them is the sum of
the other two: everything `place` spent, it spent in its children.

Errors are the other thing to count by path. The rows with an
`exception` are the declined cards, once where the gateway raised and
once where `place` let it escape.

```{cell-insert}
:id: insert-errors
:path: {{ notebook }}
:tags: [errors]
:run: true
errors = df[df["exception"].notna()].groupby("path").size()

ax = errors.plot.bar(title="Operations that raised, by path", rot=0)
errors
```

The same count on both paths, and none on the ledger, which never saw
those orders. A path with errors of its own would show a count with
nothing beneath it to explain; here every failure has a cause one
level down.

```{verify}
:id: charted
:label: The charts are drawn and the errors pair up
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-errors; cell-executed errors
ax.get_title().startswith("Operations that raised") and errors["shop:Gateway.charge"] == errors["shop:OrderService.place"] > 0 and "shop:Ledger.record" not in errors
```

```{hint}
:title: If the check fails
`errors` should be a Series with two entries, the gateway and the
service, holding the same count, and `ax` the bar chart drawn from it.
A third entry means a ledger write raised, which this shop never does;
a `TypeError` about `NaN` means the filter was `df["exception"]`
rather than `df["exception"].notna()`.
```
