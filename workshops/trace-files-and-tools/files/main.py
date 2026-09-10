"""Process several sources on a small thread pool.

Each source goes through the pipeline on one of two worker threads.
An optional argument repeats the four sources that many times, for a
run long enough to watch a trace file rotate.
"""

from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor

from pipeline import process

SOURCES = ["alpha", "beta", "gamma", "delta"]


def main(rounds: int = 1) -> None:
    with ThreadPoolExecutor(max_workers=2) as pool:
        counts = list(pool.map(process, SOURCES * rounds))

    print(f"processed {sum(counts)} items from {len(counts)} sources")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
