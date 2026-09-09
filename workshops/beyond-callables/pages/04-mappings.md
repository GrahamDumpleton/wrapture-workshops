---
title: Mappings and registries
requires: [verify:settings-pinned]
---

# Mappings and registries

`SETTINGS` is shared by reference: `shop.py` did `from config import
SETTINGS` at import time, so giving `config.SETTINGS` a new dict would
strand `price()` with the old one. `mode="mapping"` binds the dict
itself and mutates it in place, never replacing it, so every holder
sees the test's content and the original entries come back on exit.
`updates()` merges the given keys over what is there; `overrides()`
makes them the whole content.

```{cell-insert}
:id: insert-settings
:path: {{ notebook }}
:tags: [settings]
:run: true
import shop

settings = wrapture.binding(config, "SETTINGS", mode="mapping")
print(settings)

with settings.updates({"tax_rate": 0.0}), api_key.overrides("sk_test"):
    untaxed = price(100)

with settings.overrides({"currency": "EUR", "tax_rate": 0.1}), api_key.overrides("sk_test"):
    euros = price(100)
    same_dict = shop.SETTINGS is config.SETTINGS

print(untaxed)
print(euros)
same_dict, config.SETTINGS
```

For readers coming from mock: `updates()` is `patch.dict(d, values)`
and `overrides()` is `patch.dict(d, values, clear=True)`. Compare the
value binding on the attribute, which replaces the object
`config.SETTINGS` names. `price()` reads through the holder it took at
import and never notices.

```{cell-insert}
:id: insert-replaced
:path: {{ notebook }}
:tags: [replaced]
:run: true
with wrapture.binding("config", attr="SETTINGS").overrides({"currency": "EUR", "tax_rate": 0.0}), api_key.overrides("sk_test"):
    replaced = price(100)

replaced
```

Three spellings, then, for a dict: `item=` for one entry changed or
absent, `attr=` for the attribute to name a different object, and
`mode="mapping"` for the one dict to hold these entries for every
holder.

The formatter registry is a fourth shape: a callable kept in a dict.
A value binding could swap the entry for a fake, but `item=` with
`mode="callable"` wraps the entry in place instead, with the whole
call vocabulary, recording and phases included, and puts the original
back on exit.

```{cell-insert}
:id: insert-registry
:path: {{ notebook }}
:tags: [registry]
:run: true
loud = wrapture.binding("config", "FORMATTERS", item="plain", mode="callable")
loud.on_call.transforms_result(str.upper)

with wrapture.timeline(loud) as tape, api_key.overrides("sk_test"):
    shouted = price(100)

print(shouted)
print(tape.tree())
config.FORMATTERS["plain"] is config.plain
```

The real formatter ran, its result was changed on the way out, the
call is on the tape under the registry's name, and the registry holds
the original function again.

```{verify}
:id: settings-pinned
:label: The settings changed for every holder and came back, and the registry entry was wrapped
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-registry; cell-executed registry
untaxed.endswith("total=100.00") and euros == "[EUR within 30.0s] total=110.00" and same_dict and config.SETTINGS == {"currency": "USD", "tax_rate": 0.2} and replaced == "[USD within 30.0s] total=120.00" and shouted.endswith("TOTAL=120.00") and config.FORMATTERS["plain"] is config.plain
```

```{hint}
:title: Every shape at once
Bindings group, and a group applies and removes together, in order,
so a fixture that pins all of a test's configuration is one
`wrapture.bindings(api_key=..., settings=..., timeout=...)` around a
`yield`. The pytest plugin's leak sweep then reports, by name, any of
them a test left applied, the failure hand-rolled cleanup gets wrong
silently.
```
