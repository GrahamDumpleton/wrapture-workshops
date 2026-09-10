---
title: Welcome
requires: [verify:notebook-ready]
---

# Testing what a consumer does with a stream

Code that streams is lazy by design. A paginated client yields one
page at a time, and the consumer decides how far to read: to the end,
only until it finds what it wants, or until something goes wrong
halfway. The behaviour that matters lives in that interplay: how many
pages the consumer really pulled, whether it stopped when it should,
whether it closed the source or left it hanging, and what it did when
a page failed to arrive.

None of that shows in the return value. A test that hands the
consumer a canned list of pages proves it can add up ids and nothing
else: a list is never lazy, cannot be abandoned, and cannot fail
between items. wrapture leaves the real generator in place and works
in two layers. A binding on the generator method records the whole
iteration as one event, with a live item count and a visible
difference between an iteration that finished and one that was
dropped. An iterator proxy sits inside that and runs your own
behaviour per item, at exhaustion, at abandonment and on error,
including raising a failure at exactly the item you choose.

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

`catalogue.py` is a stand-in for a paginated client. `pages()` is a
generator: nothing is fetched until the consumer asks, and `fetched`
counts the pages the catalogue actually served. Three consumers read
it differently: `collect_ids()` reads to the end, `first_match()`
returns as soon as it finds an item, dropping the generator without
closing it, and `Exporter.write()` swallows an `OSError` mid-stream
and reports how many rows it managed to write. `helpers.py` holds
one test helper for a later page.

```{file-open}
:id: open-catalogue
:path: catalogue.py
```

Create the notebook. Its first cell builds a catalogue of five records
in pages of two and reads it to the end.

```{notebook-create}
:id: create-notebook
:path: {{ notebook }}
:open: true
- markdown: |
    # Testing what a consumer does with a stream
    Each step of the workshop adds a cell below.
- code: |
    import wrapture
    from catalogue import Catalogue, Exporter, collect_ids, first_match
    from helpers import fail_at

    records = [{"id": n, "name": f"item-{n}"} for n in range(1, 6)]
    catalogue = Catalogue(records)
    collect_ids(catalogue.pages()), catalogue.fetched
  tags: [setup]
```

```{cell-run}
:id: run-setup
:path: {{ notebook }}
:cell: setup
```

Five ids from three pages. The obvious test builds those pages by
hand and passes them in, and it passes, and it says nothing about
laziness: it cannot tell whether `first_match` stopped after the
second page or read them all, cannot tell whether it closed the
source, and has no way to make page two fail to arrive.

```{verify}
:id: notebook-ready
:label: The notebook runs with wrapture and the catalogue available
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:run-setup; cell-executed setup
wrapture.__version__ and len(records) == 5 and catalogue.fetched == 3
```

```{hint}
:title: If the check says wrapture is not defined
The notebook is not using the workshop's kernel. Create the
environment with the first step, then pick the kernel named
"Testing what a consumer does with a stream" from the notebook's
kernel picker at the top right, and run the cell again.
```
