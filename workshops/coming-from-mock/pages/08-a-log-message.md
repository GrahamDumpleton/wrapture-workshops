---
title: A log message
requires: [verify:logs]
---

# A log message

The comparison extends one step past `unittest.mock`, to pytest's
`caplog` fixture, because the shape is the same. `caplog` attaches a
handler at the root logger and hands the test a flat list of records,
so the strongest assertion it supports is "this message was logged at
some point during the test". wrapture's `capture_logs()` records
messages as events on the same tape as the calls, which keeps the flat
assertion one line and adds the one `caplog` cannot express: the
warning was logged by this call, not merely somewhere during the test.

```{editor-replace}
:id: convert-caplog
:path: test_shop.py
:regex: true
:match: ^def test_declined_is_logged_with_caplog\(.*\n(?:    .*\n)+
def test_declined_is_logged_with_wrapture():
    charge = wrapture.binding(Gateway, "charge")
    logs = wrapture.capture_logs("shop")
    with wrapture.timeline(charge, logs) as tape:
        with pytest.raises(CardDeclined):
            OrderService().place(250, DECLINED, tenant="globex")
        warning = logs.events.at_level("WARNING").with_message("*declined*").assert_once()[0]
        assert tape.parent_of(warning) is charge.events.first

```

```{execute}
:id: run-logs
:session: shell
:wait: prompt
pytest -q test_shop.py
```

The capture hears each record on the logger that emitted it, before
propagation, so a library that sets `propagate = False` is captured
the same as any other, with no handler configuration touched. The
`logging` import at the top of the file is now unused, and so is the
`caplog` fixture; the last page tidies the imports.

```{verify}
:id: logs
:label: The log test is converted and the suite is green
:substrate: shell
:trigger: after:run-logs; file-saved test_shop.py
out=$(.venv/bin/python -m pytest -q --color=no test_shop.py 2>&1) && printf '%s\n' "$out" | grep -q '10 passed' && ! grep -q -E '^def (test_declined_is_logged_with_caplog)\(' test_shop.py && [ "$(grep -c -E '^def (test_declined_is_logged_with_wrapture)\(' test_shop.py)" = "1" ] && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; grep -E '^def (test_declined_is_logged_with_caplog|test_declined_is_logged_with_wrapture)\(' test_shop.py | sed 's/^/still in the file: /'; exit 1
```
