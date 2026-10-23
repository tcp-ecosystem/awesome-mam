---
# MAM Metadata
id: component-template
name: Component Template
version: 1.0.0
type: component

author: Your Name
description: >
  A correct starting point for a Level 2 component: state that outlives a
  call, an explicit Memory section, exports with a frozen contract, a
  validated configuration at construction, and bounded internal growth.
  Copy both files, rename the id, and replace the bounded-counter logic
  with your own state machine — keep the handle discipline.

license: MIT

runtime:
  language: python
  version: ">=3.12"

tags:
  - template
  - component
  - starter
  - state

dependencies:
  - name: mam-runtime
    version: ">=1.0.0"

capabilities:
  - start
  - record
  - observe

permissions:
  filesystem: none
  network: none
---

# Component Template

## Purpose

The step from module to component is **state**. This template carries the
three exports every component in this library exposes: a constructor that
validates configuration and returns a handle, a mutating operation that
records against that handle, and an observation that answers questions
without changing anything. The example state is a bounded counter with a
per-key breakdown — replace it, keep the shape.

## Memory

State that outlives a call, persisted by the caller through the handle:

```text
handle = {
  "config": { "cap": int, "max_keys": int },
  "counts": { "<key>": int },
  "total":  int
}
```

- **Who persists it:** the caller — the handle crosses every call boundary.
- **Growth bound:** at most `config.max_keys` distinct keys; a new key beyond
  that is refused with `KEY_LIMIT_REACHED` instead of growing without bound.
- **Corrupt handle:** every export returns a coded `INVALID_HANDLE` envelope
  and refuses to act.

## Exports

| Export | Inputs | Returns | Contract |
|--------|--------|---------|----------|
| `start(config)` | `{cap, max_keys}` | `{valid, handle, code, errors, duration_ms}` | Configuration validated once; invalid config never produces a handle |
| `record(handle, key, amount?)` | key + positive integer amount | `{code, total, count, duration_ms}` | Mutates the handle; refuses on cap, key-space and input violations |
| `observe(handle)` | — | `{total, cap, keys, top, code}` | Read-only snapshot for health probes and dashboards |

## Inputs

### `start` — configuration

```text
{ "cap":      integer 1..1_000_000,   # maximum total this instance will count
  "max_keys": integer 1..10_000 }     # bounded key space
```

### `record` — arguments

| Name | Type | Required | Description |
|------|------|----------|-------------|
| handle | object | Yes | From `start` |
| key | string | Yes | 1–32 printable characters; the dimension being counted |
| amount | integer | No | Positive integer, default `1` |

## Outputs

| Name | Type | Description |
|------|------|-------------|
| code | string | `""`, `INVALID_CONFIG`, `INVALID_HANDLE`, `INVALID_INPUT`, `KEY_LIMIT_REACHED`, `CAP_REACHED` |
| total | integer | Running total after the call |
| count | integer | Count for the key after the call |
| top | array | Up to three `{key, count}` pairs, highest first |
| duration_ms | number | Wall-clock cost of this call |

## Capabilities

### start

Validate configuration once and produce the persistence handle.

### record

Mutate the handle under all invariants: input shape, key space, cap.

### observe

Report state without changing it.

## Rules

- The cap is a hard bound: the call that would exceed it is refused (`CAP_REACHED`) and the handle is left unchanged.
- The key space is bounded from configuration (`KEY_LIMIT_REACHED`), so hostile caller cardinality cannot grow memory without limit.
- `record` validates before mutating; a refused call never half-applies.
- `observe` never mutates and never allocates unbounded output (`top` is capped at three).
- The configuration is frozen at `start`; no export edits it.
- Booleans are not integers for `amount` (`True` is not `1`).
- The component imports nothing outside the standard library.

## Workflow

```mermaid
flowchart TD
    A[start: config] --> B{valid cap and max_keys?}
    B -->|No| C[INVALID_CONFIG, no handle]
    B -->|Yes| D[handle: totals empty, total 0]
    E[record: key, amount] --> F{handle usable?}
    F -->|No| G[INVALID_HANDLE]
    F -->|Yes| H{amount valid, key length 1..32?}
    H -->|No| I[INVALID_INPUT]
    H -->|Yes| J{new key and key space full?}
    J -->|Yes| K[KEY_LIMIT_REACHED]
    J -->|No| L{total + amount > cap?}
    L -->|Yes| M[CAP_REACHED, state untouched]
    L -->|No| N[apply: counts[key], total]
    O[observe] --> P[snapshot: total, top three, code]
```

## Python

```python
import time
from typing import Any, Dict, List

TOP_LIMIT = 3


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _usable(handle: Any) -> bool:
    if not isinstance(handle, dict):
        return False
    if not isinstance(handle.get("config"), dict) or not isinstance(handle.get("counts"), dict):
        return False
    if not _is_int(handle.get("total")) or not _is_int(handle["config"].get("cap")):
        return False
    return True


def start(config: Any) -> Dict[str, Any]:
    started = time.perf_counter()

    def envelope(valid: bool, handle: Any = None, code: str = "",
                 errors: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
        return {"valid": valid, "handle": handle, "code": code, "errors": errors or [],
                "duration_ms": round((time.perf_counter() - started) * 1000, 3)}

    if not isinstance(config, dict):
        return envelope(False, errors=[{"path": "config", "code": "TYPE_MISMATCH"}])
    cap = config.get("cap")
    max_keys = config.get("max_keys")
    errors = []
    if not _is_int(cap) or not 1 <= cap <= 1_000_000:
        errors.append({"path": "cap", "code": "OUT_OF_RANGE"})
    if not _is_int(max_keys) or not 1 <= max_keys <= 10_000:
        errors.append({"path": "max_keys", "code": "OUT_OF_RANGE"})
    if errors:
        return envelope(False, code="INVALID_CONFIG", errors=errors)

    handle = {"config": {"cap": cap, "max_keys": max_keys}, "counts": {}, "total": 0}
    return envelope(True, handle)


def record(handle: Any, key: Any, amount: Any = 1) -> Dict[str, Any]:
    started = time.perf_counter()

    def envelope(code: str) -> Dict[str, Any]:
        usable = _usable(handle)
        return {
            "code": code,
            "total": handle.get("total") if usable else None,
            "count": handle["counts"].get(key, 0) if usable and isinstance(key, str) else None,
            "duration_ms": round((time.perf_counter() - started) * 1000, 3),
        }

    if not _usable(handle):
        return envelope("INVALID_HANDLE")
    if not isinstance(key, str) or not 1 <= len(key) <= 32:
        return envelope("INVALID_INPUT")
    if not _is_int(amount) or amount < 1:
        return envelope("INVALID_INPUT")

    counts = handle["counts"]
    if key not in counts and len(counts) >= handle["config"]["max_keys"]:
        return envelope("KEY_LIMIT_REACHED")
    if handle["total"] + amount > handle["config"]["cap"]:
        return envelope("CAP_REACHED")

    counts[key] = counts.get(key, 0) + amount
    handle["total"] = handle["total"] + amount
    return envelope("")


def observe(handle: Any) -> Dict[str, Any]:
    started = time.perf_counter()

    def envelope(valid: bool, **extra: Any) -> Dict[str, Any]:
        out = {"valid": valid, "total": None, "cap": None, "keys": 0, "top": [],
               "duration_ms": round((time.perf_counter() - started) * 1000, 3)}
        out.update(extra)
        return out

    if not _usable(handle):
        return envelope(False, code="INVALID_HANDLE")

    ranked = sorted(handle["counts"].items(), key=lambda item: (-item[1], item[0]))
    top = [{"key": key, "count": count} for key, count in ranked[:TOP_LIMIT]]
    return envelope(True, total=handle["total"], cap=handle["config"]["cap"],
                    keys=len(handle["counts"]), top=top)
```

## Tests

### Input

```yaml
config: { cap: 10, max_keys: 2 }
records: [{key: errors, amount: 3}, {key: errors, amount: 2}, {key: warns, amount: 5}]
```

### Expected

```yaml
total: 10
top: [{key: errors, count: 5}, {key: warns, count: 5}]
code: ""
```

```python
def fresh():
    out = start({"cap": 10, "max_keys": 2})
    assert out["valid"] is True, out
    return out["handle"]


def test_start_validates_and_produces_a_handle():
    out = start({"cap": 10, "max_keys": 2})
    assert out["valid"] is True and out["code"] == ""
    assert out["handle"] == {"config": {"cap": 10, "max_keys": 2}, "counts": {}, "total": 0}


def test_start_rejects_bad_config_with_paths():
    out = start({"cap": 0, "max_keys": "two"})
    assert out["valid"] is False and out["code"] == "INVALID_CONFIG"
    assert [e["path"] for e in out["errors"]] == ["cap", "max_keys"]


def test_record_accumulates_per_key_and_total():
    handle = fresh()
    assert record(handle, "errors", 3)["code"] == ""
    out = record(handle, "errors", 2)
    assert out["code"] == "" and out["count"] == 5 and out["total"] == 5


def test_cap_refusal_leaves_state_untouched():
    handle = fresh()
    record(handle, "errors", 9)
    out = record(handle, "warns", 2)
    assert out["code"] == "CAP_REACHED"
    assert handle["total"] == 9 and handle["counts"] == {"errors": 9}


def test_key_space_is_bounded():
    handle = fresh()
    record(handle, "errors")
    record(handle, "warns")
    out = record(handle, "infos")
    assert out["code"] == "KEY_LIMIT_REACHED"
    assert set(handle["counts"]) == {"errors", "warns"}


def test_existing_keys_keep_working_at_the_key_bound():
    handle = fresh()
    record(handle, "errors")
    record(handle, "warns")
    assert record(handle, "errors")["code"] == ""      # same key, not a new slot


def test_input_shape_and_booleans_are_refused():
    handle = fresh()
    assert record(handle, "", 1)["code"] == "INVALID_INPUT"
    assert record(handle, "errors", True)["code"] == "INVALID_INPUT"
    assert record(handle, "errors", 0)["code"] == "INVALID_INPUT"


def test_observe_is_read_only_and_top_is_bounded():
    handle = fresh()
    for key in ("a", "b"):
        record(handle, key)
    before = dict(handle["counts"])
    out = observe(handle)
    assert out["valid"] is True and out["keys"] == 2
    assert handle["counts"] == before
    assert len(out["top"]) <= 3


def test_corrupt_handles_are_coded():
    assert record({}, "errors")["code"] == "INVALID_HANDLE"
    assert observe("nope")["valid"] is False
```

## Examples

```python
counter = start({"cap": 1_000, "max_keys": 50})["handle"]

for outcome in outcomes:
    verdict = record(counter, outcome.category)
    if verdict["code"] == "CAP_REACHED":
        alarms.raise_alarm("counter cap reached; rotate the handle")

snapshot = observe(counter)
dashboard.emit("outcomes", snapshot["top"], total=snapshot["total"])
```

### Expected Flow

```text
config gate -> handle -> validated mutation (cap + key bound) -> read-only snapshot
```

## References

- Level contract: [Level 2 — Components](../../02-components/README.md)
- Copy instructions: [`templates/component/README.md`](README.md)
- [MAM source format, full component set](https://github.com/tcp-ecosystems/MAM/blob/main/plan-doc/full-mam.md)
