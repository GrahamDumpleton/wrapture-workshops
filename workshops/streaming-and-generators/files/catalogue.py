"""A paginated catalogue and three consumers with different reading
patterns.

pages() is a generator: nothing is fetched until the consumer asks,
and fetched counts the pages the catalogue actually served.
collect_ids() reads to the end. first_match() returns as soon as it
finds an item, dropping the generator without closing it.
Exporter.write() swallows an OSError mid-stream and reports how many
rows it managed to write.
"""


class Catalogue:
    def __init__(self, records, page_size=2):
        self.records = records
        self.page_size = page_size
        self.fetched = 0

    def pages(self, *, cursor=0):
        while cursor < len(self.records):
            batch = self.records[cursor : cursor + self.page_size]
            self.fetched += 1

            yield {"cursor": cursor, "items": batch}

            cursor += self.page_size


def collect_ids(pages):
    ids = []

    for page in pages:
        ids.extend(item["id"] for item in page["items"])

    return ids


def first_match(pages, predicate):
    for page in pages:
        for item in page["items"]:
            if predicate(item):
                return item

    return None


class Exporter:
    def write(self, pages, out):
        written = 0

        try:
            for page in pages:
                for item in page["items"]:
                    out.append(f"{item['id']},{item['name']}")
                    written += 1
        except OSError:
            pass

        return written
