---
title: A picture of the run
requires: [verify:diagram]
---

# A picture of the run

The file is also what the exporters read afterwards. Three render a
trace for existing tools rather than a viewer of wrapture's own:
`chrome` for a timeline in Perfetto, `canonical` for a text
fingerprint to snapshot, and `mermaid` for a sequence diagram.
`python -m wrapture.tools convert` runs them from a shell.

```{execute}
:id: convert-mermaid
:session: shell
:wait: prompt
python -m wrapture.tools convert --format mermaid trace.jsonl
```

Participants are the classes, messages are the members called on them
in recorded order, a normal completion returns `return`, and a failure
returns the exception type. Mermaid renders natively on GitHub and in
most documentation tooling, JupyterLab's Markdown preview included, so
write the diagram inside a fence to a Markdown file and look at it
rendered.

````{execute}
:id: write-diagram
:session: shell
:title: Write the diagram to trace.md
:wait: prompt
{ printf '%s\n' '```mermaid'; python -m wrapture.tools convert --format mermaid trace.jsonl; printf '%s\n' '```'; } > trace.md
````

```{layout}
:id: show-diagram
:name: diagram
```

The preview replaces `main.py` at the top of the window. The three
orders read left to right down the page: `place` calls `charge` and
`record` and returns; the second `charge` comes back `CardDeclined`
and so does its `place`; the third runs like the first. This is the
first picture of what the program did, from a file, with the program
itself never having heard of wrapture.

```{verify}
:id: diagram
:label: trace.md holds a Mermaid sequence diagram with the declined card
:substrate: contents
:trigger: after:write-diagram
exists trace.md
contains trace.md sequenceDiagram
contains trace.md CardDeclined
```

```{hint}
:title: If the check fails
`trace.md` must start with a `mermaid` fence and hold the converter's
output: a `sequenceDiagram` line, the participants, and a
`CardDeclined` reply for the second order. An empty file means the
converter found no `trace.jsonl`; go back a page and run the program
under the runner again.
```
