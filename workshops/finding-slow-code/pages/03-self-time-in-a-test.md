---
title: Self time in a test
requires: [verify:test-passes]
---

# Self time in a test

In a test, `tape.tree(times=True)` prints both figures and
`tape.self_time()` gives it for one event, so the same observation can
be turned into an assertion that will catch the next regression. The
`wrapture.instrumentation("flask")` context applies the same Flask
instrumentation the config file named, scoped to the block, and the
timeline records what the three bindings see.

```{file-write}
:id: write-test
:path: test_timing.py
:open: true
import wrapture

from shop import Gateway, Ledger, OrderService
from webshop import app


def test_where_the_time_goes():
    place = wrapture.binding(OrderService, "place", capture=wrapture.redact("card"))
    charge = wrapture.binding(Gateway, "charge", capture=wrapture.redact("card"))
    record = wrapture.binding(Ledger, "record")

    with wrapture.instrumentation("flask"), wrapture.timeline(place, charge, record) as tape:
        client = app.test_client()
        response = client.post("/order", json={"amount": 500, "card": "4111-1111-1111-1111", "tenant": "acme"})
        assert response.status_code == 200

        print()
        print(tape.tree(times=True))

        order = place.events.assert_once()[0]
        ledger = record.events.assert_once()[0]
        assert tape.self_time(order) < 0.1 * order.duration
        assert tape.self_time(ledger) > 0.9 * order.duration
```

Run it with `-s` so the tree it prints is shown.

```{execute}
:id: run-test
:session: shell
:wait: prompt
pytest -q -s test_timing.py
```

```
shop:OrderService.place(amount=500, card='<redacted>', tenant='acme')  -> {'id': 'ch_500', 'amount': 500}  [31.0ms, self 173us]
  shop:Gateway.charge(amount=500, card='<redacted>')  -> {'id': 'ch_500', 'amount': 500}  [7us]
  shop:Ledger.record(entry={'id': 'ch_500', 'amount': 500})  -> 'led_ch_500'  [30.8ms]
```

The service spent 173us of its 31.0ms doing anything itself. No
external profiler can produce that number for an arbitrary handful of
methods, because a profiler only sees whole call stacks; wrapture can,
because the events know their parents. The two assertions say the
service's own share is under a tenth of the order and the ledger's is
over nine tenths, and a fix that moved the cost somewhere else, or a
regression that added a second slow layer, fails one of them with a
number attached.

```{verify}
:id: test-passes
:label: The timing test passes
:substrate: shell
:trigger: after:run-test
out=$(.venv/bin/python -m pytest -q --color=no test_timing.py 2>&1) && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check runs `test_timing.py` with the venv's pytest and shows its
output. An `ImportError` on `webshop` means the test is not in this
directory; a failing self-time assertion means `shop.py` has been
changed, so the ledger is no longer where the time goes.
```
