---
title: Naming events per operation
requires: [verify:resolved]
---

# Naming events per operation

A label, a category and seed data are declarations about the
binding's target, and for most targets one value each is the truth.
Some seams front several kinds of operation at once. `Notifier.send`
delivers by email, a message to a queue, or by sms, a call to an
external provider, depending on the channel it is called with, and
no single category or name is honest for all of its calls. For that,
`label=`, `category=` and `data=` each accept a callable in place of
the value, with the `when=` predicate's signature, consulted per
operation to decide that value for the one event: a resolver.

```{file-write}
:id: write-resolvers
:path: resolvers.py
:open: true
import sys

import wrapture

from shop import Notifier, OrderService
import orders

KINDS = {"email": "messaging", "sms": "external"}


def kind_of(instance, args, kwargs):
    return KINDS.get(args[0], "external")


def name_of(instance, args, kwargs):
    return f"notify/{args[0]}"


def tags_of(instance, args, kwargs):
    return {"channel": args[0]}


wrapture.binding(OrderService, "place").apply()
send = wrapture.binding(
    Notifier, "send",
    category=kind_of, label=name_of, data=tags_of,
).apply()

printer = wrapture.add_sink(wrapture.Printer(sys.stdout, timing=False))
orders.run()
wrapture.remove_sink(printer)

with wrapture.timeline():
    orders.run()
    for event in send.events:
        print(event.label, event.category, event.data, event.path)
```

```{execute}
:id: run-resolvers
:session: shell
:wait: prompt
python resolvers.py
```

```
shop:OrderService.place(amount=500, card='4111-1111-1111-1111', tenant='acme', channel='email')
  notify/email(channel='email', message='order ch_500 placed')
  notify/email -> 'email:order ch_500 placed'
shop:OrderService.place -> {'id': 'ch_500', 'amount': 500}
...
notify/email messaging {'channel': 'email'} shop:Notifier.send
notify/sms external {'channel': 'sms'} shop:Notifier.send
```

The three are consulted together, at the same moment `when=` is,
after it has accepted the operation and before its event is built, so
a declined operation consults none of them and nothing runs while
nothing listens. A resolved label names the event, not the binding,
which the last column shows: the path is still `shop:Notifier.send`,
and that is how `find_binding()` and error messages know it. Keep a
resolved name repeatable and low-cardinality, the way a request's
route is, and put identifiers in data.

```{verify}
:id: resolved
:label: Each send is named, categorised and tagged by its channel
:substrate: shell
:trigger: after:run-resolvers
out=$(.venv/bin/python resolvers.py 2>&1) && printf '%s\n' "$out" | grep -q "^  notify/email(channel='email'" && printf '%s\n' "$out" | grep -q "^  notify/sms(channel='sms'" && printf '%s\n' "$out" | grep -q "^notify/email messaging {'channel': 'email'} shop:Notifier.send$" && printf '%s\n' "$out" | grep -q "^notify/sms external {'channel': 'sms'} shop:Notifier.send$" && { echo "Sends named notify/email and notify/sms, categorised messaging and external, tagged by channel"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check expects the printer to show `notify/email(` and
`notify/sms(` lines, and the timeline loop to print the label,
category, data and path of each send. All three resolvers take
`(instance, args, kwargs)` and read the channel from `args[0]`.
```
