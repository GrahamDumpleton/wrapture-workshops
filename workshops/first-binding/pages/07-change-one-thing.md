---
title: Change one thing
requires: [verify:result-transformed, quiz:real-code-ran]
---

# Change one thing

Stubbing and failing replace the call. A binding can also let the real
method run and change one thing about it, which is what substitution
tools cannot express. Here the real `charge()` runs and only the id in
its result is rewritten, useful when a real id would differ between
runs but everything else about the result matters.

```{cell-insert}
:id: insert-transform
:path: {{ notebook }}
:tags: [transform]
:run: true
pinned = wrapture.binding(Gateway, "charge")
pinned.on_call.transforms_result(lambda result: {**result, "id": "ch_TEST"})

with pinned:
    result = gateway.charge(500)

result
```

The amount came from the real method, and the id was rewritten on the
way out. Ask this binding what it does, as you did the first one.

```{cell-insert}
:id: insert-explain-transform
:path: {{ notebook }}
:tags: [explain-transform]
:run: true
print(pinned.explain())
```

The stage is named for what it touches, and the function by its name,
which for a lambda is `<lambda>`. `transforms_args()` does the same on
the way in, and `validates_args()` and `validates_result()` check
without changing.

```{verify}
:id: result-transformed
:label: The real method ran and its result was changed
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-explain-transform; cell-executed explain-transform
result == {"id": "ch_TEST", "amount": 500} and gateway.charge(500)["id"] == "ch_500" and "transforms result" in pinned.explain()
```

```{quiz}
:id: real-code-ran
:title: What ran
question: In the cell above, where did the amount of 500 in the result come from?
options:
  - { text: "The real charge() method, which the binding let run", correct: true }
  - { text: "The binding, which fabricated the whole result", explanation: "That is what returns() does. transforms_result() runs the real method and passes its result through the function." }
  - { text: "The lambda, which built a new dictionary from scratch", explanation: "The lambda copies the real result and changes only the id." }
explanation: transforms_result() runs the real method and hands its return value to the function, which here copies it and replaces the id.
```
