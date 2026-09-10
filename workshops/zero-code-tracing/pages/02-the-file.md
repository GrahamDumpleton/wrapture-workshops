---
title: The file
requires: [verify:runner-trace]
---

# The file

A `wrapture.toml` says what to observe and where the events go. For
the shop, with the card number redacted as before, that is one
`[[observe]]` entry per method and one sink.

```{file-write}
:id: write-config
:path: wrapture.toml
:open: true
[[observe]]
target = "shop:OrderService"
name = "place"
redact = ["card"]

[[observe]]
target = "shop:Gateway"
name = "charge"
redact = ["card"]

[[observe]]
target = "shop:Ledger"
name = "record"

[[sink]]
type = "printer"
```

The `target` is always an exact module or `module:path`, never a
pattern, and the members within it come from `name` for exact members
or `match` for a glob over the target's own immediate members. That is
deliberate: a pattern's blast radius is one level of one named
container, stated on the line above it, so `match = "*"` on
`shop:OrderService` can never accidentally wrap something in another
module. `redact` on an entry is `capture=wrapture.redact("card")`
spelt in TOML, and `[[sink]]` with `type = "printer"` is the
`Printer` from the previous workshop.

The `python -m wrapture` runner applies the config and then runs the
program as `__main__`, the same `-m` convention as pdb, cProfile and
coverage.

```{execute}
:id: run-runner
:session: shell
:wait: prompt
python -m wrapture main.py
```

```
shop:OrderService.place(amount=500, card='<redacted>', tenant='acme')
  shop:Gateway.charge(amount=500, card='<redacted>')
  shop:Gateway.charge -> {'id': 'ch_500', 'amount': 500} [8us]
  shop:Ledger.record(entry={'id': 'ch_500', 'amount': 500})
  shop:Ledger.record -> 'led_ch_500' [7us]
shop:OrderService.place -> {'id': 'ch_500', 'amount': 500} [285us]
shop:OrderService.place(amount=250, card='<redacted>', tenant='globex')
  shop:Gateway.charge(amount=250, card='<redacted>')
  shop:Gateway.charge !! CardDeclined [6us]
shop:OrderService.place !! CardDeclined [90us]
shop:OrderService.place(amount=120, card='<redacted>', tenant='globex')
  shop:Gateway.charge(amount=120, card='<redacted>')
  shop:Gateway.charge -> {'id': 'ch_120', 'amount': 120} [4us]
  shop:Ledger.record(entry={'id': 'ch_120', 'amount': 120})
  shop:Ledger.record -> 'led_ch_120' [4us]
shop:OrderService.place -> {'id': 'ch_120', 'amount': 120} [115us]
```

That is the same trace as before, from a program whose source has not
changed. The ordering is what makes it work. The config is applied
before the target runs, but applying it imports nothing: each observe
entry registers a post-import hook for its target module, and the
bindings land at the moment the application itself imports `shop`, in
the application's own import order. A `from shop import OrderService`
somewhere in the program still picks up the observed class, because
the observation is already in place when that line runs.

```{verify}
:id: runner-trace
:label: The runner traces the unchanged program
:substrate: shell
:trigger: after:run-runner
out=$(.venv/bin/python -m wrapture main.py 2>&1) && [ "$(printf '%s\n' "$out" | wc -l | tr -d ' ')" -eq 16 ] && [ "$(printf '%s\n' "$out" | grep -c "card='<redacted>'")" -eq 6 ] && printf '%s\n' "$out" | grep -q '^  shop:Gateway.charge !! CardDeclined' && { echo "Sixteen lines, the card redacted on every opening line, and the declined charge marked"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check runs `python -m wrapture main.py` itself and expects the
sixteen-line trace above, with `card='<redacted>'` on six opening
lines. A message about no config found means `wrapture.toml` is not
in this directory; a shorter trace means an `[[observe]]` entry is
missing or misnames its target. The message above is what the check
saw.
```
