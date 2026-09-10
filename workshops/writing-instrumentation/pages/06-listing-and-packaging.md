---
title: Listing and packaging
requires: [verify:listed, quiz:import-posture]
---

# Listing and packaging

What is installed, and what a file could switch on, is a command
away. The listing tool reads class data the way wrapture will,
applying nothing: the target and its installed version with the
support verdict, the trigger modules, the settings with their
defaults and descriptions, and removability. With `--config` it adds
the file's own reference-form classes and marks the entries the file
selects, and `--verbose` says what applying each one here would
register.

```{execute}
:id: run-listing
:session: shell
:wait: prompt
python -m wrapture.tools instrumentation --config wrapture.toml --verbose
```

```
hookline  (local: wrapture_local.hookline_support:HooklineInstrumentation)
  Delivery and dispatch tracing for hookline.
  target: hookline, not installed
  modules: hookline.client, hookline.dispatch
  removable: yes
  settings:
    headers = false     record the headers sent with each delivery
    internals = false   record the connect and write steps beneath each delivery
  config: enabled in wrapture.toml
  would register: hookline.client
  would register: hookline.dispatch
```

The name, the description and the version came from the class: the
target, the docstring's first line and nothing, since there is no
distribution behind a local class. `not installed` says the library
has no package metadata, which is true of a directory beside the
config, and the description beside each setting is what a person
editing the file will read, so it was written for them.

```{verify}
:id: listed
:label: The listing tool reads the class from the config and would register both triggers
:substrate: shell
:trigger: after:run-listing
out=$(.venv/bin/python -m wrapture.tools instrumentation --config wrapture.toml --verbose 2>&1) && printf '%s\n' "$out" | grep -q '^hookline  (local: wrapture_local.hookline_support:HooklineInstrumentation)' && printf '%s\n' "$out" | grep -q 'would register: hookline.client' && printf '%s\n' "$out" | grep -q 'would register: hookline.dispatch' && printf '%s\n' "$out" | grep -q 'internals = false' && { echo "hookline listed from wrapture.toml, with both triggers and both settings"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check expects the listing to show `hookline` as a local class
from `wrapture.toml` with two `would register` lines. An error in
place of the entry means the class cannot load, and a warning line
means its module imported the target at the top; a missing entry
means `--config` did not name the file with the `[[instrument]]`
entry, or the entry has `enabled = false`.
```

## How it would be packaged

Nothing about the class changes when it leaves the config's
directory. A package registers each class in the
`wrapture.instrumentation` entry point group, one entry per class,
the entry point name being the bare target, and the config then
names it with that one word:

```toml
[project]
name = "wrapture-instrumentation-hookline"
version = "1.0.0"
description = "Delivery and dispatch tracing for hookline"
dependencies = ["wrapture"]

[project.entry-points."wrapture.instrumentation"]
hookline = "wrapture_instrumentation_hookline:HooklineInstrumentation"
```

Note what is not in the dependencies: hookline. An instrumentation
package depends on wrapture and never on its target, because
installing the instrumentation must not install the thing it
instruments, and the version gate is `supports`, a PEP 440 range
checked at apply time against whatever the environment has, a
warning rather than an error when it fails. Installing the package
registers the class and applies nothing; `[[instrument]]` with
`name = "hookline"` switches it on, and `hookline@distribution`
picks between two packages that register the same name. The one
rule that follows a class everywhere is the import posture the
second page relied on.

```{quiz}
:id: import-posture
:title: The import posture
:shuffle: true
question: "Why must the module that defines an Instrumentation class never import the library it patches at the top?"
options:
  - { text: "wrapture imports the class when the config loads, before the application imports anything, so a top-level import would drag the library in ahead of the hook meant to fire on its import", correct: true }
  - { text: "Because the library is not installed in the environment where the config is read", explanation: "It usually is installed; the problem is when it would be imported, not whether it can be." }
  - { text: "Because two imports of the same module would give the hook two module objects to patch", explanation: "Python imports a module once. The issue is timing: the patches would land after the import they were meant to precede." }
  - { text: "It may import the library, as long as the class sets removable = True", explanation: "Removability is about undoing patches. wrapture watches sys.modules while loading the class and warns if the target or a trigger appeared." }
explanation: The hook receives the module as a parameter, which for most instrumentation is everything it touches. Anything more is imported inside the hook, or lazily, so loading the class never imports the package it is about to patch.
```
