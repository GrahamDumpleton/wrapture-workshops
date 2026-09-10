---
title: Rebuilding the tree
requires: [verify:self-time]
---

# Rebuilding the tree

Lines were written as events closed, children before the operation
that contains them, and `load_events()` put them back in `seq` order.
The nesting is in `parent_id`: a `charge` row's parent is the `place`
row it ran inside. That link is enough to compute the figure that
settles where the time goes.

A `place` takes as long as it takes, but most of that is the gateway
and the ledger it calls. Self time is an operation's duration minus
the time its observed children account for. Sum the children's
durations by parent, subtract from each parent's own, and total both
figures by path.

```{cell-insert}
:id: insert-self
:path: {{ notebook }}
:tags: [self]
:run: true
child_time = df.groupby("parent_id")["duration"].sum()

df["self"] = df["duration"] - df["seq"].map(child_time).fillna(0)

summary = df.groupby("path")[["duration", "self"]].sum().sort_values("self", ascending=False)
summary.columns = ["total", "self"]
summary
```

`place` has the largest total and by far the smallest self time: it is
slow only because of what it calls. The ledger and the gateway have no
observed children, so their self time is their total, and the ledger
is where the run's time actually went. That is the same arithmetic
`tape.self_time()` does for one event in a test and the `Aggregate`
collector does as events close, and the same column a profiler ranks
by; here it is a two-line groupby on a file.

```{verify}
:id: self-time
:label: The ledger leads on self time, and place trails
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-self; cell-executed self
list(summary.index) == ["shop:Ledger.record", "shop:Gateway.charge", "shop:OrderService.place"] and summary.loc["shop:OrderService.place", "self"] < 0.1 * summary.loc["shop:OrderService.place", "total"]
```

```{hint}
:title: If the check fails
The check expects `summary` sorted by self time with the ledger first
and `place` last, and `place`'s self time under a tenth of its total.
If `place` leads, the subtraction is missing or was done against
`parent_id` instead of `seq`: the children's time is summed by their
parent and looked up by each parent's own sequence number.
```
