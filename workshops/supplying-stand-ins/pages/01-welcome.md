---
title: Welcome
requires: [verify:notebook-ready]
---

# When the test must supply the callable

Everything in the earlier testing workshops followed one rule: wrap
the real code, strictly, and record what actually flowed. This one is
the deliberate opt-out. A job pipeline publishes work to a message
broker. It takes the broker transport through its constructor, and
accepts an `on_complete` hook that it promises to call after each
job. The pipeline logic is what the tests are for: does it open a
channel, publish the right message, close the channel even on
failure, and honour the hook contract. The transport is what the
tests cannot have, and this time there is nothing to wrap: the seam is
the constructor, and the test itself must supply both the
collaborator and the hook.

This is the territory `unittest.mock` covers with `Mock()`, and the
convenience comes at a price: a fabricated object answers every
method, invented on first touch, so the misspelled method and the
drifted call pass silently. wrapture supplies the same stand-ins as a
scoped opt-in that stays strict. `stub()` builds one callable,
`mock()` builds one collaborator from a named class, and both record
on the same timeline as everything else in the test.

## The environment

wrapture is not installed in this JupyterLab, so the workshop needs an
environment of its own, inside the workshop directory, with a kernel
for it. The step below creates it, which takes a little while.

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

## The code under test

`pipeline.py` holds the `Pipeline`, the `Transport` and `Channel`
classes it is handed, whose methods all refuse to run because in
production every one of them does network I/O, and `on_complete`, the
documented shape of the hook.

```{file-open}
:id: open-pipeline
:path: pipeline.py
```

Create the notebook. Its first cell imports the module and shows what
happens with the real transport.

```{notebook-create}
:id: create-notebook
:path: {{ notebook }}
:open: true
- markdown: |
    # When the test must supply the callable
    Each step of the workshop adds a cell below.
- code: |
    import wrapture
    from pipeline import Channel, Pipeline, Transport, on_complete

    try:
        Pipeline(Transport()).run(["job-1"])
    except RuntimeError as exc:
        refused = str(exc)

    refused
  tags: [setup]
```

```{cell-run}
:id: run-setup
:path: {{ notebook }}
:cell: setup
```

Without library support the test would write a recorder class for the
transport, another for the channel, and a list-appending function for
the hook, then assert against the lists. It works, and for a
collaborator with real behaviour it stays the right move. The cost is
everything around it: each stand-in is hand-kept in step with the real
class, records only what its author thought to record, and none of
it shows up on the timeline next to the rest of the test's events.

```{verify}
:id: notebook-ready
:label: The notebook runs with wrapture and the pipeline available
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:run-setup; cell-executed setup
wrapture.__version__ and refused == "no broker in tests"
```

```{hint}
:title: If the check says wrapture is not defined
The notebook is not using the workshop's kernel. Create the
environment with the first step, then pick the kernel named
"When the test must supply the callable" from the notebook's kernel
picker at the top right, and run the cell again.
```
