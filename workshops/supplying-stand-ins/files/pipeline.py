"""A job pipeline that publishes work to a message broker.

The pipeline takes the broker transport through its constructor and
accepts an on_complete hook that it promises to call after each job,
as on_complete(job, outcome). The transport's methods all do network
I/O in production, so here they refuse to run at all: the seam is the
constructor, and a test must supply both the collaborator and the
hook.
"""


class Channel:
    def publish(self, body, routing_key="jobs"):
        raise RuntimeError("no broker in tests")

    def close(self):
        raise RuntimeError("no broker in tests")


class Transport:
    def open_channel(self):
        raise RuntimeError("no broker in tests")

    def close(self):
        raise RuntimeError("no broker in tests")


def on_complete(job, outcome):
    """The hook contract: called once per job with the job's id and
    its outcome. A test that wants the contract checked hands this
    function to stub(mimics=...)."""


class Pipeline:
    def __init__(self, transport, on_complete=None):
        self.transport = transport
        self.on_complete = on_complete

    def run(self, jobs):
        channel = self.transport.open_channel()
        sent = 0

        try:
            for job in jobs:
                channel.publish(job)
                sent += 1

                if self.on_complete is not None:
                    self.on_complete(job, "sent")
        finally:
            channel.close()

        return sent
