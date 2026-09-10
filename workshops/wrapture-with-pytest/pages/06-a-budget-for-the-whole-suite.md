---
title: A budget for the whole suite
requires: [verify:budget-exceeded, verify:all-green]
---

# A budget for the whole suite

Not every question needs the events themselves; often a number is the
answer. `Counter` counts operations as they begin and keeps nothing
else, and it asks for no argument or result values, so when it is the
only thing listening the recording skips value capture entirely. That
makes it cheap enough to leave running under a whole suite, which is
how the classic N+1 query regression gets caught: bind the database
layer's entry point once, register a counter, and give every test a
query budget.

The binding is applied in `pytest_configure`, once for the session,
and the sweep respects it because it was already applied when each
test began. The autouse fixture reads the count before and after each
test.

```{file-write}
:id: write-budget-conftest
:path: conftest.py
:open: true
import pytest
import wrapture

from database import Database

pytest_plugins = ["wrapture.pytest_plugin"]

queries = wrapture.Counter()


def pytest_configure(config):
    wrapture.binding(Database, "execute").apply()
    wrapture.add_sink(queries)


@pytest.fixture(autouse=True)
def query_budget():
    before = queries.count
    yield
    used = queries.count - before
    assert used <= 2, f"test issued {used} queries; N+1 regression?"
```

A test of the repository's totals asserts on the result alone, which
is all a test of a query usually can see.

```{file-write}
:id: write-budget-test
:path: test_budget.py
:open: true
from database import Database, Repository


def test_totals_per_tenant():
    assert Repository(Database()).totals() == {"acme": 1450, "globex": 120, "initech": 170}
```

```{execute}
:id: run-budget
:session: shell
:wait: prompt
pytest -q test_budget.py
```

The result is right, and the test still errors at teardown:

```
AssertionError: test issued 4 queries; N+1 regression?
```

One query listed the three tenants and one more ran per tenant.
{open}`database.py` can answer that in a single query, so rewrite
`totals()` to ask for every tenant's amounts at once and add them up
in Python.

```{verify}
:id: budget-exceeded
:label: The budget fixture reports the four queries
:substrate: shell
:trigger: after:run-budget
out=$(.venv/bin/python -m pytest -q --color=no test_budget.py 2>&1); printf '%s\n' "$out" | grep -q 'test issued 4 queries; N+1 regression?' && { echo "test_totals_per_tenant issued 4 queries against a budget of 2"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check runs `test_budget.py` and expects the budget fixture's
error naming four queries. A pass means `totals()` has already been
rewritten; no mention of queries means `conftest.py` does not have
the counter, the `pytest_configure` hook and the autouse fixture from
the step above.
```

```{editor-replace}
:id: fix-totals
:path: database.py
:regex: true
:match: ^    def totals\(self\):\n(?:        .*\n)+
    def totals(self):
        totals = {}
        for tenant, amount in self.database.execute("SELECT tenant, amount FROM orders"):
            totals[tenant] = totals.get(tenant, 0) + amount
        return totals

```

Run the whole suite this time, every file from every page.

```{execute}
:id: run-all
:session: shell
:wait: prompt
pytest -q
```

Eleven pass, the budget test among them with one query, and the
counter charged the other ten tests nothing for the guarantee. A test
that quietly starts issuing a query per row now fails with a number
attached.

```{verify}
:id: all-green
:label: The whole suite passes, the totals test within its budget
:substrate: shell
:trigger: after:run-all; file-saved database.py
out=$(.venv/bin/python -m pytest -q --color=no 2>&1) && printf '%s\n' "$out" | grep -q '11 passed' && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check runs every test file in this directory and expects eleven
passes. A budget error means `totals()` in `database.py` still issues
a query per tenant; a failure elsewhere names the file, and the page
that wrote it says what it should contain.
```
