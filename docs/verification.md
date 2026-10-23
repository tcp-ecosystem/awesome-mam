# Verification

Three gates. Two run anywhere with Python; the third needs the MAM CLI.

## 1. Executable harness

```bash
python scripts/harness.py
```

What it proves:

- Every `.mam.md` has a Python body that compiles and executes.
- Imports between members resolve (namespaces are registered in dependency
  order, the way real module dependencies resolve).
- Every `test_*` function in every `## Tests` block passes.

Observed on the current tree:

```text
files executed: 17
test cases: 193/193 passed, 0 failure(s)
```

The 17 = 5 modules + 3 components + 2 workflows + 2 services + 1 system +
4 templates. The 193 test cases are the ones shipped in the files — not a
separate test suite, so a broken example cannot hide behind green tests
elsewhere.

## 2. Twin integrity

```bash
python scripts/check_twins.py
```

What it proves: every `x.mam.md` has a sibling `x.mam` with **identical
bytes**. The `.mam` twin is the distribution/editor format; drift between the
two would mean two different libraries.

Observed: `twins checked: 17, failures: 0`.

## 3. Structural validation (MAM CLI)

```bash
mam validate awesome-mam        # when the CLI is on PATH
```

or, before the npm release, from a build of the main repository:

```bash
node cli/dist/index.js validate ../awesome-mam
```

What it proves: frontmatter fields, section order, table shape, closed code
blocks, capability/section agreement, and the other structural rules —
19 rules in the current validator.

Observed on the current tree:

```text
0 error(s), 0 warning(s), 40 info — 0 auto-fixable
Validated: 19 rules | 14,878 lines | 34 files
```

The 40 info lines are `GEN004` (table rows wider than 200 characters — wide
tables by design) and `SEC001` (section-order advice for the level-2
`Memory`/`Exports` additions). Info lines are non-blocking.

## 4. System placement (CI only)

The `placement` job in [`.github/workflows/validate.yml`](../.github/workflows/validate.yml)
executes the verifier from `05-systems/system.mam.md` against the checkout:

- every manifest member must exist at its declared path,
- every member's `.mam` twin must exist,
- `verify()` must return a valid composition.

This is the check that makes "a repository described as a system" literal.

## What the gates do not prove

- They do not prove the design is good — only that it is consistent.
- They do not prove the code is efficient.
- They do not prove adoption. Files authored here are the bar; independent
  users are the evidence (see the main repository's adoption docs).

## Running the same gates in CI

CI runs `harness.py`, `check_twins.py`, and the placement job on Ubuntu and
Windows for every push and pull request. If a change passes locally with
`python scripts/...` and a PR fails, the difference is almost always a
platform path issue — report it with the
[bug template](../.github/ISSUE_TEMPLATE/bug-report.md).
