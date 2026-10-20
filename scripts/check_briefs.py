#!/usr/bin/env python3
# SYNTHETIC DEMO DATA kit — checks briefs/*.md against accounts/*/metrics.csv.
"""Check every brief in briefs/ for the six required headings and for numbers
that match metrics.csv. Exit 0 only when every brief passes.

Usage: python3 scripts/check_briefs.py [brief.md ...]

Per brief:
  * all six headings are present (## At a glance … ## Gaps);
  * every digital payment rate, collection rate and PSAT figure stated in the
    brief matches a month in that account's metrics.csv (±0.5 pt), and the
    latest month's value is stated at least once.
Writes briefs/check-report.md: what was checked, pass/fail per brief, timestamp.
"""
from __future__ import annotations

import csv
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
ACCOUNTS = KIT / "accounts"
BRIEFS = KIT / "briefs"
REPORT = BRIEFS / "check-report.md"

HEADINGS = [
    "## At a glance",
    "## Numbers",
    "## What went wrong",
    "## Open issues",
    "## Risks",
    "## Gaps",
]

# column -> (label used in output, regex that marks a mention, is_rate)
METRICS: dict[str, tuple[str, re.Pattern[str], bool]] = {
    "digital_payment_rate": ("digital payments", re.compile(r"digital[\s-]+pay", re.I), True),
    "collection_rate": ("collection rate", re.compile(r"collection", re.I), True),
    "psat": ("PSAT", re.compile(r"\bpsat\b", re.I), False),
}
TOLERANCE = 0.5  # percentage points

PERCENT = re.compile(r"(?<![\d.])(\d{1,3}(?:\.\d+)?)\s*%")
# Integers 0–100 that are not signed, not part of a date/ticket, not followed by %/pts.
PLAIN = re.compile(r"(?<![\d.+\-−/\w])(\d{1,3}(?:\.\d+)?)(?![\d%./-])(?!\s*(?:pts?|points?)\b)(?![-–]\d)")
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def month_label(ym: str) -> str:
    return MONTHS[int(ym.split("-")[1]) - 1]


def load_metrics(account: str) -> list[dict[str, str]]:
    path = ACCOUNTS / account / "metrics.csv"
    with path.open(newline="") as f:
        return sorted(csv.DictReader(f), key=lambda r: r["month"])


def metric_values(rows: list[dict[str, str]], col: str, is_rate: bool) -> list[tuple[str, float]]:
    out = []
    for r in rows:
        v = r[col].strip()
        if v:
            x = float(v)
            out.append((r["month"], x * 100 if is_rate else x))
    return out


def stated_numbers(text: str, col: str) -> list[tuple[float, str]]:
    """Numbers in the brief attributed to this metric, with the line they came from."""
    label, mention, is_rate = METRICS[col]
    found: list[tuple[float, str]] = []
    for line in text.splitlines():
        if line.startswith("#"):
            continue
        mentions = [(m.start(), c) for c, (_, pat, _) in METRICS.items() for m in pat.finditer(line)]
        if not any(c == col for _, c in mentions):
            continue
        mentions.sort()
        numbers = PERCENT.finditer(line) if is_rate else PLAIN.finditer(line)
        for m in numbers:
            # attribute to the nearest metric mention before the number (else the first after)
            before = [c for pos, c in mentions if pos < m.start()]
            owner = before[-1] if before else mentions[0][1]
            if owner != col:
                continue
            val = float(m.group(1))
            if not is_rate and not (0 <= val <= 100):
                continue
            found.append((val, line.strip()))
    return found


def check_brief(path: Path) -> list[str]:
    account = path.stem
    text = path.read_text(encoding="utf-8")
    failures: list[str] = []

    for h in HEADINGS:
        if not re.search(rf"^{re.escape(h)}\s*$", text, re.M):
            failures.append(f'missing heading "{h}"')

    if not (ACCOUNTS / account / "metrics.csv").exists():
        failures.append(f"no accounts/{account}/metrics.csv to check numbers against")
        return failures

    rows = load_metrics(account)
    for col, (label, _, is_rate) in METRICS.items():
        values = metric_values(rows, col, is_rate)
        if not values:
            continue
        latest_month, latest = values[-1]
        mlabel = month_label(latest_month)
        unit = "%" if is_rate else ""
        stated = stated_numbers(text, col)
        if not stated:
            failures.append(f"{label} not stated; {latest:g}{unit} in metrics.csv ({mlabel})")
            continue
        known = [v for _, v in values]
        for val, _line in stated:
            if not any(abs(val - k) <= TOLERANCE for k in known):
                failures.append(
                    f"{label} {val:g}{unit} in brief, {latest:g}{unit} in metrics.csv ({mlabel})"
                )
        if not any(abs(val - latest) <= TOLERANCE for val, _ in stated):
            failures.append(
                f"{label} latest month missing; {latest:g}{unit} in metrics.csv ({mlabel}) not stated"
            )
    return list(dict.fromkeys(failures))


def write_report(results: dict[str, list[str]], stamp: str) -> None:
    lines = [
        "<!-- SYNTHETIC DEMO DATA — generated by scripts/check_briefs.py -->",
        "# Brief check report",
        "",
        f"Run: {stamp}  ",
        "Checked: six headings present (At a glance, Numbers, What went wrong, Open issues, Risks, Gaps); "
        "digital payment rate, collection rate and PSAT figures match accounts/<account>/metrics.csv "
        f"(±{TOLERANCE} pt), latest month stated.",
        "",
        "| Brief | Result | Findings |",
        "|---|---|---|",
    ]
    for name, fails in results.items():
        status = "pass" if not fails else "FAIL"
        lines.append(f"| {name} | {status} | {'; '.join(fails) if fails else '—'} |")
    passed = sum(1 for f in results.values() if not f)
    lines += ["", f"{passed} of {len(results)} briefs pass.", ""]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str]) -> int:
    if argv:
        paths = [Path(a) for a in argv]
    else:
        paths = sorted(p for p in BRIEFS.glob("*.md") if p.name != REPORT.name)
    if not paths:
        print("✗ no briefs found in briefs/")
        return 1

    results: dict[str, list[str]] = {}
    for p in paths:
        fails = check_brief(p)
        results[p.stem] = fails
        for f in fails:
            print(f"✗ {p.stem} · {f}")

    failed = sum(1 for f in results.values() if f)
    total = len(results)
    stamp = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")
    write_report(results, stamp)
    if failed:
        print(f"✗ {failed} of {total} briefs fail")
        return 1
    print(f"✓ {total} of {total} briefs pass")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
