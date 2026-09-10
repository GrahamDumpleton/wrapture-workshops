"""Read the console exporters' output back.

The console exporters print each span, and each metrics export, as one
pretty-printed JSON document after another, so spans.log is a sequence
of documents rather than one. Run as a script, it prints one line per span,
indented by parent; run as `spans.py metrics`, it prints the attribute
sets on the two duration histograms from the last metrics export.
"""

import json
import sys

PATH = "spans.log"


def documents(path=PATH):
    """Yield every JSON document in the file, in order, skipping any
    other text the server printed around them."""
    decoder = json.JSONDecoder()
    text = open(path).read()
    pos = 0
    while True:
        start = text.find("\n{", pos)
        if start < 0:
            return
        try:
            document, pos = decoder.raw_decode(text, start + 1)
        except json.JSONDecodeError:
            pos = start + 2
            continue
        yield document


def spans(path=PATH):
    """The exported spans, in the order they were exported."""
    return [d for d in documents(path) if "kind" in d]


def histogram_points(name, path=PATH):
    """The data points of a histogram from the last metrics export."""
    points = []
    for document in documents(path):
        if "resource_metrics" not in document:
            continue
        points = []
        for resource in document["resource_metrics"]:
            for scope in resource["scope_metrics"]:
                for metric in scope["metrics"]:
                    if metric["name"] == name:
                        points.extend(metric["data"]["data_points"])
    return points


def describe(span):
    kind = span["kind"].removeprefix("SpanKind.")
    status = span["status"]["status_code"]
    exceptions = [e["attributes"]["exception.type"] for e in span["events"] if e["name"] == "exception"]
    line = f"{kind} {span['name']!r}"
    if status == "ERROR":
        line += " ERROR"
    if exceptions:
        line += " " + ", ".join(exceptions)
    return line


def main(what="spans", path=PATH):
    if what == "metrics":
        for name in ("http.server.request.duration", "wrapture.call.duration"):
            points = histogram_points(name, path)
            print(f"{name}: {len(points)} data points")
            for point in points:
                print(f"  {point['count']:>3} {json.dumps(point['attributes'])}")
        return
    exported = spans(path)
    by_id = {s["context"]["span_id"]: s for s in exported}
    for span in exported:
        depth = 0
        parent = span["parent_id"]
        while parent in by_id:
            depth += 1
            parent = by_id[parent]["parent_id"]
        print("  " * depth + describe(span))


if __name__ == "__main__":
    main(*sys.argv[1:])
