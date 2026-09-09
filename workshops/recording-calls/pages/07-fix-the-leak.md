---
title: Fix the leak
requires: [verify:leak-fixed]
---

# The leak as a failing test

In a test the pairing becomes the assertion, and the failure message
carries the leaked connections and where each was acquired. `close` is
given a declared expectation of at least one call, so a path that
acquires nothing at all cannot pass by accident.

```{file-write}
:id: write-test
:path: test_pooled.py
:open: true
import wrapture

from pooled import Connection, Database, Repository, report


def test_find_releases_its_connection():
    connect = wrapture.binding(Database, "connect", stack="caller")
    close = wrapture.binding(Connection, "close").expect_at_least(1)

    with wrapture.timeline(connect, close):
        report(Repository(Database()), [1, 2])

        released = {event.instance for event in close.events}
        leaked = []
        for event in connect.events:
            if event.result not in released:
                frame = wrapture.stack_frames(event.stack)[0]
                leaked.append(f"{event.result} acquired at line {frame.lineno} in {frame.function}")

        assert not leaked, f"connections left open: {leaked}"
```

The workshop environment has pytest installed, so run the test from
the notebook.

```{cell-insert}
:id: insert-pytest-before
:path: {{ notebook }}
:tags: [pytest-before]
:run: true
!python -m pytest -q --color=no test_pooled.py
```

It fails today, naming the second connection and the line inside
`find()`. Fix the early return: release in a `finally`, as `count()`
does, so every path out of `find()` closes the connection. The action
below rewrites the body of `find()` in `pooled.py` and saves it.

```{editor-replace}
:id: fix-find
:path: pooled.py
:line: 48-53
        connection = self.database.connect()
        try:
            rows = connection.execute(f"SELECT * FROM {table} WHERE id = {key}")
            if not rows:
                return None
            return rows[0]
        finally:
            connection.close()
```

Run the test again. pytest imports the module afresh, so it sees the
fix even though the notebook's kernel still holds the old code.

```{cell-insert}
:id: insert-pytest-after
:path: {{ notebook }}
:tags: [pytest-after]
:run: true
!python -m pytest -q --color=no test_pooled.py
```

```{verify}
:id: leak-fixed
:label: find() releases its connection and the test passes
:substrate: shell
:trigger: after:insert-pytest-after; cell-executed pytest-after; file-saved pooled.py
out=$(python -m pytest -q --color=no test_pooled.py 2>&1) && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the test still fails
Look at `find()` in `pooled.py`: the `connect()` call comes first, the
query and both returns sit inside `try`, and `connection.close()` is in
the `finally`. Save the file and run the test cell again.
```
