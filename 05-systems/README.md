# Level 5 — Systems

> **A real GitHub repository can be described with MAM, organized as a
> production-grade system, and compiled into implementation targets.
> A developer outside the TCP Ecosystem independently creates a MAM module
> and uses it in a real workflow without requiring the core developer to
> build it for them.**
>
> Level 5 is where both sentences become concrete. This is the top of the
> ladder: one or more `.mam.md` files describing an entire system the way you
> would describe a repository to a new engineer — except the description
> compiles.

The reference system is authored here — [`system.mam.md`](system.mam.md) + [`mam.toml`](mam.toml),
composing all twelve members below it:

- 5 Level 1 modules · 3 Level 2 components · 2 Level 3 workflows · 2 Level 4 services
- The composition contract: manifest check, per-member gate, downward-only graph — with a verifier whose `EDGES` constant the Mermaid diagram must match
- Declared compile targets: `python`, `openai`, `langgraph`

This README is the complete usage and authoring contract the system satisfies.

---

## 1. A repository, seen from the outside

Describing a repository as a production system means the module hierarchy
mirrors what is actually deployed:

```text
my-service/                        ← the real GitHub repository
├── mam.toml                       ← system manifest: members, hub registry, targets
├── modules/                       ← Level 1: leaf capabilities used by every part
│   ├── schema-validator.mam.md
│   ├── config-loader.mam.md
│   └── …
├── components/                    ← Level 2: stateful building blocks
├── workflows/                     ← Level 3: business processes
├── services/                      ← Level 4: deployable units (one per process)
└── system.mam.md                  ← the system root: the composition contract
```

The `system.mam.md` is deliberately boring — it names members, declares the
composition order, and refuses to run if any member is absent or invalid. The
graph that a new contributor needs lives in the members, not in prose.

## 2. `system.mam.md` — the level's contract

Every reference system's root file carries:

- **Members section**: each member listed with its Level (1–4) and its `id` — the composition is explicit, not "whatever `glob` finds"
- **A system-level Workflow** in Mermaid: the arrows are *between members*, reusing their `id`s; this diagram and `mam graph` must agree
- **System Rules**: invariants that only make sense at the top (ordering between services, who owns shared state, what the system refuses to compose)
- **Catalog metadata**: `mam_version`, `license`, `tags`, and the compile targets this system claims to support

## 3. `mam.toml` — the machine composition

```toml
[system]
id = "orders-platform"
version = "1.0.0"

[targets]
compile = ["python", "openai", "langgraph"]

[registry]
hub = "https://mam-hub.onrender.com"
# members resolved from the Hub keep integrity-verified tarballs + lockfiles
```

This file exists for the tools, not for readers: `mam validate`, `mam build`
and `mam compile` consume it; humans read `system.mam.md`.

## 4. Compile targets — "compiled anywhere" made literal

```bash
mam build                          # bundle + integrity lockfiles for every member
mam compile --target python        # runnable Python implementation skeleton
mam compile --target openai        # agent-runtime scaffold for OpenAI clients
mam compile --target langgraph     # graph wiring for LangGraph hosts
mam graph system.mam.md            # the composable architecture as a picture
```

A system compiles only if its **members validate first** — that is what "a
real repository described with MAM" buys you: the description is executable
before the implementation exists.

## 5. The adoption clause this level exists for

The second sentence of this level is the bar for [Level 5 must pass the test of adoption](../README.md):

- The system describes something **already deployed** — module ids carry real work, not samples
- It compiles into a target a maintainer actually runs, **without a member of the TCP Ecosystem being involved**
- A third-party PR can add a member through the standard flow: `mam new`, the [Level 1 gate](../01-modules/README.md#5-acceptance-gate-what-mam-validate--review-enforce-before-a-module-is-listed), `mam publish`, then a one-line change in `mam.toml`

## 6. Authoring checklist

- [ ] `mam.toml` + `system.mam.md` + member folders follow the §1 layout exactly
- [ ] Every member listed in the Members section exists on disk and passes `mam validate` at its own level
- [ ] The system-level Mermaid references member `id`s only — no invented nodes
- [ ] At least two declared compile targets verified by `mam compile --target <t>`
- [ ] System Rules cover state ownership and composition order explicitly
- [ ] Twins shipped for the root file; every member at its level's twins already shipped
