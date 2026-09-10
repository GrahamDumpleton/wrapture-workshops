---
title: A diagram and a diff
requires: [verify:rendered]
---

# A diagram and a diff

The exporters that the previous workshop ran from a shell are functions
too, and they take the records the file holds. Each root event minted a
trace id of its own, so one order's tree is the events sharing its id.
Take the first two orders and the first one that was declined, and
hand their events to `mermaid()`; JupyterLab renders a Mermaid fence
in Markdown output, so the diagram appears under the cell.

````{cell-insert}
:id: insert-mermaid
:path: {{ notebook }}
:tags: [mermaid]
:run: true
from IPython.display import Markdown

roots = [event for event in events if event["parent_id"] is None]

def tree(root):
    trace_id = root["trace"]["w3c"]["trace_id"]
    return [event for event in events if event["trace"]["w3c"]["trace_id"] == trace_id]

declined = next(root for root in roots if "exception" in root)
chosen = [event for root in roots[:2] + [declined] for event in tree(root)]

Markdown(f"```mermaid\n{wrapture.mermaid(chosen)}\n```")
````

Participants are the classes, messages are the members called on
them, and a failure comes back as the exception type: the third order
ends at the gateway with `CardDeclined`, and its `place` returns the
same.

`canonical()` renders a tree as a text fingerprint with everything
unstable left out: no timings, no values, no sequence numbers, only
what called what and what failed. Two fingerprints compare as a diff.
An order that went through against one that was declined:

```{cell-insert}
:id: insert-diff
:path: {{ notebook }}
:tags: [diff]
:run: true
import difflib

placed = next(root for root in roots if "exception" not in root)

diff = difflib.unified_diff(
    wrapture.canonical(tree(placed)).splitlines(),
    wrapture.canonical(tree(declined)).splitlines(),
    "placed", "declined", lineterm="",
)
print("\n".join(diff))
```

Two lines gained the `!! CardDeclined` marker and the ledger line is
gone. That is the whole difference between the two paths through the
code, readable by someone who has never seen it, and it is the same
comparison a snapshot test makes when a refactor changes what calls
what.

```{verify}
:id: rendered
:label: The diagram and the fingerprints come from the file
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-diff; cell-executed diff
wrapture.mermaid(chosen).startswith("sequenceDiagram") and len(chosen) < 12 and "CardDeclined" in wrapture.mermaid(chosen) and "!! CardDeclined" in wrapture.canonical(tree(declined)) and "!!" not in wrapture.canonical(tree(placed))
```

```{hint}
:title: If the check fails
`chosen` must hold the events of three roots only, one of them
declined, and `placed` and `declined` a root without and with an
`exception`. If the
diagram cell shows the Mermaid source rather than a picture, the cell
still ran; the check reads the functions, not the rendering.
```
