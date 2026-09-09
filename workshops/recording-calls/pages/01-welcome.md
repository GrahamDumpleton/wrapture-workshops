---
title: Welcome
requires: [verify:notebook-ready]
---

# Recording what real code did

The tests in the previous workshop leaned on a timeline and a tape to
assert on what happened. This workshop is about that recording side of
wrapture: what gets recorded, what one event holds, how to read the
record back, and the whole-tape views that answer questions about the
flow between calls.

The example is a resource leak, because it is the kind of bug the
recording model was made for. Code that acquires a connection has to
release it on every path out. The path that forgets does not fail:
nothing raises, nothing returns the wrong value, and the pool runs dry
a week later. The failure is an absence, and asserting on an absence
needs a record of what did happen, on the real objects, including ones
minted mid-call that the test never held.

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

`pooled.py` is a stand-in for any pooled resource. `Database.connect()`
mints a `Connection`, and a connection answers queries until `close()`
sets its `closed` flag. The repository is where the bug lives: `count()`
releases in a `finally`, so it is safe on every path, and `find()`
releases only when a row was found.

```{file-open}
:id: open-pooled
:path: pooled.py
```

Create the notebook. Its first cell imports the module and runs a
report over two keys, one that matches a row and one that does not.

```{notebook-create}
:id: create-notebook
:path: {{ notebook }}
:open: true
- markdown: |
    # Recording what real code did
    Each step of the workshop adds a cell below.
- code: |
    import wrapture
    from pooled import Connection, Database, Repository, report

    report(Repository(Database()), [1, 2])
  tags: [setup]
```

```{cell-run}
:id: run-setup
:path: {{ notebook }}
:cell: setup
```

The report is correct: no rows in the count, one row found. Nothing
about that result says a connection was left open.

```{verify}
:id: notebook-ready
:label: The notebook runs with wrapture and the module available
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:run-setup; cell-executed setup
wrapture.__version__ and report(Repository(Database()), [1, 2]) == (0, [(1, "widget")])
```

```{hint}
:title: If the check says wrapture is not defined
The notebook is not using the workshop's kernel. Create the
environment with the first step, then pick the kernel named
"Recording what real code did" from the notebook's kernel picker at
the top right, and run the cell again.
```
