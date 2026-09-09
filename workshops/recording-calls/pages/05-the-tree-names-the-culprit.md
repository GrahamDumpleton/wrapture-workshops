---
title: The tree names the culprit
requires: [verify:culprit-named]
---

# The tree names the culprit

Counting says something leaked, and pairing says what. To say who, add
the repository methods to the timeline. The tape then nests each
acquire and release under the method that made it, and
`tape.children_of()` walks the tree, so a root whose children include a
`connect` but no `close` names itself.

```{cell-insert}
:id: insert-culprit
:path: {{ notebook }}
:tags: [culprit]
:run: true
find = wrapture.binding(Repository, "find")
count = wrapture.binding(Repository, "count")

with wrapture.timeline(find, count, connect, close) as tape:
    report(Repository(Database()), [1, 2])
    culprits = [
        caller for caller in tape.roots()
        if "pooled:Connection.close" not in [child.path for child in tape.children_of(caller)]
    ]

print(tape.tree())
for caller in culprits:
    print("leaked by", caller)
```

The tree shows the bug as it happened. `find()` with a key that matched
released its connection, `find()` with a key that did not match never
called `close()`, and `count()` released on the way out of its
`finally`.

When the method is long, or acquires in several places, you want the
line rather than the method. Stack capture on the acquire binding
records the calling frame with each event, priced per binding so only
the acquire pays for it.

```{cell-insert}
:id: insert-stack
:path: {{ notebook }}
:tags: [stack]
:run: true
connect_here = wrapture.binding(Database, "connect", stack="caller")

with wrapture.timeline(connect_here, close):
    report(Repository(Database()), [1, 2])
    released = {event.instance for event in close.events}
    for event in connect_here.events:
        if event.result not in released:
            frame = wrapture.stack_frames(event.stack)[0]
            print(f"{event.result} acquired at line {frame.lineno} in {frame.function}, never released")
```

That line is the `connect()` call at the top of `find()`. Open the
file there.

```{file-open}
:id: open-leak-line
:path: pooled.py
:line: 48
```

```{verify}
:id: culprit-named
:label: The tree named find() with key 2 as the leak
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-stack; cell-executed stack
len(culprits) == 1 and culprits[0].path == "pooled:Repository.find" and culprits[0].arguments["key"] == 2
```
