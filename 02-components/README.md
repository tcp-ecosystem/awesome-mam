# Level 2 — Components

> Contract definition for the second reference level. A Level 1 module is a
> capability; a Level 2 component is a *reusable building block with state and
> a public interface* — the unit a team copies into their service, configures
> once, and trusts across the codebase.

This README is the complete usage and authoring contract. The components
themselves are authored here next, composing the five Level 1 modules from
[`01-modules/`](../01-modules/README.md) — nothing below is re-implemented,
only composed.

---

## 1. What makes it a component (not a module)

A component differs from a Level 1 module in exactly three ways, and each has
a required structural consequence:

| Difference | Structural consequence in the `.mam.md` |
|------------|------------------------------------------|
| It holds **state** that outlives a call | A `## Memory` section declaring the state schema, its persistence contract, and what happens on corruption |
| It exposes a **public interface** | An `## Exports` section listing operations with the same envelope discipline Level 1 uses on `run()` |
| It is **configured**, not hardcoded | Inputs include a config object validated by [`schema-validator`](../01-modules/schema-validator.mam.md); invalid config is rejected at construction, not per call |

## 2. The reference composition story

The first wave of components is fixed — each one earns its place by composing
at least two Level 1 modules into something more than their sum:

- `http-runtime` — rate-limited, retrying, logged HTTP boundary: `rate-limiter` + `retry-policy` + `structured-logging`
- `config-factory` — env-aware config construction and hot reload: `config-loader` + `structured-logging`
- `pacing-circuit` — admission control with lockout semantics on failure storms: `rate-limiter` + `retry-policy`

Higher levels then depend on these: workflows call components; services host
components; systems wire services. The dependency arrow always points down a
level.

## 3. Authoring contract

Every component `.mam.md` must carry, on top of the full Level 1 contract
(see [the Level 1 gate](../01-modules/README.md#5-acceptance-gate-what-mam-validate--review-enforce-before-a-module-is-listed)):

- [ ] `## Memory`: state schema in schema-validator grammar + persistence contract (who saves, who loads, what a corrupt state load does)
- [ ] `## Exports`: every exported operation with its inputs/outputs envelope; undocumented operations are unexported
- [ ] State transitions are **declared** in Rules and drawn in the Workflow Mermaid (a component's diagram shows states, not just steps)
- [ ] Config at construction time; a component never re-reads environment mid-flight
- [ ] Every state-transition edge in the Mermaid diagram is covered by a test in `## Tests`
- [ ] Frontmatter `type: component`; `permissions` still minimal and concrete

## 4. Working with a component

```bash
mam validate 02-components/<name>.mam.md
mam test   02-components/<name>.mam.md
mam run    02-components/<name>.mam.md --inputs '{"op": "acquire", "config": {"capacity": 4}}'
mam graph  02-components/http-runtime.mam.md      # the state graph

# Components list what they require before installing:
mam install component-name        # → pulls its Level 1 dependencies from the Hub
mam publish --targets hub,name    # → publish with its dependency manifest intact
```

## 5. Acceptance gate

- [ ] Parses clean: `mam validate` → 0 errors
- [ ] Every `## Exports` operation has inputs/outputs tables and a test
- [ ] The Memory section answers, in one sentence each: what state exists, who persists it, what happens when it is missing/corrupt
- [ ] Composition is real: at least one Level 1 module in `dependencies` and used inside the Python — not referenced cosmetically
- [ ] Twins shipped (`.mam` + `.mam.md`), no placeholder text
