---
title: Keeping secrets out
requires: [verify:redacted]
---

# Keeping secrets out

The first thing to notice in that trace is something it should not
contain. The card numbers are in it, in full, because the bindings
captured the arguments as given. A trace that is going to be looked
at, streamed to a file or sent anywhere is exactly the place a card
number should not be.

The `redact()` capture policy replaces named parameters with a marker
before the event is recorded. It matches by parameter name against the
signature, so it works whether the caller passed the card positionally
or by keyword, and it goes on the binding, since the binding is what
captures. Two of the three methods take a card.

```{editor-replace}
:id: redact-place
:path: main.py
:match: wrapture.binding(OrderService, "place").apply()
wrapture.binding(OrderService, "place", capture=wrapture.redact("card")).apply()
```

```{editor-replace}
:id: redact-charge
:path: main.py
:match: wrapture.binding(Gateway, "charge").apply()
wrapture.binding(Gateway, "charge", capture=wrapture.redact("card")).apply()
```

```{execute}
:id: run-redacted
:session: shell
:wait: prompt
python main.py
```

The opening lines now read `card='<redacted>'` and everything else is
unchanged. Leave it on: the rest of the workshop narrows the trace,
and every version of it is one that might be kept.

```{verify}
:id: redacted
:label: No card number reaches the trace
:substrate: shell
:trigger: after:run-redacted
out=$(.venv/bin/python main.py 2>&1) && ! printf '%s\n' "$out" | grep -q '[0-9]\{4\}-[0-9]\{4\}' && [ "$(printf '%s\n' "$out" | grep -c "card='<redacted>'")" -eq 6 ] && { echo "Six opening lines say card='<redacted>' and no card number appears"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
Both `place` and `charge` take a card, so both bindings need
`capture=wrapture.redact("card")`. With only one changed, the other's
opening lines still show the number; the message above is the trace
the check saw.
```
