---
title: Welcome
requires: [verify:events-loaded]
---

# Analysing a trace in a notebook

The previous workshop streamed a trace to a file as JSON Lines and
read it back with a few lines of Python. Three orders fit on a
screen. Three hundred do not, and the questions change: where does
the time go across the whole run, which paths fail and how often, and
what does the latency of an order look like as a distribution rather
than a number. Those are questions about data, and a notebook is where
data goes.

The shop is {open}`shop.py`, with one change from the earlier
workshops: it has latencies planted in it, so that the timings are
worth charting. The gateway takes a couple of milliseconds per charge,
and the ledger takes longer the larger the amount it records.
{open}`traffic.py` places three hundred orders for two tenants, one of
them a big spender, and about one card in ten is declined.
{open}`wrapture.toml` is the config from the previous workshop, with
the card redacted and a JSON Lines sink.

## The environment

wrapture, pandas and matplotlib are not installed in this JupyterLab,
so the workshop needs an environment of its own, inside the workshop
directory, with a kernel for it. The step below creates it, which
takes a little while.

```{environment-create}
:id: create-env
:title: Create the workshop environment
```

```{hint}
:title: If the environment already exists
The step reports that it already exists and does nothing more, so it
is safe to click again. On a page without this step, a banner at the
top of the panel offers to create the environment instead, and an
environment created from the banner counts here. Restart, in the
panel's menu, removes the environment along with the notebook, and
this step creates it again.
```

## The trace

Run the traffic under the runner. This happens in the background, in
the workshop environment, and takes a few seconds; the sink appends
across runs, so any earlier file is removed first.

```{execute-capture}
:id: run-traffic
:title: Place three hundred orders under the JSON Lines sink
:capture: traffic
rm -f trace.jsonl && python -m wrapture traffic.py
```

The run reported: {var}`traffic`. Now create the notebook. Its first
cell reads the file back with `load_events()`, which returns one
dictionary per event sorted into recording order, and counts them.

```{notebook-create}
:id: create-notebook
:path: {{ notebook }}
:open: true
- markdown: |
    # Analysing a trace in a notebook
    Each step of the workshop adds a cell below.
- code: |
    import wrapture

    events = wrapture.load_events("trace.jsonl")
    len(events)
  tags: [setup]
```

```{cell-run}
:id: run-setup
:path: {{ notebook }}
:cell: setup
```

Three hundred orders, three hundred charges and one ledger write per
order that was not declined: 872 events.

```{verify}
:id: events-loaded
:label: The notebook holds the events of one run
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:run-setup; cell-executed setup
wrapture.__version__ and len(events) == 872
```

```{hint}
:title: If the check fails
A `NameError` on `wrapture` means the notebook is not using the
workshop's kernel: create the environment with the first step, pick
the kernel named "Analysing a trace in a notebook" from the picker at
the top right, and run the cell again. A count other than 872 means
`trace.jsonl` holds more than one run, or a partial one; run the
traffic step again and re-run the cell.
```
