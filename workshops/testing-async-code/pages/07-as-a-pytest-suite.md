---
title: As a pytest suite
requires: [verify:nudge-caught, verify:suite-green]
---

# As a pytest suite

pytest-asyncio drives the coroutines; the bindings and assertions are
unchanged. wrapture's pytest plugin provides the `tape` fixture, a
recording scope spanning each test, so a test that asks for it reads
`send.events` without opening a timeline of its own. The third test
states the habit worth adopting in every async suite:
`pending().assert_never()` costs nothing when everything is awaited,
and it is the line that fails when someone deletes an `await`.

```{file-write}
:id: write-test
:path: test_push.py
:open: true
import pytest
import wrapture

from push import Notifier, PushClient

pytest_plugins = ["wrapture.pytest_plugin"]


@pytest.fixture
def send():
    binding = wrapture.binding(PushClient, "send")
    binding.on_call.returns("queued")

    with binding:
        yield binding


@pytest.mark.asyncio
async def test_every_user_is_sent_to_and_awaited(send, tape):
    delivered = await Notifier(PushClient()).broadcast(["ana", "ben"], "hello")

    assert delivered == 2
    send.events.finished().assert_times(2)
    send.events.pending().assert_never()


@pytest.mark.asyncio
async def test_a_timeout_stops_the_broadcast_early(send, tape):
    send.on_call.then(after=1).raises(TimeoutError("gateway busy"))

    delivered = await Notifier(PushClient()).broadcast(["ana", "ben", "cal"], "hello")

    assert delivered == 1
    send.events.raising(TimeoutError).assert_once()


@pytest.mark.asyncio
async def test_a_nudge_is_awaited(send, tape):
    await Notifier(PushClient()).nudge("ana")

    send.events.pending().assert_never()
```

The workshop environment has pytest and pytest-asyncio installed, so
run the suite from the notebook.

```{cell-insert}
:id: insert-pytest
:path: {{ notebook }}
:tags: [pytest]
:run: true
!python -m pytest -q --color=no test_push.py
```

Two pass and the nudge test fails, with the pending event printed
under the assertion and the tape's tree attached to the report. The
warnings summary at the end carries Python's own complaint, naming
`PushClient.send`.

```{verify}
:id: nudge-caught
:label: The suite fails only the nudge test, on the pending send
:substrate: shell
:trigger: after:insert-pytest; cell-executed pytest
out=$(python -m pytest -q --color=no test_push.py 2>&1); printf '%s\n' "$out" | grep -q 'test_a_nudge_is_awaited' && printf '%s\n' "$out" | grep -q '1 failed, 2 passed' && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; exit 1
```

Now fix the bug the test found. The edit adds the missing `await` in
`push.py`.

```{editor-replace}
:id: fix-nudge
:path: push.py
:match: self.client.send(user, "nudge")  # bug: missing await
await self.client.send(user, "nudge")
```

```{cell-insert}
:id: insert-pytest-fixed
:path: {{ notebook }}
:tags: [pytest-fixed]
:run: true
!python -m pytest -q --color=no test_push.py
```

```{verify}
:id: suite-green
:label: All three tests pass with the await in place
:substrate: shell
:trigger: after:insert-pytest-fixed; cell-executed pytest-fixed
out=$(python -m pytest -q --color=no test_push.py 2>&1) && printf '%s\n' "$out" | grep -q '3 passed' && { printf '%s\n' "$out" | tail -n 1; exit 0; }; printf '%s\n' "$out"; exit 1
```

```{hint}
:title: If a check fails
`test_push.py` must be in this directory next to `push.py`. The first
check expects exactly one failure, the nudge test; the second expects
all three to pass once `nudge()` reads `await self.client.send(user,
"nudge")`. Open `push.py` to confirm the edit landed.
```
