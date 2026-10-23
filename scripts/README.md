# Scripts

Two self-contained gates, no dependencies beyond Python 3.12. They are what
CI runs, and they are what you run before opening a PR.

| Script | What it proves | Command |
|--------|----------------|---------|
| `harness.py` | Every `.mam.md` body executes, and every `test_*` function passes — in dependency order | `python scripts/harness.py` |
| `check_twins.py` | Every `.mam.md` has a byte-identical `.mam` twin | `python scripts/check_twins.py` |

## Why a harness instead of trusting the CLI alone

The MAM CLI (`mam validate`, `mam test`) is the authoritative tool, but this
repository must be verifiable by anyone who clones it — including CI runners
and contributors who do not have the CLI installed yet. The harness is the
same idea in ~180 lines of stdlib Python: discover the files, execute the
Python blocks, register namespaces so imports resolve like real module
dependencies, run the tests.

What it does **not** do: structural validation (frontmatter fields, section
order, table shape). That is `mam validate`'s job — 19 rules — and CI runs it
through the main repository's build where the CLI is available.

## Local workflow

```bash
# everything
python scripts/harness.py
python scripts/check_twins.py

# after adding a file: also structurally validate with the CLI
mam validate .        # when `mam` is on PATH
```

Observed on the current tree: **17 reference files, 193 test cases, 17/17
twins identical.**

## Adding a level folder

`harness.py` carries an explicit folder order (`FOLDERS`). If you add a new
numbered folder, add it there in dependency order — the script fails loudly
on unresolved imports rather than silently skipping files.
