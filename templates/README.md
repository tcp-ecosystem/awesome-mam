# Templates

Correct starting points, one per level. They are not demos: each template is
a complete, executable file with passing tests — the same gates as every
reference file in this repository (the harness runs `templates/` too).

| Template | Level | Use it when |
|----------|-------|-------------|
| [`module/`](module/README.md) | 1 | You need a pure decision function (validation, classification, policy) |
| [`component/`](component/README.md) | 2 | You need state that outlives a call (counters, buckets, caches, circuits) |
| [`workflow/`](workflow/README.md) | 3 | You need a multi-step process with retries, replay safety and compensation |
| [`service/`](service/README.md) | 4 | You need a resident process with lifecycle, health and drain |

A system (Level 5) is not templated: `05-systems/system.mam.md` is short by
design, and the [Level 5 contract](../05-systems/README.md) tells you what a
system root must carry.

## Copying a template

1. Copy **both** files next to each other:
   `<level>-<name>.mam.md` (readable source) and `<level>-<name>.mam` (its twin).
2. Rename the `id` in the frontmatter to your module id — and keep the file
   name equal to it (`check_twins.py` and `mam validate` both expect this).
3. Replace the body logic. Keep the envelope fields, the capability
   subsections and at least the test coverage the template ships.
4. Copy the twin: `Copy-Item x.mam.md x.mam` (PowerShell) or
   `cp x.mam.md x.mam` — then keep them byte-identical forever.
5. Run the gates:

```bash
python scripts/harness.py      # executes your file and its tests
python scripts/check_twins.py  # proves the .mam twin matches
```

With the MAM CLI available (from the main repository build, until the npm
release lands):

```bash
mam validate path/to/your-level   # structural validation, 19 rules
mam test path/to/x.mam.md         # the CLI's own test runner
```

## What templates deliberately do not do

- They do not import other library members — so they run anywhere, with
  nothing installed. Add a `dependencies:` entry only when your file really
  imports that member.
- They do not ship placeholder assertions. If a step has nothing to test,
  that step should not exist.
- They do not log, read files, open sockets, or keep secrets. Those are
  host concerns; the level contracts say what belongs where.
