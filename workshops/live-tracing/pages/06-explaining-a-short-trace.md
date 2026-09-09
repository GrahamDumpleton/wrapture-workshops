---
title: Explaining a short trace
requires: [verify:counted]
---

# Explaining a short trace

A trace that is shorter than expected raises a question of its own:
was the call never made, or made and not recorded? The skipped calls
are not simply lost. Each binding counts the operations it declined,
and the operations that ran beneath a declined tree, on
`filtered_calls`. Ask the three bindings after the run.

```{file-write}
:id: write-counts
:path: main.py
:mode: append
:open: true

print(f"filtered: place={place.filtered_calls} charge={charge.filtered_calls} record={record.filtered_calls}")
```

```{execute}
:id: run-counts
:session: shell
:wait: prompt
python main.py
```

```
filtered: place=2 charge=2 record=1
```

`place` declined the two globex orders itself. `charge` ran twice
beneath those declines and counted both. `record` counts one, because
the second globex order raised at the gateway and never reached the
ledger. Each binding explains its own silence, so a short trace can be
accounted for binding by binding rather than guessed at.

```{verify}
:id: counted
:label: The bindings account for the calls the trace left out
:substrate: shell
:trigger: after:run-counts
out=$(.venv/bin/python main.py 2>&1) && printf '%s\n' "$out" | grep -q '^filtered: place=2 charge=2 record=1$' && { echo "place=2 charge=2 record=1: the two globex orders, their charges, and the one ledger write"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check looks for the line `filtered: place=2 charge=2 record=1` in
the output of `main.py`. Different numbers mean the `place` binding
lacks `when=acme_only` or `tree=True`; a `NameError` means the
bindings are not assigned to `place`, `charge` and `record` as the
previous page's file did.
```
