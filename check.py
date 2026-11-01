#!/usr/bin/env python3
"""Catch broken local links, missing assets, and invalid article anchors."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "_site"
BASE = urlsplit(json.loads((ROOT / "site.json").read_text())["url"]).path.rstrip("/")


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.ids, self.headings = [], set(), []
        self.duplicate_ids = set()
        self.feed(text)

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if identifier := attributes.get("id"):
            if identifier in self.ids:
                self.duplicate_ids.add(identifier)
            self.ids.add(identifier)
        for attr in ["href", "src"]:
            if value := attributes.get(attr):
                self.links.append(value)
        if tag == "h1":
            self.headings.append(tag)


def main():
    documents = {p: Document(p.read_text()) for p in SITE.rglob("*.html")}
    if not documents:
        raise SystemExit("No built pages; run python build.py first")
    errors = []
    for source, document in documents.items():
        if len(document.headings) != 1:
            errors.append(f"{source.relative_to(SITE)}: expected exactly one h1")
        if document.duplicate_ids:
            errors.append(f"{source.relative_to(SITE)}: duplicate IDs {document.duplicate_ids}")
        for link in document.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            local_path = unquote(url.path)
            if local_path.startswith("/"):
                if BASE and not (local_path == BASE or local_path.startswith(BASE + "/")):
                    errors.append(f"{source.name}: link outside configured base path {link}")
                    continue
                target = SITE / local_path.removeprefix(BASE).lstrip("/")
            elif local_path:
                target = source.parent / local_path
            else:
                target = source
            target = target.resolve()
            if not target.is_relative_to(SITE.resolve()):
                errors.append(f"{source.name}: link escapes site {link}")
                continue
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                errors.append(f"{source.relative_to(SITE)}: missing target {link}")
            elif url.fragment and target.suffix == ".html":
                target_doc = documents.get(target) or Document(target.read_text())
                if unquote(url.fragment) not in target_doc.ids:
                    errors.append(f"{source.relative_to(SITE)}: missing anchor {link}")
    for name in ["sitemap.xml", "feed.xml"]:
        try:
            ET.parse(SITE / name)
        except (ET.ParseError, OSError) as error:
            errors.append(f"{name}: {error}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        raise SystemExit(1)
    print(f"Checked {len(documents)} pages: internal links, anchors, assets, headings, sitemap, and RSS are valid.")


if __name__ == "__main__":
    main()
