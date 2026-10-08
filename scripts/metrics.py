#!/usr/bin/env python3
# SYNTHETIC DEMO DATA kit — reads accounts/*/metrics.csv only.
"""Print each account's last N months of metrics and the first→last change.

Usage: python3 scripts/metrics.py [--months N] [account ...]

Rates are stored as fractions and shown as %; their change is in percentage
points. Blank cells mean "not applicable yet" and are shown as "—", never 0.
The change uses the first and last month in the window that both have a
value; low/high are listed so mid-window dips the endpoints hide stay visible.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
ACCOUNTS = KIT / "accounts"

RATES = {"digital_payment_rate", "collection_rate"}
COLUMNS = ["statements_sent", "digital_payment_rate", "collection_rate", "psat", "support_calls"]


def parse(value: str) -> float | None:
    value = value.strip()
    return float(value) if value else None


def fmt(col: str, v: float | None) -> str:
    if v is None:
        return "—"
    if col in RATES:
        return f"{v * 100:.0f}%"
    return f"{v:,.0f}"


def change(col: str, first: float, last: float) -> str:
    if col in RATES:
        return f"{(last - first) * 100:+.0f} pts"
    if col == "psat":
        return f"{last - first:+.0f} pts"
    pct = f" ({(last - first) / first * 100:+.1f}%)" if first else ""
    return f"{last - first:+,.0f}{pct}"


def load(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    missing = set(COLUMNS + ["month"]) - set(rows[0].keys() if rows else [])
    if missing:
        raise ValueError(f"{path}: missing columns {sorted(missing)}")
    return sorted(rows, key=lambda r: r["month"])


def report(account: str, months: int) -> None:
    path = ACCOUNTS / account / "metrics.csv"
    rows = load(path)
    window = rows[-months:]
    print(f"## {account}  ({path.relative_to(KIT)})")
    note = "" if len(window) == months else f"  [only {len(window)} month(s) in file]"
    print(f"Window: {window[0]['month']} → {window[-1]['month']}{note}")

    width = max(len(c) for c in COLUMNS)
    print(f"{'month':<{width}}  " + "  ".join(f"{r['month']:>8}" for r in window))
    for col in COLUMNS:
        vals = [parse(r[col]) for r in window]
        cells = "  ".join(f"{fmt(col, v):>8}" for v in vals)
        present = [(r["month"], v) for r, v in zip(window, vals) if v is not None]
        if len(present) >= 2:
            (m0, v0), (m1, v1) = present[0], present[-1]
            lo, hi = min(v for _, v in present), max(v for _, v in present)
            summary = f"{m0}→{m1}: {change(col, v0, v1)}; low {fmt(col, lo)}, high {fmt(col, hi)}"
        else:
            summary = "change: n/a (fewer than 2 months with a value)"
        print(f"{col:<{width}}  {cells}   {summary}")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("accounts", nargs="*", help="account folder names (default: all)")
    parser.add_argument("--months", type=int, default=4)
    args = parser.parse_args()
    if args.months < 1:
        parser.error("--months must be >= 1")

    names = args.accounts or sorted(p.parent.name for p in ACCOUNTS.glob("*/metrics.csv"))
    status = 0
    for name in names:
        try:
            report(name, args.months)
        except (FileNotFoundError, ValueError) as e:
            print(f"error: {e}", file=sys.stderr)
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main())
