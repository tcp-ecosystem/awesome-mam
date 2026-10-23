# Level 4 — Services

> Contract definition for the fourth reference level. A service is the first
> level that *exists continuously*: it boots, it responds to the world while
> running, and it shuts down without orphaning work. Modules are capabilities;
> workflows are processes; a service is the deployable skin around both.

The services themselves are authored here next, hosted on the Level 1–3
primitives. This README is their complete usage and authoring contract.

---

## 1. What makes it a service (not a workflow)

| In scope | Out of scope |
|----------|--------------|
| A lifecycle: `init → ready → degraded → draining → stopped` | Branching business logic (→ [Level 3](../03-workflows/README.md)) |
| A health contract an external observer can poll | Holding a library's algorithms (→ [Level 1](../01-modules/README.md)) |
| Config resolved once at boot, from all three layers | Config *syntax rules* (→ [`config-loader`](../01-modules/config-loader.mam.md)) |
| Structured telemetry with correlation, end to end | Redaction policy definition (→ [`structured-logging`](../01-modules/structured-logging.mam.md)) |

## 2. The five mandatory sections of a service

On top of the full Level 1 component set:

1. **`## Lifecycle`** — the state table: what triggers each transition, what each state means for callers, and which transitions are forbidden (`ready → init` must be impossible)
2. **`## Health`** — the check report: what is probed, what `healthy`/`degraded`/`unhealthy` mean in measurable terms, and that health never lies (`degraded` when a dependency is down, never `healthy` with a swallowed error)
3. **Boot order** — an explicit list: config → module wiring → state load → advertise ready. Any step that fails short-circuits to `stopped` with the failing code in the shutdown envelope
4. **Shutdown contract** — in-flight work: what finishes, what is parked, and the deadline after which `draining` stops accepting
5. **Telemetry** — every lifecycle transition and every request outcome is emitted via [`structured-logging`](../01-modules/structured-logging.mam.md) with a correlation id; a service without event provenance is a black box and fails review

## 3. Config and permissions at service level

- Configuration enters **once**, through [`config-loader`](../01-modules/config-loader.mam.md), at `init`; the validated config object is immutable for the process lifetime. A service that re-reads `os.environ` mid-flight is a defect
- `permissions` in the frontmatter must enumerate the system surfaces this service actually touches (`filesystem: read/write`, `network: outbound`, `environment: read`) — the sandbox/permissions story from [full-mam.md §10](https://github.com/tcp-ecosystems/MAM/blob/main/plan-doc/full-mam.md) becomes real here
- Where a service calls a network dependency, Level 3 failure semantics apply: the workflow/module boundary handles retry, the service handles *whether embarrassing retries are even visible in logs*

## 4. Authoring checklist

- [ ] Every lifecycle transition is drawn in Mermaid and asserted by a test — including the forbidden ones
- [ ] Health envelope: `{state, uptime_ms, dependencies: [{id, state, latency_ms}]}`
- [ ] Shutdown envelope: `{state: "stopped", drained: true|partially, parked: N, timeout: <deadline>}`
- [ ] Config comes from `config-loader`; invalid boot config → `stopped` before any side effect, not a half-booted process
- [ ] Every log line carries `correlation_id`; every emitted event name is dotted and declared
- [ ] `mam validate`/`mam test` clean; twins shipped; no placeholder text

## 5. Operating a service

```bash
mam validate 04-services/<name>.mam.md
mam run      04-services/<name>.mam.md --inputs '{"mode": "boot", "env": {"CFG_POOL__SIZE": "8"}}'
mam run      04-services/<name>.mam.md --inputs '{"mode": "probe"}'      # health check
mam run      04-services/<name>.mam.md --inputs '{"mode": "drain"}'      # graceful stop
mam publish  --targets hub                                              # ship to the Hub
```

Services are the first level whose reference deployment is a real host: the
compiled target (`mam compile --target openai|python|langgraph|…`) turns the
description into the implementation skeleton — that compilation gap is what
Level 5 is about.
