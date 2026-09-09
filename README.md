# wrapture workshops

[![Launch on Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/GrahamDumpleton/wrapture-workshops/main?urlpath=lab)

Guided, hands-on workshops for
[wrapture](https://github.com/GrahamDumpleton/wrapture), the Python
library for attaching bindings to arbitrary call sites without modifying
the code being observed, and doing something useful with what flows
through them: monkey patching, testing with recorded and supplied
stand-ins, and tracing. Each workshop takes one thing you might want to
do with wrapture and walks you through doing it, in a live JupyterLab,
with the workshop checking your work as you go.

The workshops run on
[jupyterlab-workshop](https://github.com/GrahamDumpleton/jupyterlab-workshop),
a JupyterLab extension that shows the instructions in a side panel with
clickable actions that drive the session: terminals, files, the editor,
notebooks and kernels. A workshop can check what you have done, hold a
page until it is done, ask questions, and put files back when they go
wrong. Nothing here needs a container or a cluster: a workshop is a
directory of a `workshop.yaml` manifest and Markdown pages that runs
wherever JupyterLab runs. Each workshop installs wrapture for itself,
into a virtual environment of its own inside the workshop directory,
the way you would in a project, so nothing is installed into the
JupyterLab environment and nothing is left behind outside the workshop.

## The workshops

None yet. Each workshop will be listed here in the order to take them,
with what it covers and roughly how long it takes.

## Launch on Binder

The badge above starts a JupyterLab on [mybinder.org](https://mybinder.org)
with the workshops listed in the workshop browser, ready to open. No trust dialog is shown, because the
`binder/postBuild` script installs a settings override that marks the
checkout's workshops as trusted, turns off editing, and subscribes to
the checkout's own `collection.json`, so the workshops are numbered in
the order to take them and the Finish dialog of each offers the next.

A link can open one workshop directly by naming its directory in the
checkout, URL-encoded as the `urlpath`:

```
https://mybinder.org/v2/gh/GrahamDumpleton/wrapture-workshops/main?urlpath=lab%3Fworkshop%3Dworkshops%2F<name>
```

Binder sessions are temporary: anything you do in one is gone when it
ends, and a session can take a minute or two to start.

## Run locally

You need Python 3.14 and [uv](https://docs.astral.sh/uv/).
Clone the repository, install the environment and start JupyterLab from
the checkout:

```
git clone https://github.com/GrahamDumpleton/wrapture-workshops
cd wrapture-workshops
uv sync --no-dev
uv run jupyter lab
```

Without uv, the same environment comes from the requirements file
Binder uses:

```
python3 -m venv .venv && source .venv/bin/activate
pip install -r binder/requirements.txt
jupyter lab
```

The workshops appear under Installed in the workshop browser, because
they sit in the `workshops` directory the extension looks in by default.
Open "Browse Workshops" from the launcher, or go straight to one with
`http://localhost:8888/lab?workshop=workshops/<name>`. Opening
`http://localhost:8888/lab?collection=collection.json` instead adds the
collection for the session, so the browser lists the workshops in order
under its title. Outside Binder the trust dialog appears when a
workshop opens; it lists what the workshop's pages are allowed to do.

## Subscribe from your own JupyterLab

With the extension installed anywhere, subscribe to this collection and
the workshops are offered under Available in the workshop browser, with
Install fetching each from this repository. In the browser, choose
"Collections…" and enter the raw URL of the index:

```
https://raw.githubusercontent.com/GrahamDumpleton/wrapture-workshops/main/collection.json
```

## What is in the repository

```
workshops/
  <name>/                a workshop: workshop.yaml and pages/*.md
collection.json          the index the workshop browser reads, written by `just index`
binder/
  requirements.txt       the locked runtime environment, exported from uv.lock
  runtime.txt            the Python version for the Binder image
  postBuild              writes the settings override described above
reference/wrapture       a git submodule of wrapture at the release the workshops teach,
                         the source of truth for its API and documentation
reference/jupyterlab-workshop
                         a git submodule of jupyterlab-workshop at the pinned release,
                         the full documentation and source of the workshop format
pyproject.toml           the uv project: JupyterLab and the extension, with the
                         authoring tools in the dev group
Justfile                 the common tasks; run `just` to list them
.mcp.json                the MCP server configuration for AI agent clients
AGENTS.md                guidance for AI agents writing workshops here
OUTLINE.md               the design of the collection: the workshops planned,
                         what each covers, and where each stands
.github/workflows/
  test.yml               lints and self-tests every workshop on every push
```

Each workshop is self-contained and can be copied out on its own.

## Writing and checking workshops

`just install` sets up the environment: it syncs uv, fetches the
reference submodules, downloads the browser the self-test drives, and
links the authoring skill shipped in the jupyterlab-workshop package
into `.claude/skills`, where Claude Code finds it. Then, with `just lab` running in one terminal so the live
tools have a JupyterLab to work in, start Claude Code (or VS Code with
the Claude extension) in this directory, and ask for a workshop. The
`.mcp.json` file gives the agent the `jupyter workshop` tools; the
skill tells it the format. `AGENTS.md` says what the workshops here are
for and the rules they follow.

The same tools work by hand:

```
just new <name>          scaffold a workshop under workshops/
just lint                lint collection.json and every workshop
just render <name>       render a workshop to HTML
just test <name>         self-test one workshop in a JupyterLab of its own
just index               write or refresh collection.json
```

The self-test starts a JupyterLab, opens the workshop trusted, runs every
action, check, quiz and form in order, and reports PASS or FAIL for
each. It runs the workshop's commands for real, as you, on your
machine; only the workshop directory is protected, by a temporary copy.
Read a workshop before testing it. The workflow in
`.github/workflows/test.yml` lints and self-tests every workshop on
Linux and Windows from the same lock file, so CI tests what Binder
serves.

## Updating the release

jupyterlab-workshop is pinned once, in `pyproject.toml`. `just bump
<version>` moves the pin, relocks, rewrites `binder/requirements.txt`,
relinks the skill and moves the `reference/jupyterlab-workshop`
submodule to the same release tag. Binder builds a fresh image for the
new commit, and CI tests the workshops against the new release.

The wrapture release the workshops teach is named in each workshop's
requirements and matched by the `reference/wrapture` submodule.
`just bump-wrapture <version>` moves the submodule to the release tag;
the workshops' requirements are then updated by hand and the workshops
retested.
