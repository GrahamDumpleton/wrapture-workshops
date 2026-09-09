---
title: Welcome
requires: [verify:notebook-ready]
---

# Bindings that are not calls

Everything so far has bound a call. A test also needs to reach the
things around the calls: an attribute the code reads and writes, an
environment variable, a constant on a module, a settings dict that
other modules imported by reference, a formatter looked up in a
registry, and a generator whose values arrive one at a time. The
stdlib has an idiom for each, `patch.object`, `patch.dict`, pytest's
`monkeypatch`. wrapture spells all of them as bindings, with the
lifecycle you already know: a context manager, restored on exit
however the test ends, and on the tape when there is something to
record.

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

`shop.py` holds an `Order` whose `status` moves from new to paid to
shipped, `describe()` which reads that status, `price()` which reads
its configuration from an environment variable, a settings dict, a
module constant and a formatter registry, and `history()`, a
generator over a list of orders with two consumers. The configuration
lives in {open}`config.py`, which `shop.py` imports the way any module
would, holding `SETTINGS` by reference.

```{file-open}
:id: open-shop
:path: shop.py
```

Create the notebook. Its first cell imports the module, pays an order
and describes it.

```{notebook-create}
:id: create-notebook
:path: {{ notebook }}
:open: true
- markdown: |
    # Bindings that are not calls
    Each step of the workshop adds a cell below.
- code: |
    import os

    import wrapture
    import config
    from shop import Order, describe, first_shipped, price, statuses

    order = Order(1, 100)
    order.pay()
    describe(order)
  tags: [setup]
```

```{cell-run}
:id: run-setup
:path: {{ notebook }}
:cell: setup
```

```{verify}
:id: notebook-ready
:label: The notebook runs with wrapture and the module available
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:run-setup; cell-executed setup
wrapture.__version__ and describe(order) == "order 1 is paid"
```

```{hint}
:title: If the check says wrapture is not defined
The notebook is not using the workshop's kernel. Create the
environment with the first step, then pick the kernel named
"Bindings that are not calls" from the notebook's kernel picker at
the top right, and run the cell again.
```
