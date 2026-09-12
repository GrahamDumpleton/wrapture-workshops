---
title: Welcome
requires: [verify:env-ready]
---

# wrapture and pytest, properly

Bindings are ordinary objects with an explicit lifecycle, so they fit
pytest's scoping tools without special integration. What matters in a
suite is that every applied binding is removed again, whatever the
outcome of the test: a patch that leaks changes the behaviour of every
test that runs after it, and the test that then fails is the wrong
one. The earlier workshops used a with-block and, once, the decorator
form. This one puts the styles side by side, says why not to mix them,
and then turns on the plugin that catches the mistakes the styles are
there to prevent.

{open}`shop.py` is the order service from the earlier workshops, and
{open}`database.py` is a stand-in database layer with a repository on
top, for the last page. The tests go in files you write as you go,
one file per page, and every page runs `pytest`.

## An environment for the tests

wrapture is not installed in this JupyterLab, so make a virtual
environment in this directory and install wrapture and pytest into it.
The commands run in the workshop terminal, under the editor, which
stays activated for the rest of the workshop.

```{execute}
:id: create-venv
:session: shell
:title: Create and activate a virtual environment
:wait: prompt
python3 -m venv .venv && . .venv/bin/activate
```

```{execute}
:id: install-deps
:session: shell
:title: Install wrapture and pytest
:wait: prompt
pip install wrapture==1.0.0b1 pytest
```

```{verify}
:id: env-ready
:label: wrapture and pytest are installed in .venv
:substrate: shell
:trigger: after:install-deps
.venv/bin/python -c "import wrapture, pytest; print('wrapture', wrapture.__version__, 'and pytest', pytest.__version__)"
```

```{hint}
:title: If the check fails
The virtual environment must be at `.venv` in this directory, with
wrapture and pytest installed into it. Run the two commands above
again; creating the environment a second time does no harm.
```
