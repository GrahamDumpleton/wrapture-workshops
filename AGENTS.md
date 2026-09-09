# Agent guidance for wrapture-workshops

## Project

This repository is a collection of guided JupyterLab workshops that
teach [wrapture](https://github.com/GrahamDumpleton/wrapture), a Python
library for attaching bindings to arbitrary call sites without modifying
the code being observed, for monkey patching, testing and tracing. The
workshops run on the jupyterlab-workshop extension: each is a directory
under `workshops/` holding a `workshop.yaml` manifest and MyST Markdown
pages whose fenced directives are clickable actions. See README.md for
how the workshops are run, on Binder and locally.

The audience is Python developers meeting wrapture for the first time,
or coming from `unittest.mock` or OpenTelemetry instrumentation. Each
workshop takes one thing a reader might want to do with wrapture and
has them do it, in a live session, with checks confirming each step.
Ten to twenty minutes each.

What wrapture does and how its API works comes from its own
documentation, never from memory. `reference/wrapture` is a git
submodule of the wrapture repository, checked out at the tag of the
release the workshops teach (`just install` fetches it). Its
`README.md`, `docs/*.md` and `src/wrapture/` are the source of truth:
the getting started page, the worked examples (`docs/example-*.md`),
the mock comparison and the tracing guides are the material the
workshops draw on, and the source settles any question the docs leave
open. The same documentation is published at
https://wrapture.readthedocs.io. wrapture is not installed in this
project's environment; to try something, run
`uv run --with wrapture==<version> python`, with the version the
submodule is at. Do not invent functions, arguments or behaviour.

The scratch/ directory is not part of the git repo. It holds temporary
working files, such as reference material given to an agent or plans an
agent is asked to generate. Its contents come and go, so never reference
scratch/ files by name from code or documentation that will be committed.

## Tooling: always use uv and the Justfile

All Python environment and package management is done with
[uv](https://docs.astral.sh/uv/). Never use the Python venv module or
bare pip. Run commands in the project environment with `uv run`, for
example `uv run jupyter workshop lint workshops/<name>`.

The Justfile wraps the common tasks; run `just --list` to see them all
and prefer them over the underlying commands:

- `just install` syncs the environment, downloads the self-test browser
  and links the authoring skill into `.claude/skills`.

- `just lab` starts JupyterLab from this directory. It must run from
  here: the extension lists `workshops/` as installed, and the MCP live
  tools open workshops by paths relative to this root, so a workshop is
  `workshops/<name>` to `open_workshop`.

- `just new <name>` scaffolds a workshop; `just lint` lints the index
  and every workshop; `just render <name>` renders one to HTML;
  `just test <name>` self-tests one; `just index` writes or refreshes
  `collection.json`.

- `just requirements` relocks and rewrites `binder/requirements.txt`
  after a dependency change; `just bump <version>` moves the
  jupyterlab-workshop pin; `just bump-wrapture <version>` moves the
  reference checkout to a wrapture release tag.

## Writing workshops

Use the `jupyterlab-workshop-authoring` skill for the format, the
actions and checks, the rules that keep lint and the self-test green,
and how to read test output. `just install` links it into
`.claude/skills` from the installed package, so it always matches the
pinned release. If the skill is not loaded, read the `workshop://skill`
resource from the `workshop` MCP server before writing anything; its
reference files are `workshop://skill/references/<name>`.

The skill is a summary. The full documentation of the format is in
`reference/jupyterlab-workshop`, a git submodule of the extension's
repository checked out at the tag of the pinned release (`just bump`
moves it with the pin). Its `docs/*.md` cover what the skill only
names: checks, variables, environments, layouts, platforms, trust,
settings, limitations and troubleshooting. Its `examples/` are
complete workshops that pass the self-test, and `tests/` shows every
action and check exercised. When the skill does not answer a question
about an action, a check, a manifest key or a test failure, read the
docs there before guessing, and the source (`jupyterlab_workshop/` and
`packages/`) when the docs leave it open. The same documentation is
published at https://jupyterlab-workshop.readthedocs.io.

The `workshop` MCP server configured in `.mcp.json` provides the file
tools (`init`, `lint`, `render`, `pages`, `test`, `index`) and, when
`just lab` is running with a workshop open in author mode, the live
tools (`open_workshop`, `session_status`, `run_action`, `run_page`,
`run_workshop`). Workshop directories passed to the file tools are
relative to this directory: `workshops/<name>`.

Conventions for the workshops here:

- OUTLINE.md is the design of the collection: the tiers, the workshop
  names, what each covers, its format and sources, the decisions that
  apply to all of them, and a status table. Read it before adding or
  changing a workshop, follow the name and scope it gives, and update
  its status table and any settled open question when the work is
  done.

- wrapture is not preinstalled anywhere. Each workshop installs the
  version it teaches, pinned to the release the `reference/wrapture`
  submodule is at, into an environment of its own inside the workshop
  directory. A terminal-driven workshop has the learner create it with
  `python -m venv` and install with pip, as a project would, using the
  Python that runs JupyterLab, which is always present. A
  notebook-driven workshop declares `install-packages` and an
  `environment` with a `requirements.txt`, so the extension builds the
  isolated environment under `_workshop/venv` and registers its kernel.
  Do not use uv in workshop steps: it is not on Binder and a learner
  need not have it.

- Everything a workshop writes or runs stays inside its own directory:
  files and virtual environments it creates go there, and commands run
  there. Nothing under the home directory, no global configuration, no
  installs into the JupyterLab environment.

- Declare `linux` and `macos` as platforms. Add `windows` only when
  every command has been written to work there too, and lint with
  `--platform windows` if so.

- Each workshop is self-contained and does not depend on another having
  been completed, even though the collection orders them.

- After adding a workshop or editing a manifest, run `just index` to
  refresh `collection.json`, and add or update the workshop's entry in
  the README's list, in the order the collection gives.

- Lint every change. Lint must be clean, warnings included, before a
  workshop is considered done.

## Never run a workshop without checking what it does

`jupyter workshop test`, the MCP `test`, `run_action`, `run_page` and
`run_workshop` tools, and author mode's Run actions and Run checks all
run the workshop's commands for real, as the user, on this machine, with
their home directory, environment and Python environment. The self-test
protects only the workshop directory, by working on a temporary copy;
the live tools work on the directory itself and leave state behind.

Before running any of them, read every `execute`, `execute-capture` and
`script` body and every kernel check in the workshop. Run them unasked
only when everything stays inside the workshop directory and installs
nothing, which the conventions above require of the workshops here, so
a workshop that follows them is safe to test. If a workshop reaches
outside its directory, say so and wait to be told, rather than running
it. When the user asks for a test run, run it, and mention anything it
will change beyond the workshop directory.

## Style

- Do not use emdashes in any file in this project. Rephrase with
  commas, parentheses, colons, or separate sentences instead.

- In bulleted lists where items run to multiple lines, put a blank line
  between the bullets, in Markdown files and any other prose. Be
  consistent within a list.

- Workshop prose follows the skill's style guide: short pages, one step
  per action, say why before how, and checks that tell the learner what
  is wrong rather than only that it is.

## Git

- Git commit messages must never include a co-authored-by agent message
  or any similar agent attribution trailer.

- An AI agent must never commit changes on its own initiative. Finish
  the piece of work, summarize it, and wait to be told to commit.
  Permission to commit applies only to the work it was given for; it
  does not carry forward to later steps of a multi-step plan.
