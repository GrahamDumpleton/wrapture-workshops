---
title: Finish
---

# Finish

A library that knew nothing of wrapture now records itself, from one
class next to a config file:

- The class declared its target, its removability and its settings,
  and a hook per trigger module built bindings against the module
  handed in and registered the undo with `on_cleanup()`.

- Registration was the choke point for handlers, with `observed()`
  substituted as they registered, and the error handler was where an
  absorbed failure got noted against the dispatch.

- A misspelt setting and a value of the wrong type were refused when
  the config loaded, with messages naming what was declared.

- The class was tested directly with `apply()` and `remove()`, and
  through `wrapture.instrumentation()` with `find_binding()`.

- The listing tool read it from the config, and an entry point is all
  that stands between the directory and a package.

The Finish button below says where to go next.
