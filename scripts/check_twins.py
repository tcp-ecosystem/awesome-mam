#!/usr/bin/env python3
"""Verify that every `.mam.md` ships a byte-identical `.mam` twin.

The library's distribution rule: the `.mam.md` is the readable source of
truth, the `.mam` is the same bytes for tooling and editors that key off
the `.mam` extension. They must never drift.

Usage:
    python scripts/check_twins.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".github", "scripts", "docs", "node_modules"}


def main() -> int:
    checked = 0
    failures: list[str] = []

    for path in sorted(ROOT.rglob("*.mam.md")):
        if path.name == "README.md":
            continue
        relative = path.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        twin = path.with_name(path.name[: -len(".md")])  # x.mam.md -> x.mam
        checked += 1
        if not twin.exists():
            failures.append(f"missing twin: {relative.as_posix()} -> {twin.name}")
            continue
        if twin.read_bytes() != path.read_bytes():
            failures.append(f"twin differs from source: {relative.as_posix()}")

    if checked == 0:
        print("error: no .mam.md files found — run from a checkout of awesome-mam")
        return 1

    print(f"twins checked: {checked}, failures: {len(failures)}")
    for failure in failures:
        print(" -", failure)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
