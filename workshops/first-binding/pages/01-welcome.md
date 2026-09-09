---
title: Welcome
requires: [verify:notebook-ready]
---

# Your first binding

wrapture attaches bindings to call sites, methods and functions you
name, without changing the code they belong to. A binding can observe
what flows through the call, or change it: stub the result, raise an
error, or let the real code run with one thing altered. This workshop
takes one binding through its whole lifecycle in a notebook.

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

Now create the notebook. It starts with one class to bind to, a
payment gateway whose `charge` method returns a small dictionary, and
imports wrapture. Nothing about `Gateway` knows it is about to be
observed.

```{notebook-create}
:id: create-notebook
:path: {{ notebook }}
:open: true
- markdown: |
    # Your first binding
    Each step of the workshop adds a cell below.
- code: |
    import wrapture

    class Gateway:
        def charge(self, amount, currency="USD"):
            return {"id": f"ch_{amount}", "amount": amount}

    gateway = Gateway()
    gateway.charge(500)
  tags: [setup]
```

Run the cell to define the class and check the real method works.

```{cell-run}
:id: run-setup
:path: {{ notebook }}
:cell: setup
```

```{verify}
:id: notebook-ready
:label: The notebook runs with wrapture available
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:run-setup; cell-executed setup
wrapture.__version__ and gateway.charge(500) == {"id": "ch_500", "amount": 500}
```

```{hint}
:title: If the check says wrapture is not defined
The notebook is not using the workshop's kernel. Create the environment
with the first action, then pick the kernel named "Your first binding"
from the notebook's kernel picker at the top right, and run the cell
again.
```
