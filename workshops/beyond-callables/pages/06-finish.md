---
title: Finish
requires: [quiz:dict-spelling]
---

# Finish

Five shapes, one lifecycle. Which one a binding has follows from how
it is named:

- Positional, at an attribute: an attribute binding, with `on_get`,
  `on_set` and `on_delete`, each read and write on the tape, and
  `decorates()` on a write for a guard that needs the instance.

- `attr=` or `item=`: a value binding, holding a value with
  `overrides()` or holding nothing with `hides()`, recording nothing.

- `mode="mapping"`: the one dict mutated in place for every holder,
  `updates()` merging and `overrides()` replacing its content.

- `item=` with `mode="callable"`: a callable in a registry wrapped in
  place, with the whole call vocabulary.

- A generator function, positionally: one event per iteration, with
  `items` and a `MISSING` result when the consumer stopped early.

```{quiz}
:id: dict-spelling
:title: Which spelling
question: "Another module did `from config import SETTINGS` at import time. Which binding changes the tax rate it sees during a test?"
options:
  - { text: "binding(config, \"SETTINGS\", mode=\"mapping\").updates({\"tax_rate\": 0.0})", correct: true }
  - { text: "binding(\"config\", attr=\"SETTINGS\").overrides({\"tax_rate\": 0.0})", explanation: "That gives config.SETTINGS a new dict; the other module still holds the old one." }
  - { text: "binding(config, \"SETTINGS\").on_get.returns({\"tax_rate\": 0.0})", explanation: "That intercepts reads through the module object; a holder that already has the dict never reads through it." }
explanation: A mapping binding mutates the one dict in place, so every holder of it sees the change, and the original entries come back on exit. The item= form on the dict itself, binding(config.SETTINGS, item="tax_rate"), reaches holders too, for a single entry.
```

The Finish button below says where to go next.
