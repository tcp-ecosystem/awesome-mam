# Level guides

Five rungs, each with one question it answers. Pick the lowest rung that
answers yours; moving a file up a level is a rewrite, not a rename.

| Level | Question it answers | Folder | Template |
|-------|--------------------|--------|----------|
| 1 | "What is the decision?" | [`01-modules/`](../01-modules/README.md) | [`templates/module/`](../templates/module/README.md) |
| 2 | "What remembers between calls?" | [`02-components/`](../02-components/README.md) | [`templates/component/`](../templates/component/README.md) |
| 3 | "What happens when step 3 fails?" | [`03-workflows/`](../03-workflows/README.md) | [`templates/workflow/`](../templates/workflow/README.md) |
| 4 | "How does it live and die in production?" | [`04-services/`](../04-services/README.md) | [`templates/service/`](../templates/service/README.md) |
| 5 | "What is the repository as a whole?" | [`05-systems/`](../05-systems/README.md) | (no template — see contract) |

## Level 1 — Modules

**Pure.** No I/O, no state, no clock reads, standard library only. One
decision function, an envelope with a stable `code`, and tests for every
refusal.

Read: [`schema-validator`](../01-modules/schema-validator.mam.md) for input
gates, [`retry-policy`](../01-modules/retry-policy.mam.md) for a decision
table, [`rate-limiter`](../01-modules/rate-limiter.mam.md) for state passed
*through* a caller handle, [`structured-logging`](../01-modules/structured-logging.mam.md)
for redaction, [`config-loader`](../01-modules/config-loader.mam.md) for
composition against `schema-validator`.

Acceptance bar: [`01-modules/README.md` §5](../01-modules/README.md#5-acceptance-gate-what-mam-validate--review-enforce-before-a-module-is-listed).

## Level 2 — Components

**Stateful.** The handle is the only state; the caller persists it. Required
sections: `## Memory` (state shape, persistence, corruption behavior) and
`## Exports` (inputs, outputs, contract per export). Configuration is
validated once and frozen.

Read: [`http-runtime`](../02-components/http-runtime.mam.md) (composes four
modules into one boundary), [`pacing-circuit`](../02-components/pacing-circuit.mam.md)
(a breaker state machine), [`config-factory`](../02-components/config-factory.mam.md)
(hot reload with path-only audit).

Contract: [`02-components/README.md`](../02-components/README.md).

## Level 3 — Workflows

**Resumable.** Two exports: `run` (plan the next step) and `advance` (absorb
an outcome). Four failure answers must be written down explicitly — retry,
replay, compensate, stop — plus idempotency keys and a caller-held ledger.

Read: [`order-fulfillment`](../03-workflows/order-fulfillment.mam.md) for
compensation ordering, [`dataset-publish`](../03-workflows/dataset-publish.mam.md)
for paced egress and attempt-echo idempotency.

Contract: [`03-workflows/README.md`](../03-workflows/README.md).

## Level 4 — Services

**Continuous.** Boot → ready → drain → stopped. Every service answers:
lifecycle, health (with a `critical` concept), admission (bounded), shutdown
(nothing orphaned). No sockets, timers or threads inside the file — the host
runtime owns those.

Read: [`report-worker`](../04-services/report-worker.mam.md) for backpressure
and health rollup, [`webhook-receiver`](../04-services/webhook-receiver.mam.md)
for HMAC authentication and per-producer pacing.

Contract: [`04-services/README.md`](../04-services/README.md).

## Level 5 — Systems

**Composition.** `mam.toml` for tools, `system.mam.md` for humans: member
manifest, Mermaid graph that must match the verifier's `EDGES`, refusal
codes for incomplete/invalid/upward-wired compositions.

Read: [`system.mam.md`](../05-systems/system.mam.md) — the verifier is
executable, so the diagram cannot drift.

Contract: [`05-systems/README.md`](../05-systems/README.md).

## Choosing badly (the usual mistakes)

- A workflow that *is* one function → it is a module.
- A component with no `## Memory` → it is a module with extra prose.
- A service that only handles one request → it is a workflow.
- A system root that reimplements member logic → it is a monolith in costume.
- Tests that only assert `code == ""` → they are decoration, and the review
  bar rejects them.
