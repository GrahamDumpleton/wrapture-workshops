---
title: Welcome
requires: [verify:env-ready]
---

# Reading a trace after the fact

A printer shows a trace as it happens and a tape holds one for the
length of a test. Neither outlives the process. The durable form is a
file of JSON Lines, one object per completed event, which is what the
zero-code tracing workshop first wrote and the analysis workshop read
into a notebook. This workshop stays on the command line: the file
itself, the converter that renders it for other tools, a snapshot of
it that a test compares against, and what to do about a file that
grows for days.

The program is a small pipeline: {open}`pipeline.py` fetches a
source, transforms each item and stores it, with sleeps standing in
for I/O so the slices have width on a timeline. {open}`main.py` runs
four sources through it on a pool of two worker threads, which is the
point: a config sink is a process sink, so it hears both threads with
no timeline anywhere, and each thread becomes a lane of its own once
the trace is rendered.

## An environment for the program

wrapture is not installed in this JupyterLab, so make a virtual
environment in this directory and install wrapture and pytest into
it. The commands run in the workshop terminal, under the editor,
which stays activated for the rest of the workshop.

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

Run the pipeline once, as the program stands.

```{execute}
:id: run-plain
:session: shell
:wait: prompt
python main.py
```

```
processed 12 items from 4 sources
```

Twelve items, and nothing about which thread did what or how long any
step took. The next page writes that down without touching the
program.

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
