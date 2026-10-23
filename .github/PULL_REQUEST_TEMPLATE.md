# Add a module, component, workflow, service, or system member

Thanks for contributing. This repository is a reference ladder, so "works on
my machine" is not the bar — the file must be **executable, validated, and
shaped like its level**. Fill this in honestly; reviewers run the same gates.

## What are you adding?

- [ ] Level 1 module (pure decision function)
- [ ] Level 2 component (stateful building block)
- [ ] Level 3 workflow (multi-step process with failure semantics)
- [ ] Level 4 service (resident lifecycle)
- [ ] Level 5 system member wiring (edit the manifest/graph only)

## The file

- Path:
- Level contract it follows (link):
- Real problem it solves (one paragraph, no marketing):

## Gates (paste the actual output)

```text
$ python scripts/harness.py
files executed: ...
test cases: .../... passed, 0 failure(s)

$ python scripts/check_twins.py
twins checked: ..., failures: 0
```

- [ ] `.mam.md` and `.mam` twin are byte-identical
- [ ] Filename equals the frontmatter `id`
- [ ] Executable tests exist for: the happy path, **each refusal code**, and
      corrupt-input handling
- [ ] No placeholder assertions (`assert True`, `pass`, empty test bodies)
- [ ] No secrets, tokens, private URLs, or real customer data in tests
- [ ] Dependencies listed in frontmatter match the imports in the Python block
- [ ] If the file is added to the system: `MANIFEST`, `EDGES`, and the Mermaid
      diagram agree (the verifier enforces the graph; the diagram must match it)

## Level-specific checklist

**Module** — stdlib only; no I/O, state, or clock reads; stable error codes;
bounded work.

**Component** — `## Memory` describes the handle; `## Exports` matches the
code; configuration validated once at construction; growth bounds declared.

**Workflow** — step table with real compensation; retry / replay / compensate
/ stop each answered in one line; idempotency keys declared; attempt budget
finite.

**Service** — explicit lifecycle; health rollup with `critical`; bounded
intake; one-way drain; no sockets or timers in the file.

## Anything reviewers should know?

(Optional: tricky cases, follow-ups, why an unusual choice is right.)
