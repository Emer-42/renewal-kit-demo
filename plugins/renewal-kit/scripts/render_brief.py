#!/usr/bin/env python3
# SYNTHETIC DEMO DATA kit — renders a structured brief to HTML from a fixed template.
"""Render briefs/<account>.html from a content JSON file and templates/brief.html.

Usage: python3 scripts/render_brief.py content/<account>.json [--out PATH]

The model decides what goes in content.json. This script fixes everything that
must never change: the six headings and their order, the numbers table, the
file name and the layout. Output is byte-identical for identical input: no
timestamps, fixed section order, sorted number rows, "\\n" line endings.
Exits non-zero (and writes nothing) if the content is missing or malformed.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from html import escape
from pathlib import Path
from string import Template

PLUGIN = Path(__file__).resolve().parent.parent
TEMPLATE = PLUGIN / "templates" / "brief.html"
PROJECT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd())
BRIEFS = PROJECT / "briefs"
BANNER = "SYNTHETIC DEMO DATA — every person and organisation here is made up."

HEADINGS = ["At a glance", "Numbers", "What went wrong", "Open issues", "Risks", "Gaps"]
RATE_KEYS = {"digital_payment_rate", "collection_rate"}
NUMBER_LABELS = {
    "statements_sent": "Statements sent",
    "digital_payment_rate": "Digital payment rate",
    "collection_rate": "Collection rate",
    "psat": "PSAT",
    "support_calls": "Support calls",
}


class ContentError(ValueError):
    pass


def fmt(key: str, v: float | int | None) -> str:
    if v is None:
        return "—"
    if key in RATE_KEYS:
        return f"{v * 100:.0f}%"
    return f"{v:,.0f}"


def change(key: str, first: float, last: float) -> str:
    if key in RATE_KEYS:
        return f"{(last - first) * 100:+.0f} pts"
    if key == "psat":
        return f"{last - first:+.0f} pts"
    pct = f" ({(last - first) / first * 100:+.1f}%)" if first else ""
    return f"{last - first:+,.0f}{pct}"


def validate(content: dict) -> None:
    for field in ("account", "client", "numbers", "sections"):
        if field not in content:
            raise ContentError(f"content is missing '{field}'")
    sections = content["sections"]
    missing = [h for h in HEADINGS if h not in sections]
    if missing:
        raise ContentError(f"content.sections is missing {missing}")
    for h in HEADINGS:
        if not isinstance(sections[h], list) or not all(isinstance(s, str) for s in sections[h]):
            raise ContentError(f"section '{h}' must be a list of strings")
    numbers = content["numbers"]
    for field in ("source", "window", "values"):
        if field not in numbers:
            raise ContentError(f"content.numbers is missing '{field}'")


def render_section(title: str, items: list[str]) -> str:
    if title == "Open issues":
        rows = []
        for item in items:
            cells = [c.strip() for c in item.split("|")]
            if len(cells) != 3:
                raise ContentError(f"Open issues row must be 'ticket | issue | owner': {item!r}")
            ticket, issue, owner = cells
            owner_html = "<strong>no owner</strong>" if owner.lower() == "no owner" else escape(owner)
            rows.append(f"<tr><td>{escape(ticket)}</td><td>{escape(issue)}</td><td>{owner_html}</td></tr>")
        body = (
            "<table><thead><tr><th>Ticket</th><th>Issue</th><th>Owner</th></tr></thead>\n<tbody>\n"
            + "\n".join(rows)
            + "\n</tbody></table>"
        )
    elif title == "Risks":
        body = "<ol>\n" + "\n".join(f"<li>{escape(i)}</li>" for i in items) + "\n</ol>"
    else:
        body = "<ul>\n" + "\n".join(f"<li>{escape(i)}</li>" for i in items) + "\n</ul>"
    return f'<section id="{title.lower().replace(" ", "-")}">\n<h2>{escape(title)}</h2>\n{body}\n</section>'


def render_numbers(numbers: dict) -> str:
    values = numbers["values"]
    rows = []
    for key in sorted(values, key=lambda k: list(NUMBER_LABELS).index(k) if k in NUMBER_LABELS else 99):
        v = values[key]
        first, last = v.get("first"), v.get("last")
        delta = change(key, first, last) if first is not None and last is not None else "n/a"
        low_high = (
            f"{fmt(key, v['low'])} / {fmt(key, v['high'])}" if "low" in v and "high" in v else "—"
        )
        rows.append(
            f"<tr><td>{escape(NUMBER_LABELS.get(key, key))}</td><td>{fmt(key, first)}</td>"
            f"<td>{fmt(key, last)}</td><td>{escape(delta)}</td><td>{escape(low_high)}</td></tr>"
        )
    return "\n".join(rows)


def render(content: dict) -> str:
    validate(content)
    template = Template(TEMPLATE.read_text(encoding="utf-8"))
    sections = "\n".join(render_section(h, content["sections"][h]) for h in HEADINGS)
    return template.substitute(
        banner=escape(BANNER),
        title=escape(f"{content['client']} — renewal brief for {content.get('manager', 'Jordan')}"),
        account=escape(content["account"]),
        source=escape(content["numbers"]["source"]),
        window=escape(content["numbers"]["window"]),
        number_rows=render_numbers(content["numbers"]),
        sections=sections,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("content", help="content JSON, e.g. content/lakeshore-health.json")
    parser.add_argument("--out", help="output path (default briefs/<account>.html)")
    args = parser.parse_args()

    try:
        content = json.loads(Path(args.content).read_text(encoding="utf-8"))
        html = render(content)
    except (OSError, json.JSONDecodeError, ContentError, KeyError, TypeError) as e:
        print(f"render_brief: {e}", file=sys.stderr)
        return 1

    out = Path(args.out) if args.out else BRIEFS / f"{content['account']}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    resolved = out.resolve()
    print(resolved.relative_to(PROJECT) if resolved.is_relative_to(PROJECT) else resolved)
    return 0


if __name__ == "__main__":
    sys.exit(main())
