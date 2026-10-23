# Documentation

This folder is for humans. The executable truth lives in the numbered level
folders; everything here points at it rather than restating it.

| Document | Read it when |
|----------|--------------|
| [Getting started](getting-started.md) | You have cloned the repo and want to run something real in five minutes |
| [Level guides](level-guides.md) | You are choosing a level or writing your first file at one |
| [Verification](verification.md) | You want to know exactly what the gates prove, and how to run them |
| [Contributing](../.github/PULL_REQUEST_TEMPLATE.md) | You are opening a PR — the template is the checklist |
| [Templates](../templates/README.md) | You want a correct starting point instead of a blank page |

## The map

```text
awesome-mam/
├── 01-modules/      pure decision functions        (5 reference modules)
├── 02-components/   stateful building blocks       (3 reference components)
├── 03-workflows/    resumable processes            (2 reference workflows)
├── 04-services/     resident lifecycle processes   (2 reference services)
├── 05-systems/      one composition contract       (system.mam.md + mam.toml)
├── templates/       correct starting points        (one per level, executable)
├── scripts/         the gates CI runs              (harness + twins)
└── docs/            this folder
```

The rule that holds the whole repository together: **a file is worth what it
executes**. Prose that cannot be run is documentation; the `.mam.md` files are
the library.

## The two sentences this repository exists to prove

> A real GitHub repository can be described with MAM, organized as a
> production-grade system, and compiled into implementation targets.
>
> A developer outside the TCP Ecosystem independently creates a MAM module
> and uses it in a real workflow without requiring the core developer to
> build it for them.

The first sentence is what Levels 1–5 demonstrate. The second is what the
[contribution path](../.github/PULL_REQUEST_TEMPLATE.md) is for — we can make
the bar clear and verifiable; only independent contributors can clear it.
