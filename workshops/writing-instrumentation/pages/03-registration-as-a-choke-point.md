---
title: Registration as a choke point
requires: [verify:dispatches-recorded]
---

# Registration as a choke point

The dispatcher is the harder half, and it is the shape every
framework has. Handlers are ordinary functions the application
registers, so there is no attribute to bind by name: they are
whatever `register()` was given, stored in a dictionary. Flask's
views, Celery's tasks and Django's signal receivers are the same
problem, and the answer is the same: intercept the registration
itself, and substitute `wrapture.observed(handler)` into it, so the
proxy is what gets stored and records a call whenever the library
later runs it. The binding on `register` is made with `when=False`,
behaviour-only, since the plumbing is not the trace.

The other choke point is the error handler. A handler that raises
never shows its exception on the `dispatch` event, because the
dispatcher catches it and returns `None`; the one place the failure
can be seen is `on_error()`, where the exception arrives as an
argument. A behaviour on it notes the exception against the
dispatcher's own event, aimed with `current_event(binding=...)` at
the nearest in-flight event of that binding. When nothing is
recording the handle is empty and the note quietly does nothing, so
the call needs no guard.

Replace the file with the version that has both hooks. One class can
serve several triggers, one method each, and the class's trigger
set is derived from its decorated methods.

```{file-write}
:id: write-support-both
:path: wrapture_local/hookline_support.py
:open: true
import wrapture


class HooklineInstrumentation(wrapture.Instrumentation):
    """Delivery and dispatch tracing for hookline."""

    target = "hookline"
    removable = True
    settings = {
        "headers": wrapture.Setting(False, "record the headers sent with each delivery"),
        "internals": wrapture.Setting(False, "record the connect and write steps beneath each delivery"),
    }

    @wrapture.instrumentation_hook("hookline.client")
    def client(self, name, module):
        policy = None if self.settings["headers"] else wrapture.redact("headers")

        deliver = wrapture.binding(
            module.Client,
            "deliver",
            leaf=not self.settings["internals"],
            category="external",
            capture_args=policy,
        )
        connect = wrapture.binding(module.Client, "_connect", label="hookline:connect")
        write = wrapture.binding(module.Client, "_write", label="hookline:write", capture_args=policy)

        group = wrapture.bindings(deliver=deliver, connect=connect, write=write)
        group.apply()

        self.on_cleanup(group.remove)

    @wrapture.instrumentation_hook("hookline.dispatch")
    def dispatch(self, name, module):
        def observe_handler(args, kwargs):
            if len(args) >= 2:
                kind, handler = args[:2]
                args = (kind, wrapture.observed(handler, label=f"handler:{kind}"), *args[2:])
            return args, kwargs

        register = wrapture.binding(module.Dispatcher, "register", when=False)
        register.on_call.transforms_args(observe_handler)

        dispatch = wrapture.binding(module.Dispatcher, "dispatch")

        def note_failure(wrapped, instance, args, kwargs):
            wrapture.current_event(binding=dispatch).note_exception(args[2])
            return wrapped(*args, **kwargs)

        on_error = wrapture.binding(module.Dispatcher, "on_error", when=False)
        on_error.on_call.decorates(note_failure)

        group = wrapture.bindings(register=register, dispatch=dispatch, on_error=on_error)
        group.apply()

        self.on_cleanup(group.remove)
```

```{execute}
:id: run-both
:session: shell
:wait: prompt
python -m wrapture app.py
```

```
hookline.client:Client.deliver(url='https://acme.example/hooks', payload={'order': 42}, headers='<redacted>')
hookline.client:Client.deliver -> {'url': 'https://acme.example/hooks', 'status': 202, 'bytes': 13} [3.2ms]
hookline.client:Client.deliver(url='https://globex.example/down', payload={'order': 42}, headers='<redacted>')
hookline.client:Client.deliver !! DeliveryError [4.0ms]
hookline.dispatch:Dispatcher.dispatch(kind='order.placed', event={'customer': 'ann@example.com'})
  handler:order.placed(event={'customer': 'ann@example.com'})
  handler:order.placed -> 'emailed ann@example.com' [5us]
hookline.dispatch:Dispatcher.dispatch -> 'emailed ann@example.com' [106us]
hookline.dispatch:Dispatcher.dispatch(kind='order.failed', event={'reason': 'card declined'})
  handler:order.failed(event={'reason': 'card declined'})
  handler:order.failed !! ValueError [4us]
hookline.dispatch:Dispatcher.dispatch -> None !! ValueError [174us]
delivery failed: https://globex.example/down: connection refused
emailed ann@example.com
None
failures: [('order.failed', ValueError('no handler for card declined'))]
```

Each dispatch is a tree with its handler beneath it, labelled by the
kind of event rather than by the function's own name, since that is
the name the library knows it by. The failing dispatch says both
things at once on its closing line: it returned `None`, and the
`ValueError` was why. `observed()` is idempotent, so a handler
registered twice is not wrapped twice, and the registration returns
the caller's original function rather than the proxy, which is what
lets application code keep its own name bound to its own function.

```{verify}
:id: dispatches-recorded
:label: Each dispatch records with its handler beneath it and the absorbed failure noted
:substrate: shell
:trigger: after:run-both
out=$(.venv/bin/python -m wrapture app.py 2>&1) && printf '%s\n' "$out" | grep -q "^  handler:order.placed(event=" && printf '%s\n' "$out" | grep -q '^  handler:order.failed !! ValueError' && printf '%s\n' "$out" | grep -q '^hookline.dispatch:Dispatcher.dispatch -> None !! ValueError' && { echo "Two dispatches, each with its handler beneath it, and the absorbed ValueError noted on the dispatch"; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If the check fails
The check runs `app.py` under the runner and expects handler lines
indented beneath each dispatch and `!! ValueError` on the failing
dispatch's closing line. No handler lines means the `register`
binding is not substituting `observed()`; a dispatch line without
the note means the `on_error` behaviour is missing or aimed at the
wrong binding.
```
