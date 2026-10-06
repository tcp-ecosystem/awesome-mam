# Awesome MAM

[![MAM](https://img.shields.io/badge/language-MAM-blue)](https://github.com/tcp-ecosystem/MAM)
[![Registry](https://img.shields.io/badge/registry-live-green)](https://github.com/tcp-ecosystem/MAM/tree/main/registry)
[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/tcp-ecosystem/MAM/blob/main/LICENSE)

> Curated modules, tools, and resources for [MAM (Machine Agent Modules)](https://github.com/tcp-ecosystem/MAM) — *describe systems, compile anywhere.*

## Contents

- [Registry](#registry)
- [Founding Modules](#founding-modules)
- [Templates](#templates)
- [Editors](#editors)
- [Spec & Docs](#spec--docs)
- [Contribute](#contribute)

## Registry

- [MAM Hub](https://github.com/tcp-ecosystem/MAM/tree/main/registry) — production module registry: HTTP + GraphQL + typed client, persistent auth, integrity-verified tarballs.

## Founding Modules

Live on MAM Hub (v2.0.0 unless noted). Source: [`modules/examples/`](https://github.com/tcp-ecosystem/MAM/tree/main/modules/examples).

| Module | Type | What it does |
|--------|------|--------------|
| `example-agent` | agent | Support triage: classify, score urgency, route, stop with reason |
| `example-workflow` | workflow | Ledger ETL: extract → normalize → retry-safe load |
| `example-team` | team | Planner + researchers with handoffs |
| `example-tool` | tool | Rate-limited URL fetcher |
| `example-memory` | memory | Per-session persistent memory with TTL |
| `example-policy` | policy | Allow/deny pre-execution policy |
| `example-system` | system | Order processing: validate → charge → fulfill |
| `example-service` | service | Background service with lifecycle + health endpoint |
| `example-component` | component | Circuit breaker for flaky dependencies |
| `example-contract` | contract | List-API producer/consumer agreement |
| `example-interface` | interface | Versioned search contract, opaque cursors |
| `example-module` | module | Text statistics computation |
| `example-package` | package | Distributable unit manifest |
| `example-plugin` | plugin | Host formatter extension |
| `example-repository` | repository | Content-addressed document collection |
| `example-resource` | resource | External queue broker sync |
| `example-runtime` | runtime | Untrusted step execution engine |
| `example-documentation` | documentation | API reference as a module |
| `example-extension` | extension | Host report-format extension point |

Install any of them:

```bash
mam install example-agent
```

## Templates

Scaffold your own (`mam new <type> <name>`). Nineteen types, basic + advanced:

`agent` · `component` · `contract` · `documentation` · `extension` ·
`interface` · `memory` · `module` · `package` · `plugin` · `policy` ·
`repository` · `resource` · `runtime` · `service` · `system` · `team` ·
`tool` · `workflow`

Source: [`modules/templates/`](https://github.com/tcp-ecosystem/MAM/tree/main/modules/templates).

## Editors

| Editor | Package | Notes |
|--------|---------|-------|
| VS Code | [`arkhangellifejiggy.mam-language`](https://open-vsx.org/extension/arkhangellifejiggy/mam-language) (OpenVSX) | Syntax, snippets, diagnostics, commands |
| VSCodium / Cursor / Windsurf | same OpenVSX package | Install from Open VSX registry |
| Neovim / Vim / Sublime / Emacs / JetBrains / Zed + 8 more | [`desktop-extension/`](https://github.com/tcp-ecosystem/MAM/tree/main/desktop-extension) | 14 editors covered |

## Spec & Docs

- [Specification](https://github.com/tcp-ecosystem/MAM/blob/main/spec/SPEC.md)
- [Usage guide](https://github.com/tcp-ecosystem/MAM/blob/main/usage.md)
- [Purpose](https://github.com/tcp-ecosystem/MAM/blob/main/purpose.md) · [Goal](https://github.com/tcp-ecosystem/MAM/blob/main/goal.md) · [Scope](https://github.com/tcp-ecosystem/MAM/blob/main/scope.md) · [Brain](https://github.com/tcp-ecosystem/MAM/blob/main/brain.md)

## Contribute

Publishing a module? Open a PR adding a row to [Founding Modules](#founding-modules) (name, type, one line). Quality bar:

- Parses clean (`mam validate`)
- Ships `.mam` + `.mam.md` twins
- Has tests (`## Tests` section, executable)
- Published on MAM Hub

---

*Maintained by the MAM community. Not affiliated with GitHub Topics curation — add `mam-lang` to your repo topics to be discoverable.*
