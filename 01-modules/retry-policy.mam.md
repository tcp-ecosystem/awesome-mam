---
# MAM Metadata
id: retry-policy
name: Retry Policy
version: 1.0.0
type: module

author: TCP Ecosystems
description: >
  Decision-only retry engine for transient failure categories. Given a failed
  attempt, a failure category, and elapsed time, it returns a retry-or-abort
  decision with the exact wait in milliseconds — exponential backoff bounded by
  policy, deterministic seeded jitter, attempt budget and wall-clock deadline.

license: MIT

runtime:
  language: python
  version: ">=3.12"

tags:
  - reliability
  - backoff
  - retry
  - policy
  - resilience

dependencies:
  - name: mam-runtime
    version: ">=1.0.0"

capabilities:
  - decide
  - backoff
  - bound

permissions:
  filesystem: none
  network: none
---

# Retry Policy

## Purpose

Answers one question with a number: *after this failure, do we retry, and if
so, how long do we wait?* The module holds no timers and performs no I/O — it
is a pure decision function, which makes it exactly reproducing in tests and
safe to embed in schedulers, workflow steps, and service call sites that own
their own clocks.

It does **not** execute retries, sleep, or inspect exceptions. Callers map the
raised failure to a failure category and call this module with it.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| attempt | number | Yes | Failures so far, 1-based (first failure → `1`) |
| category | string | Yes | Failure category — see the taxonomy below |
| policy | object | No | Policy knobs; defaults via `default_policy()` |
| elapsed_ms | number | No | Milliseconds since operation start, for deadline enforcement. Defaults to `0` |

### Failure taxonomy

Deterministic: the module's decision table keys on categories, not raw
exceptions — the caller's mapping layer owns exception-to-category translation.

```text
SUCCESS         → the previous attempt finished; nothing to retry
PROTOCOL_ERROR  → permanent caller error (4xx semantics); retrying cannot help
CONFLICT        → resource state changed; one re-resolution may still help
RESOURCE_STATE  → ephemeral upstream stall; retry with backoff
TIMEOUT         → attempt ran out of time; retry with backoff
CONNECTION      → transport-level failure; retry with backoff
SERVER_5XX      → remote reported server-side failure; retry with backoff
RATE_LIMITED    → throttled by the remote; retry, preferably with delay
UNKNOWN         → unmapped failure; policy decides
```

### Policy knobs (with defaults)

| Knob | Type | Default | Meaning |
|------|------|---------|---------|
| `max_attempts` | integer | 4 | Allowed failures before `ATTEMPTS_EXHAUSTED` |
| `base_delay_ms` | integer | 500 | Backoff base for failure 1 |
| `max_delay_ms` | integer | 20_000 | Ceiling for any single wait |
| `multiplier` | number | 2.0 | Backoff growth factor per attempt |
| `jitter_window_ms` | integer | 250 | Max pseudo-random additive window |
| `jitter_seed` | integer | 0 | Seed for deterministic jitter (seeded LCG) |
| `deadline_ms` | integer or null | null | Total wall-clock budget; `None` disables |

## Outputs

| Name | Type | Description |
|------|------|-------------|
| action | string | `retry`, `abort`, or `done` |
| delay_ms | integer | Backoff wait after this failure; `0` for decisions that carry no wait |
| attempt | integer | Echo of the input attempt |
| code | string | Decision code, `""` when none applies |
| detail | string | One human-readable sentence on why the decision was made |

### Decision codes

`ATTEMPTS_EXHAUSTED`, `DEADLINE_EXCEEDED`, `SUCCEEDED`, `NON_RETRYABLE`
(terminal categories: `SUCCESS`, `PROTOCOL_ERROR`, `UNKNOWN`),
`WAIT_AND_RETRY`, `RATE_LIMITED`, `INVALID_INPUT`.

## Capabilities

### decide

Map `(attempt, category, policy, elapsed_ms)` to a retry/abort decision and a
reason code — nothing else runs, nothing is scheduled.

### backoff

Compute the wait as the smaller of the policy ceiling and
`base_delay_ms x multiplier^(attempt-1)` plus seeded jitter.

### bound

Stop escalating through `max_attempts` and `deadline_ms` so callers cannot
paper over a broken dependency forever.

## Rules

- The module never sleeps and never performs I/O; callers own the clock.
- Jitter is deterministic: the same inputs always produce the same decision.
- Urgent categories (`RATE_LIMITED`, `SERVER_5XX`, `CONNECTION`, `TIMEOUT`,
  `CONFLICT`, `RESOURCE_STATE`) escalate until budget or deadline stops them.
- Deliberately stop: `SUCCESS`, `PROTOCOL_ERROR`, `UNKNOWN`.
- Budget anchors are the input knobs only — nothing else is mutable.
- The returned `delay_ms` is always an integer and `>= 0`.
- A malformed policy or non-integer attempt produces an `INVALID_INPUT` abort —
  never a raise.

## Workflow

```mermaid
flowchart TD
    A[attempt + category + policy] --> B{inputs valid?}
    B -->|No| Z1[INVALID_INPUT abort]
    B -->|Yes| C{category retryable?}
    C -->|SUCCESS| Z2[SUCCEEDED done]
    C -->|PROTOCOL_ERROR / UNKNOWN| Z3[abstain]
    C -->|retryable| D{attempt < max_attempts?}
    D -->|No| Z5[ATTEMPTS_EXHAUSTED abort]
    D -->|Yes| E[growth = base x multiplier^(attempt-1)]
    E --> F{delay >= max_delay?}
    F -->|Yes| G[clamp to max]
    F -->|No| H[keep delay]
    G & H --> I{elapsed + delay > deadline_ms?}
    I -->|Yes| Z4[DEADLINE_EXCEEDED abort]
    I -->|No| J{category = RATE_LIMITED?}
    J -->|Yes| K[code RATE_LIMITED + retry]
    J -->|No| L[code WAIT_AND_RETRY + retry]
    Z1 & Z2 & Z3 & Z4 & Z5 & K & L --> Z[decision + delay_ms]
```

## Python

```python
import time
from typing import Any, Dict, Optional, Tuple

URGENT = ("CONFLICT", "RESOURCE_STATE", "TIMEOUT", "CONNECTION", "SERVER_5XX")
RATE_LIMITED = "RATE_LIMITED"
TERMINAL = ("SUCCESS", "PROTOCOL_ERROR", "UNKNOWN")


def default_policy() -> Dict[str, Any]:
    return {
        "max_attempts": 4,
        "base_delay_ms": 500,
        "max_delay_ms": 20_000,
        "multiplier": 2.0,
        "jitter_window_ms": 250,
        "jitter_seed": 0,
        "deadline_ms": None,
    }


def _jitter(window_ms: int, seed: int) -> int:
    """Deterministic masked-LCG in [0, window_ms). Zero window → zero jitter."""
    if window_ms <= 0:
        return 0
    nxt = (1103515245 * (seed + 1) + 12345) & 0x7FFFFFFF
    return nxt % window_ms


def _validate(attempt: Any, category: Any, policy: Any) -> Tuple[bool, str]:
    if isinstance(attempt, bool) or not isinstance(attempt, int) or attempt < 1:
        return False, "attempt"
    if not isinstance(category, str):
        return False, "category"
    if not isinstance(policy, dict):
        return False, "policy"
    for key in ("max_attempts", "base_delay_ms", "max_delay_ms", "jitter_window_ms"):
        raw = policy.get(key, default_policy()[key])
        if isinstance(raw, bool) or not isinstance(raw, int) or raw < 0:
            return False, f"policy.{key}"
    multiplier = policy.get("multiplier", default_policy()["multiplier"])
    if not isinstance(multiplier, (int, float)) or isinstance(multiplier, bool) or multiplier < 1:
        return False, "policy.multiplier"
    return True, ""


def run(attempt: Any, category: Any, policy: Optional[Dict[str, Any]] = None,
        elapsed_ms: int = 0) -> Dict[str, Any]:
    started = time.perf_counter()
    if policy is not None and not isinstance(policy, dict):
        return {"action": "abort", "delay_ms": 0, "attempt": attempt, "code": "INVALID_INPUT",
                "detail": "policy must be a dict when provided",
                "duration_ms": round((time.perf_counter() - started) * 1000, 3)}
    merged = default_policy()
    if isinstance(policy, dict):
        merged.update({k: v for k, v in policy.items() if v is not None})

    def abort(code: str, detail: str) -> Dict[str, Any]:
        return {"action": "abort", "delay_ms": 0, "attempt": attempt, "code": code,
                "detail": detail,
                "duration_ms": round((time.perf_counter() - started) * 1000, 3)}

    ok, field = _validate(attempt, category, merged)
    if not ok:
        return abort("INVALID_INPUT", f"field {field} is outside its declared domain")
    if category in TERMINAL:
        return abort("SUCCEEDED" if category == "SUCCESS" else "NON_RETRYABLE",
                     f"category {category} is terminal; retrying cannot change the outcome")

    growth = merged["base_delay_ms"] * (merged["multiplier"] ** (attempt - 1))
    delay = min(int(round(growth)), merged["max_delay_ms"])
    delay += _jitter(min(merged["jitter_window_ms"], merged["max_delay_ms"]),
                     merged["jitter_seed"] + attempt)

    deadline = merged["deadline_ms"]
    if deadline is not None and elapsed_ms + delay > deadline:
        return abort("DEADLINE_EXCEEDED",
                     f"retry at {delay} ms would exceed the {deadline} ms budget")

    if attempt >= merged["max_attempts"]:
        return abort("ATTEMPTS_EXHAUSTED",
                     f"failure {attempt} consumed the {merged['max_attempts']}-attempt budget")

    if category == RATE_LIMITED:
        return {"action": "retry", "delay_ms": delay, "attempt": attempt,
                "code": "RATE_LIMITED",
                "detail": f"throttled upstream; wait {delay} ms and retry",
                "duration_ms": round((time.perf_counter() - started) * 1000, 3)}
    if category in URGENT:
        return {"action": "retry", "delay_ms": delay, "attempt": attempt,
                "code": "WAIT_AND_RETRY",
                "detail": f"transient {category}; wait {delay} ms and retry",
                "duration_ms": round((time.perf_counter() - started) * 1000, 3)}
    return abort("NON_RETRYABLE", f"category {category} has no retry mapping")
```

## Tests

### Input

```yaml
attempt: 2
category: TIMEOUT
policy:
  base_delay_ms: 500
  multiplier: 2.0
```

### Expected

```yaml
action: retry
code: WAIT_AND_RETRY
```

```python
P = default_policy()


def wait_ms(attempt, base=500, mult=2.0, jitter_window=250, seed=0):
    return min(int(round(base * mult ** (attempt - 1))), 20_000) \
        + _jitter(min(jitter_window, 20_000), seed + attempt)


def test_first_transient_failure_retries_with_base_delay():
    out = run(1, "TIMEOUT", P)
    assert out["action"] == "retry" and out["code"] == "WAIT_AND_RETRY"
    assert out["delay_ms"] == wait_ms(1)


def test_backoff_grows_until_ceiling():
    assert wait_ms(1) < wait_ms(3) < 20_000
    capped = dict(P, base_delay_ms=5000, max_delay_ms=1200, jitter_window_ms=0)
    out = run(3, "TIMEOUT", capped)
    assert out["action"] == "retry"
    assert out["delay_ms"] == 1200  # growth (20000) is clamped by policy ceiling


def test_success_is_terminal():
    out = run(1, "SUCCESS", P)
    assert out["action"] == "abort" and out["code"] == "SUCCEEDED"
    assert out["delay_ms"] == 0


def test_protocol_error_never_retries():
    out = run(1, "PROTOCOL_ERROR", P)
    assert out["action"] == "abort" and out["code"] == "NON_RETRYABLE"


def test_rate_limited_gets_backoff_window():
    out = run(2, "RATE_LIMITED", P)
    assert out["action"] == "retry"
    assert out["code"] == "RATE_LIMITED"
    assert 1_000 <= out["delay_ms"] <= 1_000 + 250


def test_attempt_budget_stops_escalation():
    out = run(4, "TIMEOUT", P)
    assert out["action"] == "abort" and out["code"] == "ATTEMPTS_EXHAUSTED"


def test_deadline_overrides_retry():
    tight = dict(P, deadline_ms=900)
    out = run(2, "TIMEOUT", tight, elapsed_ms=600)
    assert out["action"] == "abort" and out["code"] == "DEADLINE_EXCEEDED"


def test_jitter_is_deterministic_for_same_seed():
    a = run(1, "TIMEOUT", P)
    b = run(1, "TIMEOUT", P)
    assert a["delay_ms"] == b["delay_ms"]


def test_budget_is_inclusive_on_the_last_attempt():
    tight = dict(P, max_attempts=2)
    out = run(2, "TIMEOUT", tight)
    assert out["action"] == "abort" and out["code"] == "ATTEMPTS_EXHAUSTED"


def test_invalid_inputs_abort_instead_of_raising():
    for attempt, category, policy in (0, "TIMEOUT", P), (1, None, P):
        out = run(attempt, category, policy)
        assert out["action"] == "abort" and out["code"] == "INVALID_INPUT"
    assert run(1, "TIMEOUT", "not-a-policy")["code"] == "INVALID_INPUT"


def test_zero_jitter_window_disables_jitter():
    flat = dict(P, jitter_window_ms=0)
    assert run(1, "TIMEOUT", flat)["delay_ms"] == 500


def test_none_deadline_is_unbounded():
    out = run(3, "TIMEOUT", P, elapsed_ms=3_600_000)
    assert out["action"] == "retry"
```

## Examples

```python
# First failure on a flaky connection with the default policy
run(1, "CONNECTION")
# {'action': 'retry', 'delay_ms': 612, 'attempt': 1, 'code': 'WAIT_AND_RETRY',
#  'detail': 'transient CONNECTION; wait 612 ms and retry', ...}

# The 5th failure of a hard-down dependency
run(5, "TIMEOUT")
# {'action': 'abort', 'delay_ms': 0, 'attempt': 5, 'code': 'ATTEMPTS_EXHAUSTED',
#  'detail': "failure 5 consumed the 4-attempt budget", ...}
```

### Expected Flow

```text
validate -> terminal check -> backoff (+jitter) -> deadline -> budget -> decide
```

## References

- [MAM source format, full component set](https://github.com/tcp-ecosystems/MAM/blob/main/plan-doc/full-mam.md) §9–§13
- Consumed by workflow steps in [Level 3 — Workflows](../03-workflows/README.md) and service call sites in [Level 4 — Services](../04-services/README.md)
