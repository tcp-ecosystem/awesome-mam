# Service Template (Level 4)

Copy [`service-template.mam.md`](service-template.mam.md) +
[`service-template.mam`](service-template.mam) as a pair. Suggested rename:
`<your-id>.mam.md` / `<your-id>.mam`.

## Rename checklist

- [ ] `id:` matches the new file name
- [ ] **Memory** describes your real state shape (queue + config are the minimum here)
- [ ] Lifecycle transitions remain one-way: boot → ready → drain → stopped
- [ ] Health rollup keeps a `critical` concept — every service has one
- [ ] Intake remains bounded; names the refusal code
- [ ] Tests cover: boot rejection, admission, capacity refusal, duplicate,
      health rollup, one-way drain, corrupt state

## Why this shape

1. **Lifecycle is explicit.** A service that cannot say whether it is `ready`
   or `stopped` cannot be deployed safely.
2. **Health is a rollup, not a ping.** Criticality is configuration; the probe
   only reads it.
3. **Overload is refused, not buffered forever.** The queue bound and its code
   are part of the API.
4. **Drain is irreversible.** A drained state never re-opens; a restart is a
   new boot, not a lie.

Add `config-loader` to `dependencies:` when your boot should read layered
files and environment (the reference [`report-worker`](../../04-services/report-worker.mam.md)
does exactly that); the template validates configuration inline to stay
dependency-free.

## Gates

```bash
python ../../scripts/harness.py
```

Then the Level 4 contract: [`04-services/README.md`](../../04-services/README.md).
