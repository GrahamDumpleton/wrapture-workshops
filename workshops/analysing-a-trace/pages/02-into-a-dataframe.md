---
title: Into a DataFrame
requires: [verify:frame-built]
---

# Into a DataFrame

Every line of the file has `seq`, `parent_id`, `depth`, `kind` and
`path`, and everything else appears only when it was observed:
`duration`, `arguments`, `result`, `exception`. A list of dictionaries
with a stable shape is exactly what a DataFrame is built from. Keep
the columns the analysis needs.

```{cell-insert}
:id: insert-frame
:path: {{ notebook }}
:tags: [frame]
:run: true
import pandas as pd

df = pd.DataFrame(events)[["seq", "parent_id", "depth", "path", "duration", "arguments", "exception"]]
df.head()
```

The `arguments` column holds the dictionary the binding captured, with
the card already `<redacted>` because the config said so, and
`exception` is a dictionary of type and message on the rows that
raised and `NaN` on the rest. A field that is absent from a line means
it was not captured, and pandas keeps that distinction as a missing
value.

The three paths, and how many events each recorded:

```{cell-insert}
:id: insert-counts
:path: {{ notebook }}
:tags: [counts]
:run: true
df["path"].value_counts()
```

Three hundred `place`, three hundred `charge`, and fewer `record`,
because a declined charge never reaches the ledger. The gap is the
first number the trace gives that the program's own output did not.

```{verify}
:id: frame-built
:label: The DataFrame holds every event on three paths
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-counts; cell-executed counts
len(df) == len(events) and df["path"].nunique() == 3 and df["path"].value_counts()["shop:Ledger.record"] < 300
```

```{hint}
:title: If the check fails
`df` must be built from `events` with the seven columns above and
hold the same number of rows. A `KeyError` on a column means the file
holds events without that field, which happens when the config lost
its `redact` or the sink is not `jsonlines`; check `wrapture.toml`
against the previous workshop and run the traffic again.
```
