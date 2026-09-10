"""A notifier that fans messages out through a push gateway.

The client is async all the way down: one coroutine method per send,
and an async generator streaming delivery receipts back. Every method
refuses to run, because in production each one talks to the gateway.
The notifier sends sequentially and treats a timeout as a partial
result rather than a failure; its nudge has the bug unique to async
code, a coroutine created and never awaited.
"""

import asyncio


class PushClient:
    async def send(self, user: str, message: str) -> str:
        raise RuntimeError("no gateway in tests")

    async def receipts(self, batch: str):
        raise RuntimeError("no gateway in tests")
        yield


class Notifier:
    def __init__(self, client: PushClient) -> None:
        self.client = client

    async def broadcast(self, users: list[str], message: str) -> int:
        delivered = 0

        for user in users:
            try:
                await self.client.send(user, message)
            except TimeoutError:
                break
            delivered += 1

        return delivered

    async def nudge(self, user: str) -> None:
        self.client.send(user, "nudge")  # bug: missing await


class ConcurrentNotifier(Notifier):
    async def broadcast(self, users: list[str], message: str) -> int:
        results = await asyncio.gather(
            *(self.client.send(user, message) for user in users),
        )
        return len(results)


async def collect_receipts(client: PushClient, batch: str) -> list[str]:
    return [receipt async for receipt in client.receipts(batch)]
