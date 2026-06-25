---
status: partial
phase: 85-datasheet-acquisition
source: [85-VERIFICATION.md]
started: 2026-06-25T16:00:00Z
updated: 2026-06-25T16:00:00Z
---

## Current Test

[awaiting human testing]

## Tests

### 1. PDF Content Identity Spot-Check
expected: Each opened PDF shows a title page / first page identifying the chip matching its README row; substitute/representative flags are honest. Suggested candidates: `0x08-EPROM-QUICK/W27E040.pdf` (family-substitute — confirm it is a Winbond EPROM family doc, not an unrelated PDF) and `0x29-SRAM-512K-1M/DS1245Y.pdf` (substitute for DS1250Y — confirm it is a Dallas DS1245Y NVRAM datasheet). Note: `0x08-EPROM-QUICK/W27C020.pdf` is already content-verified (pypdf extraction) and is exempt.
result: [pending]

### 2. No-Silicon Exemplar Quality Review
expected: Operator confirms the 6 no-silicon representatives (AT28C256/0x0D, DS1245Y/0x0E, Intel-28F010/0x10, 6116/0x27, DS1245Y-as-DS1250Y-sub/0x29, X88C64 data-book/0x34) are adequate algorithm references for their buckets, and the D-06 "best-documented exemplar" rationale holds.
result: [pending]

## Summary

total: 2
passed: 0
issues: 0
pending: 2
skipped: 0
blocked: 0

## Gaps
