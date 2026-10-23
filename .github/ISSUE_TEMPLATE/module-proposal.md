---
name: Module proposal
about: Propose a new module, component, workflow, or service before writing it
title: "proposal: "
labels: proposal
---

## What real problem does it solve?

(One paragraph. If the answer is "it demonstrates the format", it is a
template, not a member — see `templates/` instead.)

## Level

- [ ] Level 1 module — pure decision function
- [ ] Level 2 component — stateful building block
- [ ] Level 3 workflow — multi-step process
- [ ] Level 4 service — resident process

## Proposed id

`kebab-case-id` (must match the filename)

## Contract sketch

- Inputs:
- Outputs (envelope fields + every error `code`):
- Bounded work (what stops a hostile caller?):
- Tests planned (happy path + each refusal):

## Dependencies

Which existing members would this compose, and why can't it stay independent?
