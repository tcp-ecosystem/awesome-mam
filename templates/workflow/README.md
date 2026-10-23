# Workflow Template (Level 3)

Copy [`workflow-template.mam.md`](workflow-template.mam.md) +
[`workflow-template.mam`](workflow-template.mam) as a pair. Suggested rename:
`<your-id>.mam.md` / `<your-id>.mam`.

## Rename checklist

- [ ] `id:` matches the new file name
- [ ] **Step table** lists your real steps (add rows, keep the compensation column honest)
- [ ] The four failure answers (retry / replay / compensate / stop) say something *specific* about your process
- [ ] Idempotency keys declared; the executor receives one per planned step
- [ ] `MAX_ATTEMPTS` finite; backoff values justified
- [ ] Tests cover: first plan, happy path, replay guard, transient wait,
      exhaustion, invalid event, corrupt state

## Why this shape

1. **The workflow plans; the executor performs.** No side effects live in the
   file, so the whole process is testable without mocking a network.
2. **The ledger is caller-held.** A crash loses no decision: replay the ledger.
3. **Idempotency is echoed, not assumed.** `advance(..., attempt_no=...)`
   matches the attempt embedded in the step key; a stale echo is settled, never
   re-applied.
4. **Stop is a declared answer.** Infinite retry is not a policy.

If your step needs real category-based schedules instead of the linear
template backoff, add `retry-policy` to `dependencies:` and call it — the
reference workflow [`order-fulfillment`](../../03-workflows/order-fulfillment.mam.md)
shows that composition.

## Gates

```bash
python ../../scripts/harness.py
```

Then the Level 3 contract: [`03-workflows/README.md`](../../03-workflows/README.md).
