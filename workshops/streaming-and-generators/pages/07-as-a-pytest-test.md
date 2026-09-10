---
title: As a pytest test
requires: [verify:test-passes]
---

# As a pytest test

The same moves as a test file, with `fail_at` from the helper module.
The test builds its own proxy, so the failure counter starts fresh,
and the timeline scopes the binding so nothing stays applied
afterwards. The consumer's error handling is asserted against a
failure that arrived in the middle of a real iteration: the rows
written before it survive, `raising()` confirms the recorded event
carries the injected `OSError`, and `fetched` confirms the catalogue
was never asked for a third page.

```{file-write}
:id: write-test
:path: test_catalogue.py
:open: true
import pytest
import wrapture

from catalogue import Catalogue, Exporter
from helpers import fail_at


@pytest.fixture
def catalogue():
    records = [{"id": n, "name": f"item-{n}"} for n in range(1, 6)]
    return Catalogue(records)


def test_exporter_keeps_rows_written_before_a_failure(catalogue):
    flaky = wrapture.iterator()
    flaky.on_item.validates_item(fail_at(2, OSError("connection reset")))

    pages = wrapture.binding(Catalogue, "pages").on_call.transforms_result(flaky)

    with wrapture.timeline(pages):
        out = []
        assert Exporter().write(catalogue.pages(), out) == 2

        pages.events.raising(OSError).assert_once()

    assert out == ["1,item-1", "2,item-2"]
    assert catalogue.fetched == 2
```

The workshop environment has pytest installed, so run the test from
the notebook.

```{cell-insert}
:id: insert-pytest
:path: {{ notebook }}
:tags: [pytest]
:run: true
!python -m pytest -q --color=no test_catalogue.py
```

```{verify}
:id: test-passes
:label: The exporter test passes
:substrate: shell
:trigger: after:insert-pytest; cell-executed pytest
out=$(python -m pytest -q --color=no test_catalogue.py 2>&1) && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the test fails
`test_catalogue.py` must be in this directory, next to `catalogue.py`
and `helpers.py`. A `fetched` of 3 means the failure was not
injected, so check that the proxy is handed to `transforms_result()`
and that `fail_at` is given position 2.
```
