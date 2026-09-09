---
title: Values
requires: [verify:values-restored]
---

# Values

Some patches wrap nothing. The test wants an environment variable set,
or a module constant lowered, for its duration and then put back, and
has no interest in watching anything. That is a value binding: name
the owner positionally, name the slot with `item=` for a mapping entry
or `attr=` for an attribute, and say what the slot should hold. It has
no `on_*` namespaces and records nothing, because there is no
operation to record, only a value in a slot.

`price()` refuses to run without `API_KEY` in the environment.
`overrides()` puts it there while applied; on exit the variable is
absent again, or back to what it held.

```{cell-insert}
:id: insert-env
:path: {{ notebook }}
:tags: [env]
:run: true
api_key = wrapture.binding(os.environ, item="API_KEY")
print(api_key)

try:
    price(100)
except RuntimeError as exc:
    print("without a key:", exc)

with api_key.overrides("sk_test"):
    priced = price(100)

print(priced)
"API_KEY" in os.environ
```

The other direction is `hides()`: the slot is absent while applied,
which `overrides(None)` cannot say, since None is a value that is
there. It is how the missing-configuration branch gets tested on a
machine where the variable is set. The verbs take effect at once on an
applied binding, so one binding can walk a slot through several states
within a test.

```{cell-insert}
:id: insert-hidden
:path: {{ notebook }}
:tags: [hidden]
:run: true
with api_key.overrides("sk_live") as key:
    print("set:", price(100))
    key.hides()
    try:
        price(100)
    except RuntimeError as exc:
        hidden = str(exc)

print("hidden:", hidden)
"API_KEY" in os.environ
```

A module constant is the same with `attr=`. A module can be named by
its import path, so the test needs no import of its own.

```{cell-insert}
:id: insert-timeout
:path: {{ notebook }}
:tags: [timeout]
:run: true
with wrapture.binding("config", attr="TIMEOUT").overrides(0.5), api_key.overrides("sk_test"):
    quick = price(100)

print(quick)
config.TIMEOUT
```

The value binding holds a value and observes nothing. When the question
becomes who reads the constant, name the attribute positionally instead
and it is the attribute binding from the last page, on a module this
time: every read is an event, and `on_get.returns()` shapes what the
reads see.

```{cell-insert}
:id: insert-reads
:path: {{ notebook }}
:tags: [reads]
:run: true
timeout = wrapture.binding("config", "TIMEOUT")
timeout.on_get.returns(0.5)

with timeout, wrapture.timeline() as tape, api_key.overrides("sk_test"):
    price(100)
    price(100)
    reads = [event.kind for event in tape.for_binding(timeout)]

print(tape.tree())
reads
```

Two calls, two reads: `price()` reads the timeout every time rather
than caching it, and the tape proves it, with each read marked as
injected.

```{verify}
:id: values-restored
:label: The key and the timeout held while applied and were put back after
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-reads; cell-executed reads
priced == "[USD within 30.0s] total=120.00" and "API_KEY" not in os.environ and hidden == "API_KEY is not configured" and quick.startswith("[USD within 0.5s]") and config.TIMEOUT == 30.0 and reads == ["get", "get"]
```

```{hint}
:title: Other slots
`item=` names any mapping entry, so `binding(sys.modules,
item="boto3").overrides(fake)` is a stand-in module for imports made
while applied, and `attr=` on an instance,
`binding(client, attr="base_url").overrides(...)`, changes one object
only, which the positional form refuses since it would affect every
instance. What a value binding restores is the slot, not objects
reachable through it: mutate the original dict a slot held and the
restore puts the same mutated dict back.
```
