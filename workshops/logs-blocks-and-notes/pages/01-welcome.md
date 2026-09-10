---
title: Welcome
requires: [verify:notebook-ready]
---

# Messages, phases and handled failures as events

A binding records calls observed from outside. That is one producer
of events, and the earlier workshops used nothing else. Three more
produce events onto the same tape, and each answers a question a call
event cannot. A log message the code emitted: which call logged it?
A stretch of code smaller than a function: what happened during the
render phase? A fact only the code knows: which tenant was this order
for? And a failure the code caught and handled itself, so the call
returned normally: did this operation fail?

Each of those is a line the code's author puts in the code, like a
log statement, and each is inert when nothing is listening. With no
sink and no timeline, nothing is built at all, which is what makes
them safe to leave in application code permanently, and it is what
makes them spans later when the same program runs under a tracer.

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

`shop.py` is the order service from the earlier workshops, and this
copy talks about itself. The gateway logs a warning before declining
a card. The service declares its fulfilment step as a block and
annotates it with the ledger entry, and it handles a declined card
rather than raising, returning a declined outcome with the exception
noted against the order.

```{file-open}
:id: open-shop
:path: shop.py
```

Create the notebook. Its first cell places two orders with nothing
listening, one paid and one declined, and asks whether anything is
in flight.

```{notebook-create}
:id: create-notebook
:path: {{ notebook }}
:open: true
- markdown: |
    # Messages, phases and handled failures as events
    Each step of the workshop adds a cell below.
- code: |
    import wrapture
    from shop import CardDeclined, Gateway, Ledger, OrderService

    service = OrderService()
    outcomes = [
        service.place(500, "4111-1111-1111-1111", tenant="acme"),
        service.place(250, "4000-0000-0000-0000", tenant="globex"),
    ]
    listening = bool(wrapture.current_event())

    outcomes, listening
  tags: [setup]
```

```{cell-run}
:id: run-setup
:path: {{ notebook }}
:cell: setup
```

One placed, one declined, and the warning the gateway logged went to
standard error the way any unhandled log record does. `current_event()`
returned an empty handle, which is falsy: nothing was recording, so
the block, the annotation and the noted exception in `shop.py` did
nothing. The rest of the workshop turns each of them on by listening.

```{verify}
:id: notebook-ready
:label: The notebook runs with wrapture and the shop available
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:run-setup; cell-executed setup
wrapture.__version__ and outcomes[0]["status"] == "placed" and outcomes[1]["status"] == "declined" and listening is False
```

```{hint}
:title: If the check says wrapture is not defined
The notebook is not using the workshop's kernel. Create the
environment with the first step, then pick the kernel named
"Messages, phases and handled failures as events" from the notebook's
kernel picker at the top right, and run the cell again.
```
