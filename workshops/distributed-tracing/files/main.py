"""Three uploads, each handing work to a pool and to a queue.

Each upload produces three trees: the request, the thumbnail work on
a pool thread with a link back to the request, and the notification
on the consumer thread with a link back to the same request carried
by the message's headers.
"""

import time

from uploads import handle_upload, start_notifier, stop_notifier


def main():
    notifier = start_notifier()

    try:
        for name in ("cat.png", "dog.png", "fish.png"):
            print(f"{name}: {handle_upload(name)}")
            time.sleep(0.05)
    finally:
        stop_notifier(notifier)


if __name__ == "__main__":
    main()
