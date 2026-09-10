---
title: The collaborator, strictly
requires: [verify:nothing-fabricated]
---

# The collaborator, strictly

The transport double deserves a closer look, because it is where the
difference from a fabricated object shows. A mock requires a spec and
fabricates nothing beyond it: a misspelled method is an
`AttributeError` wherever it happens, in the test or inside the
pipeline, and calls are checked against the real method's signature.

```{cell-insert}
:id: insert-misspelled
:path: {{ notebook }}
:tags: [misspelled]
:run: true
try:
    transport.open_chanel
except AttributeError as exc:
    misspelled = str(exc)

try:
    channel.publish("job-1", "jobs", "extra")
except TypeError as exc:
    too_many = str(exc)

print(misspelled)
print(too_many)
```

And there are no fabricated chains. Every method returns `None` until
`returns()` or `raises()` configures it, so had `open_channel` not
been configured, the pipeline's `channel.publish(...)` would have
failed loudly on the next line instead of an invented channel
absorbing the call. The object graph a test depends on is declared,
one double per node, which is why the `Channel` double was built and
wired first. The declared graph is also reachable back from the
configuration, so a fixture need not thread every double through to
the test.

```{cell-insert}
:id: insert-unconfigured
:path: {{ notebook }}
:tags: [unconfigured]
:run: true
unconfigured = wrapture.mock(Transport).open_channel()

unconfigured, transport.open_channel.returns_value is channel, isinstance(transport, Transport)
```

The double passes `isinstance` for the class it stands in for, since
that is exactly what it is standing in for. Data attributes hold no
invented values either: the test assigns what the code reads, and
reading an unassigned one is a loud error.

```{verify}
:id: nothing-fabricated
:label: The double rejects the misspelled method and the drifted call, and invents no channel
:substrate: learner-kernel
:path: {{ notebook }}
:trigger: after:insert-unconfigured; cell-executed unconfigured
"fabricates nothing" in misspelled and "too many positional" in too_many and unconfigured is None and transport.open_channel.returns_value is channel
```
