---
title: Welcome
requires: [verify:notebook-ready]
---

# Behaviour that changes over time

Most of what a test configures on a patch holds until the test changes
it. Retry logic is the classic case where that is not enough: the code
under test keeps calling, and the test needs the behaviour to change on
its own as it does. Fail twice and then succeed. Hand out a sequence of
canned responses. Run the real thing until it breaks and then fail
fast. `unittest.mock` handles the first two with a list passed as
`side_effect`. wrapture models the same idea as phases, and this
workshop is about what that buys you beyond the list.

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

`remote.py` holds a client that fetches a URL and rejects any with
"bad" in it, and three loops that call things: `fetch_with_retry()`
retries a fetch on a timeout, `wait_for()` polls a job until it says
done, and `reconnect()` asks a monitor for the service's health and
then tries the client, round after round.

```{file-open}
:id: open-remote
:path: remote.py
```

Create the notebook. Its first cell imports the module and fetches
once through the retry loop, which succeeds first time.

```{notebook-create}
:id: create-notebook
:path: {{ notebook }}
:open: true
- markdown: |
    # Behaviour that changes over time
    Each step of the workshop adds a cell below.
- code: |
    import wrapture
    from remote import Client, Job, Monitor, fetch_with_retry, reconnect, wait_for

    fetch_with_retry(Client(), "/orders")
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
wrapture.__version__ and fetch_with_retry(Client(), "/orders") == {"url": "/orders", "status": 200}
```

```{hint}
:title: If the check says wrapture is not defined
The notebook is not using the workshop's kernel. Create the
environment with the first step, then pick the kernel named
"Behaviour that changes over time" from the notebook's kernel picker
at the top right, and run the cell again.
```
