# Getting started

There are two honest paths today, because the public npm release of the MAM
CLI has not shipped yet. Pick the one that matches what you want to do.

## Path 1 — verify the library (no installs beyond Python)

Use this if you want to know whether the files really run before trusting
anyone's README.

```bash
git clone https://github.com/tcp-ecosystem/awesome-mam
cd awesome-mam
python --version        # 3.12 or newer
python scripts/harness.py
python scripts/check_twins.py
```

Expected output on the current tree:

```text
files executed: 17
test cases: 193/193 passed, 0 failure(s)
twins checked: 17, failures: 0
```

That is the whole claim in executable form: seventeen files, 193 tests, no
dependencies, no network.

## Path 2 — use the real CLI (from source)

Use this if you want `mam validate`, `mam run`, `mam test`, or compilation.

```bash
git clone https://github.com/tcp-ecosystems/MAM
cd MAM
pnpm install
pnpm build
node cli/dist/index.js validate ../awesome-mam        # 19 rules, 34 files
node cli/dist/index.js test ../awesome-mam/01-modules/schema-validator.mam.md
node cli/dist/index.js run ../awesome-mam/01-modules/schema-validator.mam.md
```

The global `npm install -g @mam/cli` path becomes valid when the public npm
release lands (tracked in the main repository's `plan-doc/adpotion.md`). This
page will not pretend it exists before then.

## Your first ten minutes

1. Run the gate (above). If tests fail, stop — that is a real finding.
2. Open `01-modules/schema-validator.mam.md` and read it top to bottom.
   Notice the envelope: `code` is the API, prose is the explanation.
3. Copy a template into a scratch folder:

   ```bash
   mkdir -p scratch/my-first-module
   cp templates/module/module-template.mam.md scratch/my-first-module/my-first-module.mam.md
   cp templates/module/module-template.mam   scratch/my-first-module/my-first-module.mam
   ```

4. Change the `id`, break the tests on purpose, watch the harness fail, then
   fix it. That loop is the entire workflow — the test failure is the tool
   telling you the contract broke.
5. Read [level-guides.md](level-guides.md) before writing anything bigger.

## Editing support

The MAM VS Code extension (Open VSX / Marketplace) highlights and validates
`.mam` and `.mam.md` files. It is optional; nothing here depends on it.

## Where things live

- Reference files: `01-modules/` … `05-systems/`
- Starting points: `templates/`
- Gates: `scripts/`
- The machine-readable system contract: `05-systems/system.mam.md` + `mam.toml`
