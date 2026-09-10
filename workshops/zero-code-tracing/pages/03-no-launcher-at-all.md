---
title: No launcher at all
requires: [verify:injected]
---

# No launcher at all

The runner still owns the command line, and sometimes that is not
available either. A service manager, a container entry point or a
WSGI server starts the process, and you do not get to put
`python -m wrapture` in front of it. For that case the same config can
be injected at interpreter startup through autowrapt, a package that
exists precisely to run registered code once site initialisation
completes. Two opt-ins gate it, both outside wrapture: the package
has to be installed, and an environment variable has to name wrapture
as the thing to bootstrap.

```{execute}
:id: install-autowrapt
:session: shell
:title: Install autowrapt
:wait: prompt
pip install autowrapt
```

```{execute}
:id: run-injected
:session: shell
:wait: prompt
AUTOWRAPT_BOOTSTRAP=wrapture python main.py
```

The output is identical to the runner's, from plain `python` with the
program's own name on the command line. Absent either opt-in, the
entry in wrapture's package metadata is inert, and wrapture itself has
no dependency on autowrapt. Run the program once more without the
variable to see that.

```{execute}
:id: run-uninjected
:session: shell
:wait: prompt
python main.py
```

Silence again. Underneath, both doors lead to the same place: the
post-import hook machinery in wrapt is what lets wrapture apply a
config to modules that have not been imported yet, and the runner and
autowrapt are two triggers for it. Nothing is expressible through one
and not the other.

The positioning matters. Injection is a development, staging and
break-glass tool. The unwritten rule for autowrapt has always been
that it is not installed on production systems in normal
circumstances, precisely because of what it enables, and that
installation gate is the feature. Two consequences follow from the
mechanism. A config that is missing, or that cannot be applied, warns
and lets the process start untraced, because an error at bootstrap
would be fatal to an interpreter that has not even started, and the
variable reaches every Python process launched under it, not only the
one you meant. And the bootstrap imports no application code, so the
bindings still land as the application imports its own modules.

```{verify}
:id: injected
:label: autowrapt traces the program, and plain python does not
:substrate: shell
:trigger: after:run-injected
out=$(AUTOWRAPT_BOOTSTRAP=wrapture .venv/bin/python main.py 2>&1) && [ "$(printf '%s\n' "$out" | wc -l | tr -d ' ')" -eq 16 ] && printf '%s\n' "$out" | grep -q '^  shop:Gateway.charge !! CardDeclined' && [ -z "$(.venv/bin/python main.py 2>&1)" ] && { echo "Sixteen lines under AUTOWRAPT_BOOTSTRAP=wrapture, and nothing without it"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check runs `main.py` twice, once with `AUTOWRAPT_BOOTSTRAP=wrapture`
and once without, and expects the sixteen-line trace from the first
and nothing from the second. No trace from the first means autowrapt
is not installed in `.venv`; a warning about the config means
`wrapture.toml` has a problem the runner on the previous page would
have reported as an error.
```
