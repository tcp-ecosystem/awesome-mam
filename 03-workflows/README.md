# Level 3 — Workflows

> Orchestrated processes, **complete in this folder**: two reference workflows
> with declared failure semantics. A workflow sequences Level 1 capabilities
> and Level 2 components into a multi-step business process — what is retried,
> what is compensated, what can never happen twice.

Both reference workflows are authored here, each satisfying the complete
contract below:

- [`order-fulfillment`](order-fulfillment.mam.md) — validate → reserve → charge → notify, with release compensation and a run ledger; composes `pacing-circuit` (Level 2) + `schema-validator`
- [`dataset-publish`](dataset-publish.mam.md) — schema gate → paced upload → structured completion record; composes four Level 1 modules directly (the no-component pattern)

---

## 1. What makes it a workflow (not a component or service)

| In scope | Out of scope |
|----------|--------------|
| A finite sequence of steps with an end state | A long-running resident process (→ [Level 4](../04-services/README.md)) |
| Failure semantics per step: retry / skip / abort / compensate | Holding state across deployments (→ [Level 2 Memory](../02-components/README.md)) |
| Progress visible as structured events | Owning infrastructure (sockets, ports, workers) |
| Idempotency against re-delivery | Policy definition (→ [Level 1](../01-modules/README.md)) |

## 2. The four mandatory failure answers

A Level 3 workflow is only production-grade if, for **every** step, the module
answers all four of these — and every answer is testable:

1. **Retry?** — transient failures map into a [`retry-policy`](../01-modules/retry-policy.mam.md) category (never ad-hoc `time.sleep` loops)
2. **Compensate?** — if the step succeeded and a later step fails, what reverses it (and if the answer is "nothing", the Rules section must say so explicitly)
3. **Replay?** — what happens if the same event is delivered twice; the idempotency key and where its "already done" marker is checked
4. **Stop?** — which condition ends the workflow overall, and what "done" looks like in the output envelope

## 3. Structure: what a workflow `.mam.md` contains

Every Level 3 file starts from the complete Level 1 component set
([full-mam.md](https://github.com/tcp-ecosystems/MAM/blob/main/plan-doc/full-mam.md)) and adds:

- **Dependencies as steps**: the frontmatter `dependencies` list names the modules/components the steps call; a step that calls something unlisted is broken by definition
- **A step table** in `## Inputs` or its own section: `step → failure categories → retry policy → compensation` per row
- **The Mermaid diagram spans modules**: nodes are the modules from `01-modules/` and `02-components/` keyed by their `id`, not abstract boxes — the diagram is the compiled topology
- **Boundary validation**: events entering and leaving the workflow are checked with [`schema-validator`](../01-modules/schema-validator.mam.md); malformed events park in a dead-letter state, never crash the run
- **A run ledger**: every `run()` output includes which steps completed and their codes, so the workflow is resumable rather than all-or-nothing

## 4. Authoring checklist

- [ ] All four failure answers declared per step (§2), each backed by a test
- [ ] Error codes at step level re-use Level 1 codes (TIMEOUT, RATE_LIMITED, …) — a workflow never invents a fourth name for a third-party timeout
- [ ] Idempotency key defined and checked before the first side effect
- [ ] Compensation is defined *before* the step that needs it (read the Rules section with that in mind)
- [ ] The envelope reports `steps: [{id, status, code}]`, the terminal `status`, and `duration_ms`
- [ ] Mermaid `flowchart` covers every branch the tests exercise — no "…" ellipses, no fantasized steps
- [ ] `mam validate` → 0 errors, `mam test` → pass, twins shipped

## 5. Working with a workflow

```bash
mam validate 03-workflows/<name>.mam.md
mam graph    03-workflows/<name>.mam.md       # topology of the composed steps
mam run      03-workflows/<name>.mam.md --inputs '{"event_id": "e-881", ...}'
mam publish --targets hub,github              # workflows ship with their notes
```
