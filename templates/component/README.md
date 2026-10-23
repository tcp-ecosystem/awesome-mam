# Component Template (Level 2)

Copy [`component-template.mam.md`](component-template.mam.md) +
[`component-template.mam`](component-template.mam) as a pair. Suggested
rename: `<your-id>.mam.md` / `<your-id>.mam`.

## Rename checklist

- [ ] `id:` matches the new file name
- [ ] **Memory** section updated to your state shape (the section is required)
- [ ] **Exports** table updated; every listed export exists in the Python block
- [ ] `start()` validates configuration once; no export re-reads config
- [ ] Growth bounds preserved (cap, key space, or equivalent)
- [ ] Tests cover: config rejection, happy mutation, bound refusal,
      corrupt-handle refusal

## Why this shape

A component is the first place state exists, so three disciplines come with
the template:

1. **The handle is the only state** — the caller persists it; the module keeps
   nothing between calls. That is what makes restarts honest.
2. **Refusal before mutation** — a refused `record()` leaves the handle
   untouched; there is no half-applied state.
3. **Bounded growth** — `cap` and `max_keys` are configured, not hoped for.
   Any map a caller can influence needs a bound like this.

Replace the counter; keep the handle discipline and the refusal codes.

## Gates

```bash
python ../../scripts/harness.py
```

Then the Level 2 authoring contract:
[`02-components/README.md`](../../02-components/README.md).
