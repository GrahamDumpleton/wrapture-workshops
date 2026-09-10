---
title: Finish
requires: [quiz:inert-when-silent]
---

# Finish

Four producers, one tape:

- Bindings record calls observed from outside, as before.

- `capture_logs()` records log messages as events nested inside the
  call that emitted them, with `at_level()` and `with_message()` to
  select them.

- `block()` records a named stretch of code as one event, in the test
  body or in the application, and `within()` scopes every query to
  its contents.

- `annotate()` merges into the innermost event in flight, and
  `note_exception()` records a failure the code handled, so
  `failed` and `raising()` find it while `result` still holds what
  the caller got.

```{quiz}
:id: inert-when-silent
:title: Leaving them in
:shuffle: true
question: "shop.py calls block(), annotate() and note_exception() unconditionally. What do those calls cost in production when nothing is listening?"
options:
  - { text: "Nothing is built at all: no event, no data, no tape; each call is a no-op until a sink or a timeline is listening", correct: true }
  - { text: "An event is built and then discarded, so the cost is one allocation per call", explanation: "The recording gate is checked first. With nothing listening, no event is constructed." }
  - { text: "They raise unless the code is running under a timeline, so production code must guard them", explanation: "Outside recording they are silent no-ops. A note aimed at an event that has already finished warns, but that needs recording to be on." }
  - { text: "They are compiled out by the wrapture launcher", explanation: "Nothing is compiled away. The calls stay, and they check whether anything is listening." }
explanation: Like a log statement, each marker is embedded by the author and inert when nothing listens. That is what lets them stay in application code and become spans later under a tracer.
```

The Finish button below says where to go next.
