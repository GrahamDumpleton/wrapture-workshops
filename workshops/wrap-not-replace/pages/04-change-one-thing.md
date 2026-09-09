---
title: Change one thing
requires: [verify:pinned-result]
---

# Change one thing

This is where substitution runs out of road. `Mock(wraps=real)` forwards
calls to the real method, but it cannot change the arguments the real
method receives and cannot touch the result on the way back. The
standard library has no way to say "run the real method, but change
one thing about it".

For wrapture that is the ordinary case. Here the real `charge()` runs
and only the id in its result is rewritten, which is useful when a real
id would differ between runs but everything else about the result
matters.

```{file-write}
:id: write-pinned-test
:path: test_orders.py
:mode: append
:open: true



def test_pinned_result_with_wrapture():
    charge = wrapture.binding(Gateway, "charge")
    charge.on_call.transforms_result(lambda r: {**r, "id": "ch_TEST"})

    with charge:
        assert OrderService().place(500) == {"id": "ch_TEST", "amount": 500}
```

```{execute}
:id: run-pinned
:session: shell
:wait: prompt
pytest -q test_orders.py -k pinned_result
```

The amount came from the real method and the id was rewritten on the
way out. `transforms_args()` does the same on the way in, and
`validates_args()` and `validates_result()` check without changing.
These are stages, and they compose, so one binding can rewrite an
argument and check the result while the real code does the work in
between.

```{verify}
:id: pinned-result
:label: The real method ran and its result was changed
:substrate: shell
:trigger: after:run-pinned
out=$(.venv/bin/python -m pytest -q --color=no test_orders.py -k pinned_result 2>&1) && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; exit 1
```
