---
title: Declared settings
requires: [verify:internals-on, verify:typo-refused, verify:type-refused]
---

# Declared settings

Any key on the `[[instrument]]` entry other than `name` is one of
the settings the class declares, and declaration is what makes the
file validated rather than passed through blind. The resolved
values, class defaults under the entry's, are `self.settings` inside
the hooks, which is where the first page's `internals` decided
whether the deliveries were leaves. Switch it on.

```{editor-replace}
:id: add-internals
:path: wrapture.toml
:match: name = "wrapture_local.hookline_support:HooklineInstrumentation"
name = "wrapture_local.hookline_support:HooklineInstrumentation"
internals = true
```

```{execute}
:id: run-internals
:session: shell
:wait: prompt
python -m wrapture app.py
```

```
hookline.client:Client.deliver(url='https://acme.example/hooks', payload={'order': 42}, headers='<redacted>')
  hookline:connect(url='https://acme.example/hooks')
  hookline:connect -> None [2.7ms]
  hookline:write(url='https://acme.example/hooks', payload={'order': 42}, headers='<redacted>')
  hookline:write -> None [1.2ms]
hookline.client:Client.deliver -> {'url': 'https://acme.example/hooks', 'status': 202, 'bytes': 13} [4.2ms]
...
```

The connect and write steps now record beneath each delivery, for
someone debugging the client itself. That is the setting's whole
purpose, and the reason to offer one: the default is the terminal
node most users want, and the switch is there for the rest.

```{verify}
:id: internals-on
:label: With internals on, the connect and write steps record beneath each delivery
:substrate: shell
:trigger: after:run-internals
out=$(.venv/bin/python -m wrapture app.py 2>&1) && [ "$(printf '%s\n' "$out" | grep -c '^  hookline:connect(url=')" = 2 ] && printf '%s\n' "$out" | grep -q "^  hookline:write(.*headers='<redacted>')" && { echo "Connect and write beneath each delivery, headers still redacted"; exit 0; }; printf '%s\n' "$out"; exit 1
```

An unknown key is a `ConfigError` when the config loads, not a key
that is silently ignored, so a typo fails where the file is read
rather than an hour into a run. Misspell the setting and run again.

```{editor-replace}
:id: break-name
:path: wrapture.toml
:match: internals = true
internal = true
```

```{execute}
:id: run-typo
:session: shell
:wait: prompt
python -m wrapture app.py
```

```
wrapture: instrument entry 'wrapture_local.hookline_support:HooklineInstrumentation': unknown settings ['internal']; the declared settings are ['headers', 'internals']
```

```{verify}
:id: typo-refused
:label: The misspelt setting is refused when the config loads
:substrate: shell
:trigger: after:run-typo
out=$(.venv/bin/python -m wrapture app.py 2>&1); printf '%s\n' "$out" | grep -q "unknown settings \['internal'\]; the declared settings are \['headers', 'internals'\]" && { echo "Refused at load: unknown setting internal"; exit 0; }; printf '%s\n' "$out"; exit 1
```

The check is shallow by design: a value whose outer type does not
match the default's is refused too, a string where the default is a
boolean, a scalar where it is a list, but nothing inside a list or
table, because element types cannot be inferred from an empty
default. A setting with a shape of its own is checked in
`configure()`, the optional one-time method that runs before any
trigger fires, where a `ConfigError` still surfaces at config time.
Put the name right and the value wrong.

```{editor-replace}
:id: break-type
:path: wrapture.toml
:match: internal = true
internals = "yes"
```

```{execute}
:id: run-type
:session: shell
:wait: prompt
python -m wrapture app.py
```

```
wrapture: instrument entry 'wrapture_local.hookline_support:HooklineInstrumentation': setting 'internals' expects a boolean (its default is False), got 'yes'
```

```{verify}
:id: type-refused
:label: A value of the wrong type is refused when the config loads
:substrate: shell
:trigger: after:run-type
out=$(.venv/bin/python -m wrapture app.py 2>&1); printf '%s\n' "$out" | grep -q "setting 'internals' expects a boolean (its default is False), got 'yes'" && { echo "Refused at load: internals must be a boolean"; exit 0; }; printf '%s\n' "$out"; exit 1
```

Put the file back to the default before moving on.

```{editor-replace}
:id: restore-config
:path: wrapture.toml
:match: internals = "yes"
internals = false
```

```{hint}
:title: If a check fails
The three checks run `app.py` under the runner and expect, in turn,
connect and write lines beneath each delivery, then the unknown
settings error naming `internal`, then the type error for `"yes"`.
Open `wrapture.toml` to see which state it is in; each check
expects exactly the edit above it.
```
