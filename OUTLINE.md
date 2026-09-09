# wrapture workshops: outline

The design of the collection: how it is organised, what each workshop
covers, its name, format and source material, and the decisions that
cut across all of them. It is a living document. Read it before adding
a workshop, and update it when one is added, changed or dropped: the
status table below records where each workshop stands, and the open
questions section shrinks as they are settled.

## Sources

The first tier follows a series of blog posts on wrapture, one post
per workshop. The links are the posts' public addresses. The posts
are the starting point for what each workshop says; the
wrapture documentation and source in `reference/wrapture` remain the
authority on what wrapture does, and a workshop follows the docs
where the two differ.

- [Introducing wrapture](https://grahamdumpleton.me/posts/2026/08/introducing-wrapture/),
  31 August 2026. Background: what wrapture is for and why it exists.
  No workshop of its own.

- [Unit testing with wrapture](https://grahamdumpleton.me/posts/2026/09/unit-testing-with-wrapture/),
  1 September 2026. Source for `wrap-not-replace`.

- [Recording calls with wrapture](https://grahamdumpleton.me/posts/2026/09/recording-calls-with-wrapture/),
  2 September 2026. Source for `recording-calls`.

- [Phased behaviour in wrapture](https://grahamdumpleton.me/posts/2026/09/phased-behaviour-in-wrapture/),
  3 September 2026. Source for `phased-behaviour`.

- [Beyond callables in wrapture](https://grahamdumpleton.me/posts/2026/09/beyond-callables-in-wrapture/),
  4 September 2026. Source for `beyond-callables`.

- [Live tracing with wrapture](https://grahamdumpleton.me/posts/2026/09/live-tracing-with-wrapture/),
  7 September 2026. Source for `live-tracing`.

- [Zero-code tracing with wrapture](https://grahamdumpleton.me/posts/2026/09/zero-code-tracing-with-wrapture/),
  8 September 2026. Source for `zero-code-tracing` and, with the
  documentation, `analysing-a-trace`.

- [Tracing Flask with wrapture](https://grahamdumpleton.me/posts/2026/09/tracing-flask-with-wrapture/),
  9 September 2026. Source for `tracing-flask`.

- [Finding slow code with wrapture](https://grahamdumpleton.me/posts/2026/09/finding-slow-code-with-wrapture/),
  10 September 2026. Source for `finding-slow-code`.

- [OpenTelemetry export in wrapture](https://grahamdumpleton.me/posts/2026/09/opentelemetry-export-in-wrapture/),
  11 September 2026. Source for `opentelemetry-export`.

The repositories the workshops draw on, all on GitHub:

- [wrapture](https://github.com/GrahamDumpleton/wrapture), the
  library itself, with its documentation and runnable examples. The
  `reference/wrapture` submodule is a checkout of it.

- [wrapture-instrumentation](https://github.com/GrahamDumpleton/wrapture-instrumentation),
  ready-made instrumentation for common Python packages, the Flask
  target among them, used from `tracing-flask` on.

- [wrapture-instrumentation-postgresql](https://github.com/GrahamDumpleton/wrapture-instrumentation-postgresql),
  the PostgreSQL client libraries (psycopg, psycopg2, asyncpg).

- [wrapture-instrumentation-mysql](https://github.com/GrahamDumpleton/wrapture-instrumentation-mysql),
  the MySQL client libraries (PyMySQL, mysqlclient, aiomysql).

- [wrapture-instrumentation-aws](https://github.com/GrahamDumpleton/wrapture-instrumentation-aws),
  the AWS SDK (boto3 and botocore).

- [autowrapt](https://github.com/GrahamDumpleton/autowrapt), the
  bootstrap that applies a config at interpreter startup, used in
  `zero-code-tracing`.

- [wrapt](https://github.com/GrahamDumpleton/wrapt), the library
  wrapture's patching is built on. Not taught here, but the place
  to read when a question is about the wrapper itself rather than
  the binding, and the target of wrapture's escape hatch.

The product-specific instrumentation packages need a real database
or cloud account behind them, so no workshop here uses them; they are
listed for completeness and as candidates should a workshop with a
local database ever be wanted.

The second tier draws on the wrapture documentation, published at
https://wrapture.readthedocs.io and checked out under
`reference/wrapture/docs`: the guides (`monkey-patching.md`,
`unit-testing.md`, `ad-hoc-tracing.md`, `wsgi-tracing.md`,
`asgi-tracing.md`, `scheduled-tracing.md`, `otel-export.md`,
`instrumentation-packages.md`), the worked examples (`example-*.md`)
and the runnable examples under `reference/wrapture/examples`. Each
workshop entry below names the pages it uses.

## Shape of the collection

Two tiers, in one ordered collection. The number of workshops is not
a concern: the collection is in part an experiment in using an AI
agent to write a long course, so more workshops, each exercising a
different example, is the better outcome. Workshops are bite sized,
one question each, rather than merged to make fewer of them.

The first tier follows the September blog series, with a first
workshop on the getting started page in front of it, kept separate
from the recording workshop so the opening chunks stay small. Each
workshop takes one post's question, has the learner do it in a live
session, and stops where the post stops. They are short, ten to fifteen minutes,
and a learner who does only these has seen the whole of wrapture once:
the testing arc and then the tracing arc, on one running example,
with one notebook workshop between the arcs that treats a trace as
data to chart.

The second tier goes deeper on one topic each, where the first tier
gave it a paragraph. These are longer, fifteen to twenty minutes, and
draw on the guides and worked examples in the documentation rather
than the posts. Each states which first-tier workshop it assumes the
learner has seen, but does not depend on it having been completed in
this session: it ships its own starting code.

The ordering rule is the documentation's own: mechanism before
recording before tracing, and within each tier the simple case before
the special case. The collection is marked ordered so the browser
numbers the workshops and each Finish dialog offers the next.

Every workshop uses the same running example wherever it fits, the
shop from the posts (`Gateway`, `Ledger`, `Notifier`, `OrderService`,
later behind Flask). A learner who has seen it once does not have to
learn new code to learn the next idea. Workshops whose question needs
different code (a connection pool, a paginated catalogue, a retrying
client) use the code the corresponding worked example uses.

## Naming

Directory names are short kebab-case phrases naming the question, not
the mechanism, with no numeric prefix. The collection index carries
the order, and unnumbered names stay stable as workshops are inserted
or moved. Titles are sentence case and read as what the learner will
do.

Tier one names echo the post titles so a reader arriving from the
blog finds the matching workshop. Tier two names name the topic.

## Tier one: the series, hands on

### 1. `first-binding`: Your first binding

The getting started page, first half. Create a binding on a class
method, see that creating and configuring it patches nothing, apply
it, watch the stub answer, suspend, resume, remove. The context
manager form. `returns()`, `raises()`, and `transforms_result()` to
show the real method running with one thing changed.

- Format: notebook. Every step is a cell; checks read kernel state
  (the binding's repr, the method's result).

- Requires: wrapture only.

- Source: docs getting-started, "Your first binding".

- Length: 10 minutes.

- Not in the series as a post of its own, but every post assumes it,
  and it is the right place for the trust-building point that nothing
  happens until `apply()`.

### 2. `wrap-not-replace`: Testing by wrapping, not replacing

The unit testing post. The same tests written with `unittest.mock`
and with wrapture, one idea per page: a stub that is strict by
default (the drifted call), a call an object makes to itself, the
real method with one thing changed, and asserting on what did not
happen on an error path with `assert_never()` and `assert_order()`.
Ends with the decorator form as a preview of the pytest workshop.

- Format: terminal and files. The learner has `shop.py` and a test
  file, adds tests, runs `pytest` after each, and the check reads the
  pytest output. This is deliberately terminal-driven because the
  point is what a test can say, and a test is a file pytest runs.

- Requires: wrapture, pytest.

- Source: post "Unit testing with wrapture"; docs coming-from-mock.

- Length: 15 minutes.

### 3. `recording-calls`: Recording what real code did

The recording post, on the connection leak. Timeline and tape,
`tree()`, what one event holds, filters versus assertions versus
declared expectations, `children_of()` to name the culprit,
`stack="caller"` to name the line, `assert_order()`, nested timelines
instead of `reset_mock()`. Ends with the leak as a failing pytest test
that the learner fixes.

- Format: notebook. The final pytest run goes through an
  `execute-capture`, which runs in the workshop environment, and the
  check reads the captured output.

- Requires: wrapture, pytest.

- Source: post "Recording calls with wrapture"; docs
  example-resource-hygiene.

- Length: 15 minutes.

### 4. `phased-behaviour`: Behaviour that changes over time

The phases post. `then(after=n)` for a retry loop, `then(until=fn)`
for a circuit breaker, `returns_from()` for a polling loop and the
loud `SequenceExhaustedError`, `advance()` from outside and from
another binding's `validates_result()`.

- Format: notebook.

- Requires: wrapture.

- Source: post "Phased behaviour in wrapture"; docs monkey-patching,
  "Phased behaviour".

- Length: 15 minutes.

### 5. `beyond-callables`: Bindings that are not calls

The beyond callables post, trimmed. Attribute bindings with `on_get`
and `on_set` and the state-transition guard, value bindings with
`overrides()` and `hides()` on an environment variable and a module
constant, `mode="mapping"` on a settings dict held by reference, a
callable in a registry with `mode="callable"`, and one page on
generators: one event per iteration, `items`, and `MISSING` when the
consumer stops early. The iterator proxy is left to tier two.

- Format: notebook.

- Requires: wrapture.

- Source: post "Beyond callables in wrapture"; docs
  example-pinning-configuration.

- Length: 15 minutes.

### 6. `live-tracing`: A program that narrates itself

The live tracing post. The same three bindings, applied in the entry
point with no timeline, and a `Printer` sink. Card numbers appear in
the trace, so `capture=wrapture.redact("card")`. Then narrowing:
`Depth(1, ...)` at the sink, `when=` at the binding and the orphaned
children it leaves, `tree=True`, and `filtered_calls` to explain a
short trace.

- Format: terminal and files (`shop.py`, `orders.py`, `main.py`).
  Checks read the captured stderr of each run.

- Requires: wrapture.

- Source: post "Live tracing with wrapture"; docs ad-hoc-tracing.

- Length: 10 minutes.

### 7. `zero-code-tracing`: Tracing without touching the program

The zero-code post. Move the bindings and sink into `wrapture.toml`,
run `python -m wrapture main.py`, and see the same trace from an
unchanged program. Swap the sink to JSON Lines and read the file back
(with Python, since `jq` is not on Binder; see decisions), then
convert the three orders to a Mermaid sequence diagram, written
inside a fence to a Markdown file that a `layout` directive shows
rendered, the first picture of what the program did. Install
autowrapt and run with plain `python` under `AUTOWRAPT_BOOTSTRAP`.
Optionally the `applied.report()`, `suspend()` and `resume()` console
sequence, if a terminal action can drive `python -i` reliably.

- Format: terminal and files. The diagram page relies on JupyterLab's
  Markdown preview rendering a Mermaid fence, which JupyterLab 4.1 and
  later do; confirm it when the page is written.

- Requires: wrapture, autowrapt.

- Source: post "Zero-code tracing with wrapture"; docs ad-hoc-tracing,
  "Configuring from a file" and "Injection without a launcher".

- Length: 15 minutes.

### 8. `analysing-a-trace`: Analysing a trace in a notebook

A JSON Lines trace is data, and a notebook is where data goes. The
shop runs under a JSON Lines sink for a few hundred orders, then the
notebook reads the file with `load_events()`, puts the records in a
DataFrame, rebuilds the tree from `seq` and `parent_id`, computes
total and self time per path from the parent links (the same
arithmetic `tape.self_time()` does in a test), charts where the time
goes by path and the error count by path, and plots the latency
distribution of `place` across the run. Ends with a three-order trace
as a Mermaid sequence diagram from `mermaid()`, rendered in a Markdown
cell, and a `canonical()` snapshot of two runs compared as a diff.

- Format: notebook. The trace is produced by an `execute-capture`,
  which runs in the workshop environment, so no terminal is needed.

- Requires: wrapture, pandas, matplotlib.

- Source: docs ad-hoc-tracing, "Streaming to disk" and "Exporting
  traces to other tools"; example-request-timing, "Reading the time
  off the tree".

- Assumes: `zero-code-tracing`.

- Length: 15 to 20 minutes.

### 9. `tracing-flask`: One request as one tree

The Flask post. Why a binding on the WSGI callable is true and useless,
then one `[[instrument]]` entry from wrapture-instrumentation. The
learner starts the development server under the runner in one
terminal and sends four requests with `curl` from another: a quote,
an order, a declined order, and the missing item that shows a 500
with its `KeyError`. Then `ignore_paths` for the health check.

- Format: two terminals and files (`shop.py`, `webshop.py`,
  `templates/quote.html`, `wrapture.toml`).

- Requires: wrapture, wrapture-instrumentation, flask.

- Source: post "Tracing Flask with wrapture"; docs wsgi-tracing.

- Length: 15 minutes.

### 10. `finding-slow-code`: Where the time goes

The slow code post. A `time.sleep()` planted in `Ledger.record`, the
tree with times on it, self time versus total in
`tape.tree(times=True)`, and a test that asserts on
`tape.self_time()`. Then the `Aggregate` collector as a `[[window]]`
in the config, thirty requests from a loop, and the report file. One
page on `annotate()` to tag requests by tenant.

- Format: two terminals and files, plus one pytest run.

- Requires: wrapture, wrapture-instrumentation, flask, pytest.

- Source: post "Finding slow code with wrapture"; docs
  example-request-timing, scheduled-tracing.

- Length: 15 minutes.

### 11. `opentelemetry-export`: The same events, sent to a backend

The OpenTelemetry post. Add the `[otel]` table, run the Flask shop
with the console exporters, and read the spans: the SERVER span named
by route, the INTERNAL span beneath it, the exception on both, and the
metrics histograms after the export interval. No collector is needed.
A final optional page on distributed tracing using the
trace-propagation example, which is standard library only: two
processes, one trace id across both files.

- Format: two terminals and files.

- Requires: wrapture with the `otel` extra, wrapture-instrumentation,
  flask.

- Source: post "OpenTelemetry export in wrapture"; docs
  otel-export; examples trace-propagation.

- Length: 15 to 20 minutes.

## Tier two: one topic, in depth

### 12. `wrapture-with-pytest`: wrapture and pytest, properly

The topic the series gave lip service to. Scoping styles and why not
to mix them: the `with` block, `@wrapture.taped()` with
`@wrapture.bound()` and expectations on the decorator, yield fixtures
that hand the binding to the test for reconfiguring in flight, and
shared binding declarations at module scope applied per test. Then
the plugin: enable it from `conftest.py`, write a test that leaks a
binding and watch the sweep fail it by name, use the `tape` fixture
and see the tree attached to a failure report, and see what the
assertion rewriting prints for an `EventLog`. Ends with the `Counter`
query budget fixture from the ad-hoc tracing page, the one to leave
running under a whole suite.

- Format: terminal and files. Every page runs `pytest` and the check
  reads its output.

- Requires: wrapture, pytest.

- Source: docs unit-testing, "Scoping with ..." through "The pytest
  plugin"; ad-hoc-tracing, "Counting without retaining".

- Assumes: `wrap-not-replace` and `recording-calls`.

- Length: 20 minutes.

### 13. `coming-from-mock`: Converting a mock test suite

A small test module written entirely with `unittest.mock`, converted
one test at a time, with the suite green after each step. Each page is
one idiom from the comparison page: `return_value`, `side_effect` as
an exception, `side_effect` as a list, `patch.multiple`, `patch.dict`
and `monkeypatch.setenv`, `Mock(wraps=...)`, `assert_has_calls`, and
`caplog`. Ends with the case to leave as mock: a spec-less object
invented as it is touched.

- Format: terminal and files.

- Requires: wrapture, pytest.

- Source: docs coming-from-mock.

- Assumes: `wrap-not-replace`.

- Length: 20 minutes.

### 14. `supplying-stand-ins`: When the test must supply the callable

`stub()` for a hook the code under test receives, `mock(Spec)` for a
collaborator it is handed, both strict, both recorded on the same
tape. Opting a stub back into strictness, asserting across a batch,
failure paths reconfigured in place. The one deliberate opt-out from
wrap-not-replace, and where its limits are.

- Format: notebook.

- Requires: wrapture.

- Source: docs example-supplied-stand-ins; unit-testing, "Supplying a
  stand-in" and "A collaborator double".

- Assumes: `wrap-not-replace`.

- Length: 15 minutes.

### 15. `streaming-and-generators`: Testing what a consumer does with a stream

The paginated catalogue. One event per iteration and the live item
count, the iterator proxy with `on_item`, `on_finish`, `on_abandon`
and `on_error`, failing at page k, transforming items on the way
through, and the consumer-side proxy on an argument rather than a
result. Ends as a pytest test for a consumer that must cope with a
failed page.

- Format: notebook, one pytest page.

- Requires: wrapture, pytest.

- Source: docs example-streaming-data; monkey-patching, "Iterators
  and generators".

- Assumes: `beyond-callables`.

- Length: 15 minutes.

### 16. `testing-async-code`: Async methods and generators

Stubbing an async method so the outcome arrives on `await`, catching
the coroutine that was never awaited, concurrent sends on one tape,
an async generator with stubbed items. As a pytest suite with
pytest-asyncio.

- Format: notebook (the kernel supports top-level `await`), one
  pytest page.

- Requires: wrapture, pytest, pytest-asyncio.

- Source: docs example-async-code; monkey-patching, "Async targets".

- Assumes: `wrap-not-replace`.

- Length: 15 minutes.

### 17. `patching-third-party-code`: Changing what a library does

Monkey patching as a discipline. A library the learner cannot edit:
inject a header with `transforms_args()`, prove reversibility with
suspend, resume and remove, reconfigure the live patch, wrap the whole
call with `decorates()` for a retry, clamp an attribute the library
reads, apply before the library is imported with the post-import hook,
record calls without recording the token, and finally the same patch
from a config file with code in `wrapture_local/` beside it.

- Format: terminal and files.

- Requires: wrapture.

- Source: docs example-third-party-libraries; monkey-patching,
  "Patching a module before it is imported" and "Escape hatch".

- Assumes: `first-binding` and `live-tracing`.

- Length: 20 minutes.

### 18. `logs-blocks-and-notes`: Messages, phases and handled failures as events

`capture_logs()` and the assertion `caplog` cannot make (this call
logged it), `wrapture.block()` to name phases of an integration test
and `tape.within()`, `annotate()` to attach what the code knows, and
`note_exception()` for a failure the code handled itself. All inert
when nothing is listening, so safe to leave in application code, which
is what makes them spans later.

- Format: notebook.

- Requires: wrapture.

- Source: docs unit-testing, "Recording calls on a timeline"
  subsections, "Capturing log messages", "Declaring blocks of code".

- Assumes: `recording-calls`.

- Length: 15 minutes.

### 19. `sinks-and-collectors`: Where events go

The ad-hoc tracing guide beyond the printer. The sink protocol and a
sink of the learner's own in a few lines, fan-out, sampling and
filtering combinators, `Counter` and `Aggregate` registered in code,
`leaf=` and `category=`, and resolvers that decide the name and tags
per operation. Process versus scoped listening and what it costs when
nobody is listening.

- Format: terminal and files.

- Requires: wrapture.

- Source: docs ad-hoc-tracing, "Sinks" through "Writing your own
  sink".

- Assumes: `live-tracing`.

- Length: 20 minutes.

### 20. `trace-files-and-tools`: Reading a trace after the fact

JSON Lines as the durable form, from the command line. The pipeline
on two worker threads from the stream-to-disk example, one lane per
thread once `python -m wrapture.tools convert` has turned it into
Chrome trace JSON and Perfetto has opened it, the canonical form as a
golden file a test compares against, and output path templates and
rotation for a process that runs for days. The in-notebook analysis
and the Mermaid diagram belong to `analysing-a-trace`.

- Format: terminal and files.

- Requires: wrapture.

- Source: examples stream-to-disk; docs ad-hoc-tracing, "Streaming to
  disk", "Output paths and rotation", "Exporting traces to other
  tools".

- Assumes: `zero-code-tracing` and `analysing-a-trace`.

- Length: 15 minutes.

### 21. `watching-a-service-over-time`: Reports on a schedule

Windows. `Window` with `every=` in code, then `[[window]]` in config:
a minute's `Aggregate` summary on the minute, one file per run, and an
on-demand window opened with `kill -USR1`. The always-on JSON Lines
stream with `rotate=`. Clocks and restarts.

- Format: two terminals and files.

- Requires: wrapture, wrapture-instrumentation, flask.

- Source: docs example-service-over-time, scheduled-tracing.

- Assumes: `tracing-flask` and `finding-slow-code`.

- Length: 15 minutes. Schedules must be short enough to observe in a
  workshop; the self-test has to wait for them too.

### 22. `distributed-tracing`: One trace across two processes

The trace-propagation and detached-work examples. A client and a
server, standard library only, `trace_headers()` on the way out,
the WSGI boundary parsing `traceparent` on the way in, the join by
trace id across two files with no backend. Then work the caller does
not wait for: `detach()` and `handoff()`, and links instead of
nesting. Optionally with `[otel]` on both sides and the console
exporter showing the remote parent.

- Format: two terminals and files.

- Requires: wrapture, optionally the `otel` extra.

- Source: examples trace-propagation, detached-work; docs
  ad-hoc-tracing, "Trace identity and propagation", "Work the caller
  does not wait for".

- Assumes: `zero-code-tracing` and `opentelemetry-export`.

- Length: 20 minutes.

### 23. `testing-web-requests`: Requests in tests, and at the boundary

`wrapture.instrumentation("flask")` inside a test, the request event
and its `data`, asserting on requests, and the `on_request` namespace:
a canned response without calling the application, a fault the server
sees, rewriting a status on the way out. ASGI is left to the FastAPI
workshops planned later.

- Format: terminal and files with pytest.

- Requires: wrapture, wrapture-instrumentation, flask, pytest.

- Source: docs wsgi-tracing, "The on_request namespace" and "Asserting
  on requests in tests"; asgi-tracing.

- Assumes: `tracing-flask` and `wrapture-with-pytest`.

- Length: 15 minutes.

### 24. `writing-instrumentation`: Instrumenting a package nobody has covered

An `Instrumentation` class for a small library in the workshop
directory: the shape, hooks that run when the target is imported,
declared settings validated when the config loads, `on_cleanup()` so
the patch comes down with the config, and the class named by
reference from `[[instrument]]` with `pythonpath`. The flask-app
example's local class is the model. How it would be packaged with an
entry point.

- Format: terminal and files.

- Requires: wrapture.

- Source: docs instrumentation-packages; examples operator-code,
  flask-app.

- Assumes: `zero-code-tracing` and `tracing-flask`.

- Length: 20 minutes.

## Candidates left out, for now

- **FastAPI and ASGI** as workshops of their own, later: tracing a
  FastAPI application from one `[[instrument]]` entry (the mechanism
  is the Flask one with different choke points), and the ASGI side of
  `testing-web-requests`. Never as a track inside the Flask
  workshops; the FastAPI example in the wrapture repository is the
  source when they are written.

- **Manual setup** (gunicorn, mod_wsgi). Deployment specific, and
  neither server belongs in a workshop environment.

- **Pinning configuration** as a separate workshop. Covered by
  `beyond-callables` and the fixture shape in `wrapture-with-pytest`.

- **Design concepts and philosophy.** Reading, not doing. The README
  and each workshop's welcome page can link to them.

## Decisions that cut across the workshops

**One collection.** One ordered collection holds both tiers, with
the tiers as a visible break in the numbering. Splitting into two
collections in a catalog can be revisited later; nothing in the
workshops depends on it.

**Format per workshop.** Notebook where the check is about kernel
state, what a binding or a tape holds; terminal and files where the
check is a pytest run, a config file or a running server. A workshop
picks one and does not mix them, because the two formats have
different Python environments (see the extension features section).
Each notebook workshop declares `install-packages` and an
`environment` with a `requirements.txt`, so the extension builds the
venv under `_workshop/venv` and registers the kernel. Each terminal
workshop has the learner create `.venv` inside the workshop directory
with `python -m venv` and install with pip. Both pin wrapture to the
submodule's tag. In neither case does anything land outside the
workshop directory.

**Shipped code versus typed code.** Workshops ship the code under test
as files in the workshop directory and have the learner write only the
wrapture parts: the binding, the test, the config entry. A learner
types what they are there to learn and not the shop. Where a post edits
application code (the tenant hook in `finding-slow-code`, the `finally`
fix in `recording-calls`), the workshop uses a file edit action with a
check.

**Versions.** wrapture is pinned to 1.0.0a22 everywhere. Every feature
the posts use exists at that tag (`self_time`, `Aggregate`, `annotate`,
`trace_headers`, `detach`), which I checked in the source. 1.0.0a22
added `explain()` on bindings and behaviours and the `configured` word
in a binding's repr, which `first-binding` shows and the later
workshops can lean on when a binding's behaviour is not in view.
wrapture-
instrumentation's compatible version needs confirming on PyPI before
`tracing-flask` is written, as does whether its Flask target's
`ignore_paths` and `lifecycle` settings match the post. autowrapt and
pytest-asyncio are only installed by the workshops that use them.

**Platform.** linux and macos. Windows is not declared: several
workshops use `curl`, `kill -USR1`, two terminals and
`AUTOWRAPT_BOOTSTRAP=... python`, and the venv activation differs.
Revisit per workshop if there is demand.

**No jq.** Binder does not have it and a learner need not. Where a
post uses `jq` on a JSON Lines file, the workshop uses a short Python
one-liner or a notebook cell. Same result, fewer assumptions.

**Wheelhouse on Binder.** The Binder image downloads every workshop's
requirements, and ipykernel, into a wheelhouse under the home directory
at build time and points pip at it with `find-links` in a user pip
config, so an environment step installs from disk rather than PyPI. It
is never `no-index`: learners can install packages of their own, and a
workshop whose requirements are missing from the wheelhouse still
works, only more slowly. The config exists only in the image, so
nothing in a workshop refers to it and local checkouts are unaffected.
Environments are not pre-built in the image: each would add its own
copy of ipykernel and its dependencies, and image size is paid on
every launch.

**Ports.** Servers bind explicit ports above 5000 to stay clear of
macOS AirPlay, one distinct port per workshop so two workshops opened
in one session do not collide.

**Checks.** Every page ends with something checkable, on the
substrate its format allows (see the extension features section).
Checks say what is wrong rather than that something is:
"wrapture.toml has no [[sink]] entry" rather than "config incorrect".
A `hint` block beside a check says what to look at when it fails.

**Self-test time.** Each workshop must self-test on CI. The self-test
stops an action after 300 seconds and the whole run after 1200 by
default, and environment creation and pip installs count, so the
workshops that install Flask or the OpenTelemetry extra pass a longer
`--timeout` through `just test` and in CI. Workshops that wait on a
schedule (`watching-a-service-over-time`) or an export interval
(`opentelemetry-export`) keep those intervals at a few seconds.

**No tracks.** The extension supports a track chosen by the learner
(`tracks` in the manifest, a `choice` with `:track: true`, pages with
`when: track == ...`). The workshops here never use it. A variant
that wants different pages, FastAPI beside Flask for instance, is a
separate workshop, which keeps each one small and lets the self-test
cover every page.

**The shop code.** One canonical `shop.py`, the live tracing post's
version with cards and tenants, copied into every workshop that uses
it rather than shared, because each workshop must be self-contained.
Earlier workshops that need the simpler version (no card) get that
version; the difference is noted on the welcome page so a learner is
not surprised by the signature change.

## Extension features the workshops use

The patterns settled from the extension's documentation in
`reference/jupyterlab-workshop/docs`, so each workshop does not
rediscover them. The authoring skill covers the syntax; this records
the choices.

**Two formats, two Python environments.** In a notebook workshop the
`environment` kernel is also the hidden workshop kernel behind kernel
verifies, `execute-capture` and `kernel-execute` without a path, so a
check can import wrapture and inspect the learner's objects, and a
pytest run through `execute-capture` uses the workshop venv. In a
terminal workshop the hidden kernel is the server's Python, which has
no wrapture, and the learner's `.venv` is invisible to it. Checks
there use the `shell` substrate (a command run in the workshop
directory, exit code decides, output is the message), such as the
venv's pytest with `-q`, or `contents` predicates on files. A kernel
check in a terminal workshop must never import wrapture.

**Notebook pages.** The welcome page creates the notebook with
`notebook-create` on the environment's kernel; each later step is one
`cell-insert` with a tag and `:run: true`, so a page reads as prose,
cell, check. The check is a `learner-kernel` verify, an expression
evaluated in the learner's own kernel, triggered by `cell-executed
<tag>`, asking the question directly: is the binding applied, how
many events are on the tape, what did the stub return. Pages gate on
those verifies with `requires`.

**Terminal pages.** One named session per role (`shell`, `server`,
`client`), declared in the layout so the actions and the layout share
one shell. The venv is created and activated in the `shell` session
on the welcome page, and every later `execute` in that session
inherits it. Commands run from the workspace; `:cwd:` only applies
when a session first starts. A check on a pytest run uses the `shell`
substrate and the venv's own interpreter by path (`.venv/bin/python -m
pytest`), since the hidden kernel is not activated, and reports
pytest's summary line on success and its full output on failure.

**Long-running servers.** The self-test gives every `execute` that
sets no `wait` a `wait: prompt` and fails it after the action timeout
when the prompt never comes back, which a server never does. A server
is started in its own session with an explicit `:wait:` of a few
seconds, its readiness is a verify that retries an HTTP request, the
requests come from the `client` session or an `execute-capture`, and
the page ends with an `interrupt` on the server session so the next
page and the self-test start clean. Every server binds an explicit
port above 5000, one per workshop.

**Layouts.** Each workshop declares one: the instructions on the
right, the file under study or the notebook on top, the terminals at
the bottom. A two-terminal workshop puts `server` and `client` side
by side. Layouts apply on first open and from a launch link, which
includes Binder and the self-test.

**Shipped files and edits.** The code under test ships under `files/`,
which the extension copies into the workspace (`work/`) when the
workshop first opens, so it is there from the start and Restart puts it
back without touching the pages. Where placing a file is a step worth
seeing, `file-write` with `:from:` copies it from `files/` instead. Small edits, the `finally` fix or the tenant hook, are
`editor-replace` actions with a verify triggered by `file-saved`. A
named `checkpoint` before a fix lets a page offer to put the bug
back.

**Variables and conditions.** Captured output (`execute-capture`,
`kernel-execute` with `:capture:`) is shown in prose with `{var}` and
read by checks. Variable names say what they hold (`trace_file`, not
`path`), since each is exported to the terminals in upper case and
`path`, `pythonpath`, `term` and the like would replace the real
ones. `{when} host == "binder"` carries the note that the session is
temporary; `container` gates advice about installing freely.

**Manifest.** `env` sets `PAGER: cat` and `PYTHONUNBUFFERED: "1"` so
server output appears as it happens. `requires.tools` names `curl`
with install hints where a workshop uses it. `duration` and `tags`
are filled in, `gating` is `soft`, and `finish` names the next
workshop in the sequence. A `quiz` closes a page that has nothing
else checkable, such as reading a trace; the self-test answers it
correctly.

**Ordered collection.** `jupyter workshop index` is run with
`--ordered`, which numbers the workshops in the browser and makes
each Finish dialog offer the next; the Justfile passes it.

**JupyterLite** is not a target. It has no package installs and no
subprocess, and wrapt's extension does not run under Pyodide, so
`lite` is never listed as a platform.

## Status

Not the collection order. The writing order learns the format on the
simplest workshops and gets the shared assets right before the
workshops that depend on them: `first-binding` settles the notebook
format, the environment manifest and kernel checks; `wrap-not-replace`
settles the terminal format, the venv step and shell checks on a
pytest run; `live-tracing` adds captured-output checks and a running
server; then the core of the testing arc, then the tracing arc once
the wrapture-instrumentation version is confirmed; then tier two,
starting with `wrapture-with-pytest` and `coming-from-mock` since they
serve the stated audience most directly.

Each workshop is scaffolded, written, linted clean, self-tested,
indexed and added to the README before the next starts. Status is one
of: planned, in progress, written (lint clean), tested (self-test
green), or published (indexed and in the README).

| # | Workshop | Status |
|---|----------|--------|
| 1 | `first-binding` | published (indexed, in the README, self-test green) |
| 2 | `wrap-not-replace` | published (indexed, in the README, self-test green) |
| 3 | `recording-calls` | planned |
| 4 | `phased-behaviour` | planned |
| 5 | `beyond-callables` | planned |
| 6 | `live-tracing` | planned |
| 7 | `zero-code-tracing` | planned |
| 8 | `analysing-a-trace` | planned |
| 9 | `tracing-flask` | planned |
| 10 | `finding-slow-code` | planned |
| 11 | `opentelemetry-export` | planned |
| 12 | `wrapture-with-pytest` | planned |
| 13 | `coming-from-mock` | planned |
| 14 | `supplying-stand-ins` | planned |
| 15 | `streaming-and-generators` | planned |
| 16 | `testing-async-code` | planned |
| 17 | `patching-third-party-code` | planned |
| 18 | `logs-blocks-and-notes` | planned |
| 19 | `sinks-and-collectors` | planned |
| 20 | `trace-files-and-tools` | planned |
| 21 | `watching-a-service-over-time` | planned |
| 22 | `distributed-tracing` | planned |
| 23 | `testing-web-requests` | planned |
| 24 | `writing-instrumentation` | planned |

## Known blockers

- None at present. The first workshop turned up seven problems in
  jupyterlab-workshop 0.1.15 (silent `learner-kernel` checks, no
  kernelspec refresh after `environment-create`, kernelspecs left
  behind by the self-test, the environment banner and action not
  knowing about each other, Restart reverting page edits, the last run
  cell's output not saved, the open workshop restored across servers),
  all fixed in 0.1.16. Moving to it found three more (the self-test
  restoring the user's JupyterLab workspace into the run, notebook
  actions not scrolling to the cell they act on, and the harness dying
  when its output goes through a pipe), all fixed in 0.1.17. The gaps
  in the authoring skill that the same two workshops exposed were
  filled in 0.1.18, which the project now pins.

## Open questions

Decisions not yet taken. Remove each as it is settled and record the
answer in the section it belongs to.

- None at present.
