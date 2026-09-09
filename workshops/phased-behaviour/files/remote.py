"""A client that fetches URLs, and the loops that call it.

fetch_with_retry() retries a fetch on a timeout. wait_for() polls a job
until it reports done. reconnect() asks a monitor for the service's
health and then tries the client, round after round.
"""


class Client:
    def fetch(self, url):
        if "bad" in url:
            raise ConnectionError(f"cannot reach {url}")
        return {"url": url, "status": 200}


def fetch_with_retry(client, url, attempts=3):
    for attempt in range(1, attempts + 1):
        try:
            return client.fetch(url)
        except TimeoutError:
            if attempt == attempts:
                raise


class Job:
    def status(self):
        return "done"


def wait_for(job, polls=5):
    for _ in range(polls):
        if job.status() == "done":
            return True
    return False


class Monitor:
    def check(self):
        return "healthy"


def reconnect(monitor, client, url, rounds=5):
    for _ in range(rounds):
        monitor.check()
        try:
            return client.fetch(url)
        except ConnectionError:
            pass
    return None
