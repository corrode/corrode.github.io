#!/usr/bin/env python3
"""Check that rendered posts reference nonempty local social images."""

import argparse
from html.parser import HTMLParser
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit


class Metadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.properties = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta" and "property" in attrs:
            self.properties[attrs["property"]] = attrs.get("content", "")


def check(root):
    root = root.resolve()
    errors = []
    count = 0
    for page in sorted(root.rglob("*.html")):
        metadata = Metadata()
        metadata.feed(page.read_text(encoding="utf-8"))
        props = metadata.properties
        if props.get("og:type") != "article":
            continue
        count += 1
        label = page.relative_to(root)
        image = props.get("og:image", "").strip()
        if not image:
            errors.append(f"{label}: missing og:image")
            continue
        url = urlsplit(image)
        site = urlsplit(props.get("og:url", ""))
        if url.netloc and url.netloc != site.netloc:
            errors.append(f"{label}: social image must be local: {image}")
            continue
        path = unquote(url.path)
        target = ((root / path.lstrip("/")) if path.startswith("/")
                  else (page.parent / path)).resolve()
        if not target.is_relative_to(root):
            errors.append(f"{label}: image path escapes build directory: {image}")
        elif not target.is_file() or target.stat().st_size == 0:
            errors.append(f"{label}: missing or empty social image: {image}")
    if count == 0:
        errors.append(f"{root}: no rendered articles found; run zola build --drafts first")
    return count, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", nargs="?", type=Path, default=Path("public"))
    args = parser.parse_args()
    count, errors = check(args.directory)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print("Add the missing social.png files (make social can generate them), then rebuild.",
              file=sys.stderr)
        return 1
    print(f"Social images present for all {count} rendered posts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
