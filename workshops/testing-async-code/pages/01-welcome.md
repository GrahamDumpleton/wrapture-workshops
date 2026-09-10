---
title: Welcome
requires: [verify:notebook-ready]
---

# Async methods and generators

A notifier fans messages out through a push gateway. The client is
`async def` all the way down: one coroutine method per send, and an
async generator streaming delivery receipts back. The notifier's
logic is what the tests are for. Does it send to every user, does it
survive a gateway timeout, and does it actually await what it calls?
That last one is the bug class unique to async code. A coroutine
created and dropped runs precisely nothing, and the code reads
correctly right up until production.

`unittest.mock` grew a separate class for all this, `AsyncMock`, with
`assert_awaited` alongside `assert_called`. wrapture needs no separate
anything. A binding on an `async def` target delivers stubbed
outcomes on await, exactly as the real method would, and every event
already records the call and its completion as two moments, so
"called but never awaited" is an ordinary filter.

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

`push.py` holds the `PushClient`, whose methods all refuse to run, the
`Notifier` that sends sequentially and stops at a timeout, a
`ConcurrentNotifier` that fans out with `asyncio.gather()`, and a
`collect_receipts()` consumer for the receipts stream. The notifier's
`nudge()` carries the bug this workshop catches on its fourth page.

```{file-open}
:id: open-push
:path: push.py
```

Create the notebook. The kernel supports `await` at the top level of a
cell, so the cells await the notifier directly rather than wrapping
each call in `asyncio.run()`. The first cell shows what the real client
does.

```{notebook-create}
:id: create-notebook
:path: {{ notebook }}
:open: true
- markdown: |
    # Async methods and generators
    Each step of the workshop adds a cell below.
- code: |
    import warnings

    import wrapture
    from push import ConcurrentNotifier, Notifier, PushClient, collect_receipts

    notifier = Notifier(PushClient())

    try:
        await notifier.broadcast(["ana"], "hello")
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

The gateway is what the tests cannot have. Everything from here on
leaves the client's methods in place and binds them.

```{verify}
:id: notebook-ready
:label: The notebook runs with wrapture and the notifier available
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:run-setup; cell-executed setup
wrapture.__version__ and refused == "no gateway in tests"
```

```{hint}
:title: If the check says wrapture is not defined
The notebook is not using the workshop's kernel. Create the
environment with the first step, then pick the kernel named
"Async methods and generators" from the notebook's kernel picker at
the top right, and run the cell again.
```
