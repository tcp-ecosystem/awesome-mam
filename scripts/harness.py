#!/usr/bin/env python3
"""awesome-mam gate: execute every Python block in every reference file.

The library's core promise is that its files are *executable*, not prose.
This script proves it: it loads each `.mam.md` body in dependency order,
registers every module namespace so downstream imports resolve exactly the
way a MAM runtime resolves module dependencies, then executes every test
block and every `test_*` function.

Folder order is dependency order:

    01-modules -> 02-components -> 03-workflows -> 04-services -> 05-systems

`templates/` runs last: starter files must be correct too, so they carry
executable tests like everything else.

Usage:
    python scripts/harness.py

Exit code 0 only when every body executed and every test passed. No
third-party dependencies, no network, no files written.
"""

from __future__ import annotations

import re
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FOLDERS = [
    "01-modules",
    "02-components",
    "03-workflows",
    "04-services",
    "05-systems",
    "templates",
]
STDLIB = {
    "typing", "time", "math", "json", "re", "types", "uuid", "hashlib",
    "hmac", "functools", "collections", "dataclasses", "enum", "itertools",
    "string", "random", "datetime", "pathlib",
}

PYTHON_BLOCK = re.compile(r"```python\n(.*?)```", re.S)
SECTION = r"^## {heading}\n(.*?)(?=^## |\Z)"
IMPORT = re.compile(r"^\s*from ([a-z_][a-z0-9_]*) import", re.M)


def section(source: str, heading: str) -> str | None:
    match = re.search(SECTION.format(heading=heading), source, re.S | re.M)
    return match.group(1) if match else None


def blocks(text: str) -> list[str]:
    return PYTHON_BLOCK.findall(text)


def collect() -> list[dict]:
    pending: list[dict] = []
    for folder in FOLDERS:
        directory = ROOT / folder
        if not directory.is_dir():
            print(f"warning: folder missing, skipped: {folder}")
            continue
        for path in sorted(directory.rglob("*.mam.md")):
            if path.name == "README.md":
                continue
            source = path.read_text(encoding="utf-8")
            name = path.name[: -len(".mam.md")]
            python_zone = section(source, "Python")
            if python_zone is None:
                print(f"error: no ## Python section in {path.relative_to(ROOT)}")
                continue
            body_blocks = blocks(python_zone)
            if not body_blocks:
                print(f"error: no python block in {path.relative_to(ROOT)}")
                continue
            tests_zone = section(source, "Tests")
            deps = [d for d in IMPORT.findall(body_blocks[0]) if d not in STDLIB]
            pending.append({
                "path": path.relative_to(ROOT).as_posix(),
                "name": name,
                "body": body_blocks[0],
                "tests": blocks(tests_zone) if tests_zone else [],
                "deps": deps,
            })
    return pending


def main() -> int:
    pending = collect()
    if not pending:
        print("error: no reference files found — run from a checkout of awesome-mam")
        return 1

    registered: dict[str, dict] = {}
    total = passed = 0
    failures: list[str] = []

    while pending:
        progressed = False
        stalled: list[dict] = []
        for item in pending:
            if not all(dep in registered for dep in item["deps"]):
                stalled.append(item)
                continue
            progressed = True
            namespace: dict = {}
            try:
                exec(compile(item["body"], item["name"], "exec"), namespace)
            except Exception as exc:  # noqa: BLE001 - report, never crash the gate
                failures.append(f"{item['path']}: body failed — {type(exc).__name__}: {exc}")
                continue

            package = item["name"].replace("-", "_")
            registered[package] = namespace
            module = types.ModuleType(package)
            for key, value in namespace.items():
                if not key.startswith("__"):
                    setattr(module, key, value)
            sys.modules[package] = module

            for index, block in enumerate(item["tests"]):
                try:
                    exec(compile(block, f"{item['name']}@block{index}", "exec"), namespace)
                except Exception as exc:  # noqa: BLE001
                    failures.append(
                        f"{item['path']} block {index}: exec failed — {type(exc).__name__}: {exc}")
                    continue
                tests = {
                    key: value for key, value in namespace.items()
                    if key.startswith("test_") and callable(value)
                }
                for key, function in tests.items():
                    total += 1
                    try:
                        function()
                    except Exception as exc:  # noqa: BLE001
                        failures.append(
                            f"{item['path']}::{key} — {type(exc).__name__}: {exc}")
                    else:
                        passed += 1
                for key in tests:
                    namespace.pop(key, None)

        pending = stalled
        if pending and not progressed:
            for item in pending:
                failures.append(f"{item['path']}: unresolved imports {item['deps']}")
            break

    print(f"\nfiles executed: {len(registered)}")
    print(f"test cases: {passed}/{total} passed, {len(failures)} failure(s)")
    for failure in failures:
        print(" -", failure)
    return 0 if failures == [] and total > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
