# wrapture workshops

[![Launch on Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/GrahamDumpleton/wrapture-workshops/main?urlpath=lab)

Nothing to install: [start the workshops on mybinder.org](https://mybinder.org/v2/gh/GrahamDumpleton/wrapture-workshops/main?urlpath=lab)
in your browser (see [Launch on Binder](#launch-on-binder) below), or
[run them locally](#run-locally).

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

In the order to take them, with what each covers and roughly how long
it takes. [OUTLINE.md](OUTLINE.md) is the plan for the whole
collection.

1. **Your first binding** (`first-binding`, 10 minutes). Create a
   binding on a method, see that nothing is patched until you say so,
   apply it, suspend and resume it, remove it, scope it to a block, and
   change one thing about a call while the real method runs. In a
   notebook.

2. **Testing by wrapping, not replacing** (`wrap-not-replace`,
   15 minutes). Write the same unit tests with `unittest.mock` and with
   wrapture: a stub that rejects a drifted call, a private method seen
   from outside, a real result with one field pinned, and an error
   path asserted on what did not happen, ending with the decorator
   form and the pytest plugin. In a terminal, with pytest.

3. **Recording what real code did** (`recording-calls`, 15 minutes).
   Record real calls on a timeline and read the tape back: what one
   event holds, filters against assertions against expectations, the
   call tree naming the method that leaked a connection and the stack
   naming the line, order across bindings, nested timelines instead of
   resetting, and the record turned into a pytest test that fails until
   you fix the code. In a notebook.

4. **Behaviour that changes over time** (`phased-behaviour`,
   15 minutes). Script a binding's behaviour with phases: a count for a
   retry loop, a condition for a circuit breaker, a sequence for a
   polling loop with a loud error when it runs out, and `advance()`
   from the test or from another binding's result stage. In a notebook.

5. **Bindings that are not calls** (`beyond-callables`, 15 minutes).
   Bind an attribute to record its reads and writes and guard its
   transitions, hold a value in an environment variable or a module
   constant, change a settings dict for every module holding it, wrap a
   callable kept in a registry, and see how far a consumer read a
   generator. In a notebook.

6. **A program that narrates itself** (`live-tracing`, 10 minutes).
   Apply bindings in a program's entry point with no timeline and let a
   `Printer` narrate each call as it happens, redact the card numbers,
   then narrow the trace at the sink, at the binding, and for a whole
   subtree, and read the count of what was left out. In a terminal.

7. **Tracing without touching the program** (`zero-code-tracing`,
   15 minutes). Move the bindings and the sink into a `wrapture.toml`
   beside the program and run it unchanged under `python -m wrapture`,
   then injected at interpreter startup by autowrapt; ask the traced
   process what is installed and switch it off and on; keep the trace
   as JSON Lines, read it back, and draw it as a sequence diagram. In a
   terminal.

8. **Analysing a trace in a notebook** (`analysing-a-trace`,
   15 minutes). Run three hundred orders under a JSON Lines sink and
   treat the file as data: a DataFrame, the tree rebuilt from the
   parent links to give each path its total and self time, charts of
   where the time and the errors went, the latency of an order by
   tenant, and a few orders as a sequence diagram and a diff. In a
   notebook.

9. **One request as one tree** (`tracing-flask`, 15 minutes). Put the
   shop behind Flask and record each HTTP request as one tree from a
   single `[[instrument]]` entry: a quote, an order, a declined order,
   and a request that fails with a 500 and says why, then keep the
   health checks out. In two terminals.

10. **Where the time goes** (`finding-slow-code`, 15 minutes). Read the
    time off one request's tree, tell slow itself from slow because of
    a child with self time and assert on it in a test, get one
    `Aggregate` report for thirty requests from a window in the config,
    and tag each request with its tenant. In two terminals, with
    pytest.

11. **The same events, sent to a backend** (`opentelemetry-export`,
    20 minutes). Switch on OpenTelemetry export for the Flask shop with
    one `[otel]` table and read what the console exporters print, no
    collector needed: the request span named by its route, the view
    span beneath it with the exception on both, and the histograms
    after an export interval. Then a client and a quote service, and
    one trace id across both. In two terminals.

12. **wrapture and pytest, properly** (`wrapture-with-pytest`,
    20 minutes). Scope bindings in a suite without mixing styles, with
    the with-block, the decorators, yield fixtures that hand the
    binding over and shared declarations applied per test; then the
    plugin, whose sweep fails a leaking test by name and whose `tape`
    fixture attaches the call tree to a failure report, and a query
    budget for the whole suite from a counter. In a terminal, with
    pytest.

13. **Converting a mock test suite** (`coming-from-mock`, 20 minutes).
    Take a test module written with `unittest.mock` and convert it to
    wrapture one idiom at a time, with the suite green after every
    step: a return value, a failure, a sequence of outcomes, several
    patches at once, a value in place, the real call with one change,
    the order of calls, a log message, and the one test to leave as
    mock. In a terminal, with pytest.

14. **When the test must supply the callable** (`supplying-stand-ins`,
    15 minutes). Test a pipeline whose transport and completion hook
    the test has to supply: a stub for the hook, strict again with the
    real signature, a collaborator double from the named class that
    fabricates nothing, both on one tape, order across a batch, and
    failure paths reconfigured in place. In a notebook.

15. **Testing what a consumer does with a stream**
    (`streaming-and-generators`, 15 minutes). Test the consumers of a
    paginated catalogue against the real generator: one event per
    iteration with the item count and whether it finished, a proxy
    that sees every item and hears the end, a failure injected at the
    page you choose, items transformed on the way through, the proxy
    on the consumer's argument, and the whole thing as a pytest test.
    In a notebook.

16. **Async methods and generators** (`testing-async-code`,
    15 minutes). Test a notifier whose client is async all the way
    down: a stub whose outcome arrives on await, a timeout that stops
    a broadcast early through the real loop, the coroutine that was
    never awaited caught in one line, concurrent sends on one tape,
    an async generator with stubbed items, and the same assertions as
    a pytest suite under pytest-asyncio. In a notebook.

17. **Changing what a library does** (`patching-third-party-code`,
    20 minutes). Patch a vendored client you cannot edit: a header
    injected on the way in, the patch suspended, resumed and removed,
    reconfigured while installed, a retry around the whole call, an
    attribute clamped, the patch applied from a post-import hook
    before the library is imported, calls recorded without the token,
    and the same patch from a config file with the code beside it. In
    a terminal.

18. **Messages, phases and handled failures as events**
    (`logs-blocks-and-notes`, 15 minutes). Three more producers of
    events on the same tape as the calls: log messages pinned to the
    call that emitted them, named blocks that give a test phases to
    assert within, annotations that attach what the code knows, and a
    noted exception for a failure the code handled itself, all inert
    when nothing is listening. In a notebook.

19. **Where events go** (`sinks-and-collectors`, 20 minutes). The
    other side of the tape: a sink of your own, what a process sink
    hears that a timeline cannot and what a bound method costs when
    nobody listens, fan-out, depth, filtering and sampling in one
    registration, `Counter` and `Aggregate` keeping numbers rather
    than events, a binding declared a terminal node with a category,
    and resolvers naming each event per operation. In a terminal.

20. **Reading a trace after the fact** (`trace-files-and-tools`,
    15 minutes). JSON Lines as the durable form of a trace: a
    two-thread pipeline streamed to disk from a config file,
    converted for Perfetto with one lane per thread, rendered as a
    canonical golden file that a test compares the live call tree
    against, and rotated on a schedule through a path template. In a
    terminal.

21. **Reports on a schedule** (`watching-a-service-over-time`,
    15 minutes). A `Window` with `every=` closing a run each period
    in code, then the same from the config file for the Flask shop:
    a summary every few seconds with one file per run, a report on
    demand from a signal, an always-on JSON Lines stream that rotates
    rather than grows, and what a restart does to a schedule. In two
    terminals.

22. **One trace across two processes** (`distributed-tracing`,
    20 minutes). A client and a server, standard library only, one
    trace id across both: the identity in the `traceparent` header on
    the way out, parsed at the WSGI boundary on the way in, and two
    JSON Lines files joined on the id with no backend. Then work the
    caller does not wait for, on a thread and through a queue, linked
    back to its origin rather than nested under it. In two terminals.

23. **Requests in tests, and at the boundary** (`testing-web-requests`,
    15 minutes). The Flask instrumentation inside a pytest test: the
    request event with its status as the result and its route in
    `data`, a streamed body's chunks, the exception behind a 500, an
    ignored path, and then the `on_request` namespace on a WSGI
    binding, a canned response, a fault the server sees and a status
    rewritten on the way out. In a terminal.

24. **Instrumenting a package nobody has covered**
    (`writing-instrumentation`, 20 minutes). An `Instrumentation`
    class for a small library shipped with the workshop: the shape,
    a hook per trigger module, handlers observed as they register,
    an absorbed failure noted from the error handler, settings
    validated when the config loads, the class tested directly and
    through wrapture, listed by the tool, and how it would be
    packaged with an entry point. In a terminal.

## Launch on Binder

[mybinder.org](https://mybinder.org) is a free public service that
builds this repository into a temporary JupyterLab and runs it for you
in the browser, so there is nothing to install. To start, click this
link:

**[Launch the workshops on Binder](https://mybinder.org/v2/gh/GrahamDumpleton/wrapture-workshops/main?urlpath=lab)**

The badge at the top of this page opens the same link. Building and
starting the session takes a minute or two. When JupyterLab appears,
the workshops are listed in its workshop browser, numbered in the
order to take them, and the Finish dialog of each offers the next.
Opening a workshop locally shows a dialog asking you to trust it, since
its actions run commands on your machine. On Binder that dialog is
removed: the session is a container of its own, created for you and
discarded when you are done, and at no time is anything done on your
machine. The `binder/postBuild` script installs a settings override
that marks the checkout's workshops as trusted, turns off editing,
subscribes to the checkout's own `collection.json`, and names
`binder/welcome.md` as the message shown when the session starts,
which says what the workshops are and how to end the session.

Binder sessions are temporary: anything you do in one is gone when it
ends, so finish a workshop in the session you started it in. When you
are done with the session, whether you finished a workshop or not,
shut it down rather than closing the browser tab, so the resources go
back to Binder for other users. The Finish dialog at the end of a
workshop has a button for this, and so does JupyterLab's File menu,
under "Shut Down".

## Run locally

You need Python 3.14 and [uv](https://docs.astral.sh/uv/).
Clone the repository, install the environment and start JupyterLab from
the checkout:

```
git clone https://github.com/GrahamDumpleton/wrapture-workshops
cd wrapture-workshops
uv sync --no-dev
uv run jupyter lab --config=jupyter_lab_config.py
```

Without uv, the same environment comes from the requirements file
Binder uses:

```
python3 -m venv .venv && source .venv/bin/activate
pip install -r binder/requirements.txt
jupyter lab --config=jupyter_lab_config.py
```

The workshops appear under Installed in the workshop browser, because
they sit in the `workshops` directory the extension looks in by default.
The config file opens JupyterLab at
`http://localhost:8888/lab?collection=collection.json`, which adds the
collection for the session, so the browser lists the workshops numbered
in the order to take them, under the collection's title; without it
they are listed in directory order. From the browser, open a workshop,
or go straight to one with
`http://localhost:8888/lab?workshop=workshops/<name>`. Outside Binder
the trust dialog appears when a workshop opens; it lists what the
workshop's pages are allowed to do.

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
  welcome.md             the message shown when a Binder session starts
reference/wrapture       a git submodule of wrapture at the release the workshops teach,
                         the source of truth for its API and documentation
reference/jupyterlab-workshop
                         a git submodule of jupyterlab-workshop at the pinned release,
                         the full documentation and source of the workshop format
pyproject.toml           the uv project: JupyterLab and the extension, with the
                         authoring tools in the dev group
jupyter_lab_config.py    opens a local JupyterLab on the collection, so the workshops
                         are listed in order; `just lab` passes it to jupyter lab
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
