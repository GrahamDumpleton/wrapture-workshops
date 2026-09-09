---
title: What did not happen
requires: [verify:error-path, quiz:absence]
---

# What did not happen

The tests that matter most are usually on the error paths, and the
interesting fact on an error path is often an absence. When the ledger
write fails, the refund must be issued and the notification must not
be sent. The mock version, the fourth test in the file, takes three
doubles to write. Look at its refund assertion.

```{editor-highlight}
:path: test_orders.py
:match: gateway.refund.assert_called_once_with
:duration: 4s
```

Because the gateway is a mock, the charge id is a fabricated
`MagicMock` rather than `"ch_500"`, so the only way to assert on it is
to ask the mock what it invented. The test cannot say "the refund was
for the charge that was taken", only "the refund was passed whatever
`charge()` returned".

With wrapture the failure is injected at the ledger and nothing else is
touched. Four bindings, one with behaviour, three there to be watched.

```{file-write}
:id: write-error-path-test
:path: test_orders.py
:mode: append
:open: true



def test_error_path_with_wrapture():
    charge = wrapture.binding(Gateway, "charge")
    refund = wrapture.binding(Gateway, "refund")
    record = wrapture.binding(Ledger, "record")
    send = wrapture.binding(Notifier, "send")

    record.on_call.raises(OSError("disk full"))

    with wrapture.timeline(charge, refund, record, send) as tape:
        with pytest.raises(OSError):
            OrderService().place(500)

        refund.events.with_args(charge_id="ch_500").assert_once()
        send.events.assert_never()
        tape.assert_order(charge, record, refund)

    print(tape.tree())
```

```{execute}
:id: run-error-path
:session: shell
:wait: prompt
pytest -q -s test_orders.py -k error_path_with_wrapture
```

The real gateway was charged, so the refund is asserted against the
real charge id. The notifier is real and was never called.
`assert_order()` says the refund came after the failed ledger write,
across three different bindings. The tree shows exactly that: the
charge, the record marked as an injected failure, then the refund.

```{verify}
:id: error-path
:label: The refund was for the real charge and nothing was sent
:substrate: shell
:trigger: after:run-error-path
out=$(.venv/bin/python -m pytest -q --color=no test_orders.py -k error_path_with_wrapture 2>&1) && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; exit 1
```

````{hint}
:title: What a failing assertion shows
Asserting on a refund for the wrong id does not just say the count was
wrong. It shows what was recorded, and what the filter discarded:

```
AssertionError: expected exactly 1 event(s), got 0
<EventLog orders:Gateway.refund[charge_id='ch_999']: 0 event(s)>
    (no events)
  filtered from:
    <EventLog orders:Gateway.refund: 1 event(s)>
        orders:Gateway.refund(charge_id='ch_500')
```

An over-narrowed filter producing an empty log is the easiest way to
get a wrong assertion, and seeing what it discarded is the fastest way
to notice.
````

```{quiz}
:id: absence
:title: What the mock version could not say
question: Which of these can the wrapture test assert that the mock version cannot?
options:
  - { text: "The refund was for ch_500, the charge that was really taken", correct: true }
  - { text: "The ledger write raised OSError", explanation: "Both versions inject that failure and see it propagate." }
  - { text: "The notifier was not called", explanation: "assert_not_called() says that too. What it cannot say is that the real notifier, not a double, was never reached." }
explanation: With the gateway real, the charge id is real, so the refund is asserted against the charge that was taken rather than against whatever a mock invented.
```
