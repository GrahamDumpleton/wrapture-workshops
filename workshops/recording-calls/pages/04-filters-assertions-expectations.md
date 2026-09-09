---
title: Filters, assertions, expectations
requires: [verify:assertion-shown]
---

# Filters narrow, assertions conclude

One naming rule holds across the whole package. A method whose name
starts with `assert_` raises immediately, one starting with `expect_`
declares a claim that is checked when the scope closes, and everything
else returns data. A mistyped assertion name is an `AttributeError`
rather than the silent pass that mock's `assert_calld_once` was famous
for.

Filters chain and never raise: `with_args()`, `with_instance()`,
`raising()`, `returning()` and `matching()`. Assertions conclude:
`assert_never()`, `assert_once()`, `assert_times()`, `assert_at_least()`
and `assert_at_most()`. Each prints the events it looked at on failure.
Assert two closes, which passes, then three, which does not.

```{cell-insert}
:id: insert-assert
:path: {{ notebook }}
:tags: [assert]
:run: true
with wrapture.timeline(connect, close):
    report(Repository(Database()), [1, 2])
    close.events.assert_times(2)
    try:
        close.events.assert_times(3)
    except AssertionError as exc:
        failure = str(exc)

print(failure)
```

An assertion is written where it runs. An expectation is the same
claim declared on the binding up front, before the run, and verified
when the timeline exits.

```{cell-insert}
:id: insert-expect
:path: {{ notebook }}
:tags: [expect]
:run: true
strict_close = wrapture.binding(Connection, "close").expect_times(3)

try:
    with wrapture.timeline(connect, strict_close):
        report(Repository(Database()), [1, 2])
except wrapture.ExpectationNotMetError as exc:
    print(exc)
```

`ExpectationNotMetError` derives from `AssertionError`, so test
frameworks report it as a failure. Expectations read as a contract at
the top of a test with the body free of bookkeeping, and an expectation
with nothing recording is an error rather than a pass.

```{verify}
:id: assertion-shown
:label: The failing assertion reported two closes
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-expect; cell-executed expect
"got 2" in failure and "pooled:Connection.close" in failure
```
