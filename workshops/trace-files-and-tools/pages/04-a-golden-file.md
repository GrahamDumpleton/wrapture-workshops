---
title: A golden file
requires: [verify:snapshot-passes, verify:refactor-caught, verify:snapshot-restored]
---

# A golden file

`canonical` renders the call tree as a deterministic text
fingerprint: kind and path per line, indented by nesting, `!!` with
the exception type for failures, `(injected)` for outcomes supplied
by behaviour. Everything unstable between runs, sequence numbers,
timings, captured values and thread identity, is left out, so the
same code produces the same text.

```{execute}
:id: run-canonical
:session: shell
:wait: prompt
python -m wrapture.tools convert --format canonical -o golden.txt trace.jsonl && head -n 9 golden.txt
```

```
call pipeline:process
  call pipeline:fetch
  call pipeline:transform
  call pipeline:store
  call pipeline:transform
  call pipeline:store
  call pipeline:transform
  call pipeline:store
call pipeline:process
```

Snapshot it once and a refactor that silently changes what calls what
fails the comparison as a diff a reviewer can read. This is the
complement to `assert_order()`: the assertion states the rules you
thought of, the snapshot catches the changes you did not. The test
records the four sources on a tape and compares `canonical(tape)`
with the file; `discover()` binds every function in the module by
pattern.

```{file-write}
:id: write-test
:path: test_pipeline.py
:open: true
from pathlib import Path

import wrapture

import pipeline

SOURCES = ["alpha", "beta", "gamma", "delta"]


def test_the_pipeline_still_calls_what_it_called():
    calls = wrapture.discover(pipeline, "*")

    with wrapture.timeline(calls) as tape:
        for source in SOURCES:
            pipeline.process(source)

    assert wrapture.canonical(tape) == Path("golden.txt").read_text().rstrip("\n")
```

```{execute}
:id: run-test
:session: shell
:wait: prompt
pytest -q test_pipeline.py
```

```{verify}
:id: snapshot-passes
:label: The live call tree matches the golden file
:substrate: shell
:trigger: after:run-test
out=$(.venv/bin/python -m pytest -q --color=no test_pipeline.py 2>&1) && printf '%s\n' "$out" | grep -q '1 passed' && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; exit 1
```

Now the refactor nobody reviewed. Someone decides the transform is
redundant and stores the raw item.

```{editor-replace}
:id: break-pipeline
:path: pipeline.py
:match: store(transform(item))
store(item)
```

```{execute}
:id: run-test-broken
:session: shell
:wait: prompt
pytest -q test_pipeline.py
```

The assertion fails with a diff: every `call pipeline:transform` line
the golden file expects is missing from the live tree. Nothing about
the program's output changed, twelve items still come out, and the
snapshot caught the change in shape anyway.

```{verify}
:id: refactor-caught
:label: The snapshot fails on the missing transform calls
:substrate: shell
:trigger: after:run-test-broken
out=$(.venv/bin/python -m pytest -q --color=no test_pipeline.py 2>&1); printf '%s\n' "$out" | grep -q '1 failed' && printf '%s\n' "$out" | grep -q 'pipeline:transform' && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; exit 1
```

Put the transform back and confirm the snapshot passes again.

```{editor-replace}
:id: restore-pipeline
:path: pipeline.py
:match: store(item)
store(transform(item))
```

```{execute}
:id: run-test-restored
:session: shell
:wait: prompt
pytest -q test_pipeline.py
```

```{verify}
:id: snapshot-restored
:label: The restored pipeline matches the golden file again
:substrate: shell
:trigger: after:run-test-restored
out=$(.venv/bin/python -m pytest -q --color=no test_pipeline.py 2>&1) && printf '%s\n' "$out" | grep -q '1 passed' && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If a check fails
`golden.txt` must be rendered from the one-run trace of the earlier
pages, and `test_pipeline.py` must call `pipeline.process` through
the module so the bound function is the one that runs. The second
check expects `pipeline.py` to read `store(item)`; the third expects
`store(transform(item))` again. Open the file to see which it says.
```
