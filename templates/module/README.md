# Module Template (Level 1)

Copy [`module-template.mam.md`](module-template.mam.md) +
[`module-template.mam`](module-template.mam) as a pair. Suggested rename:
`<your-id>.mam.md` / `<your-id>.mam`.

## Rename checklist

- [ ] `id:` matches the new file name exactly
- [ ] `name:`, `description:`, `tags:` describe your decision, not the template
- [ ] `capabilities:` still lists one capability per `### ` subsection
- [ ] `apply()` replaced by your function; envelope keys kept
      (`code` + `duration_ms` are the contract)
- [ ] Tests renamed and extended; at least one refusal per error code

## Why this shape

Level 1 modules are pure: no I/O, no state, no clock reads, stdlib only. The
template's `apply()` demonstrates the three bars every module must clear:

1. **Never raise** — malformed input is a coded envelope.
2. **Stable codes** — callers branch on `INVALID_INPUT` / `INVALID_CONFIG` /
   `TOO_MANY_VALUES`, not on prose.
3. **Bounded work** — `MAX_VALUES` stops a hostile caller from allocating an
   unbounded rejection list.

## Gates

```bash
python ../../scripts/harness.py      # from templates/module/
```

From the repository root (`awesome-mam/`), `python scripts/harness.py`
executes this file and its tests together with the rest of the library.

Accepted? Then the module is ready for the Level 1 review bar:
[`01-modules/README.md` §5](../../01-modules/README.md#5-acceptance-gate-what-mam-validate--review-enforce-before-a-module-is-listed).
