---
name: Bug or gate failure
about: A reference file fails to execute, a test fails, or a gate is wrong
title: "bug: "
labels: bug
---

## What failed?

- File:
- Command (`python scripts/harness.py`, `python scripts/check_twins.py`, `mam validate`, ...):
- Expected:
- Actual (paste the output):

## Environment

- OS:
- Python version (`python --version`):
- MAM CLI version, if used (`mam --version`):

## Is the file or the test wrong?

- [ ] The module/component/workflow/service is wrong
- [ ] The test asserts the wrong behavior
- [ ] The gate (harness/twins/CI) is wrong
- [ ] Not sure

## Minimal reproduction

(Paste the smallest snippet — ideally the one `test_` function body plus the
input that triggers it.)
