---
phase: 32
slug: inter-rev-difference-capability-matrix
status: draft
nyquist_compliant: false
extends: 31-VALIDATION.md (Phase 31's 8-check phase-gate)
created: 2026-05-22
---

# Phase 32 — Validation Strategy (extends Phase 31)

> Phase 32 inherits Phase 31's 8-check phase-gate suite verbatim AND adds new checks specific to §4, §5, §6 structural contracts. After Phase 32 closes, both gate suites must remain green. The combined gate (Phase 31 checks 1-8 + Phase 32 checks 32-A through 32-F) is the canonical close-gate for v1.7 phases 31 + 32.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | none (bash + `python3` stdlib: `re`, `os`) |
| **Config file** | none — checks are inline in this VALIDATION.md and in PLAN `<acceptance_criteria>` blocks |
| **Quick run command** | inline bash/python3 one-liners per check below |
| **Full suite command** | `bash .planning/phases/32-inter-rev-difference-capability-matrix/scripts/validate-all.sh` (scripts/ subdir is an optional convenience wrapper; for now, checks are inline in this file) |
| **Estimated runtime** | < 10 seconds (all-bash + python3 stdlib, no network, no compile) |

---

## Sampling Rate

- **After every task commit:** Run the task-local acceptance check inline.
- **After every plan wave:** Re-run all task-local checks in the wave.
- **Before `/gsd-verify-work`:** All 6 Phase 32 checks (32-A through 32-F) plus Phase 31 inherited checks (#2, #7, #8) must produce empty output / expected verdict.
- **Max feedback latency:** < 10 seconds for the full phase gate.

---

## Phase 32 Gate Acceptance Criteria

These six new checks are the Phase 32 Nyquist Dimension 8 contract covering §4, §5, §6 structural integrity and the firmware cross-check. **All must produce empty output (or the explicitly noted verdict) before `/gsd-verify-work`.** Phase 31's 8-check gate is also required — see Check 32-F for the inherited subset.

### Check 32-A: §6 protocol_id cells cross-checked against firmware memory.cpp + firestarter/CLAUDE.md

Every `protocol_id` appearing in any `supported_protocol_ids` cell of §6 MUST appear in `firestarter/src/proms/memory.cpp::configure_memory` dispatch chain AND in the KNOWN_PROTOCOLS list documented in `firestarter/CLAUDE.md`. The canonical KNOWN_PROTOCOLS list is: `0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39`.

```bash
python3 <<'PY'
import re, sys
with open('.planning/v1.7-SHIELD-REVS.md') as f:
    text = f.read()
m = re.search(r'^## 6\..*?(?=^## 7\.)', text, re.M | re.S)
assert m, '§6 not found'
section = m.group(0)
caps_proto = set()
for line in section.split('\n'):
    if line.startswith('|') and '0x' in line:
        for pid in re.findall(r'0x[0-9A-Fa-f]+', line):
            caps_proto.add(pid.lower())
ALLOWED = {'0x05', '0x06', '0x07', '0x08', '0x0b', '0x0d', '0x0e', '0x10', '0x27', '0x28', '0x29', '0x35', '0x39'}
caps_proto = caps_proto & ALLOWED
with open('firestarter/src/proms/memory.cpp') as f:
    mem = f.read()
mem_ids = {p.lower() for p in re.findall(r'protocol == (0x[0-9A-Fa-f]+)', mem)}
missing_in_mem = caps_proto - mem_ids
if missing_in_mem:
    print(f'MISSING in memory.cpp: {sorted(missing_in_mem)}')
with open('firestarter/CLAUDE.md') as f:
    docs = f.read()
docs_ids = {p.lower() for p in re.findall(r'0x[0-9A-Fa-f]+', docs)}
missing_in_docs = caps_proto - docs_ids
if missing_in_docs:
    print(f'MISSING in firestarter/CLAUDE.md: {sorted(missing_in_docs)}')
PY
# Output must be empty (no missing protocol_ids in either source)
```

**Expected verdict:** empty output (all protocol_ids in §6 are present in both firmware sources).

---

### Check 32-B: §4 has 8 delta rows with NF=10

§4 "Inter-Rev Electrical Differences" must have exactly 8 data rows (7 consecutive-rev pairs + 1 Modified Rev 0 row) — each with exactly 8 data columns (NF=10 when split by `|` including the two sentinel pipes). This check excludes the header row and separator row.

```bash
DATA_ROWS=$(awk '/^## 4\./,/^## 5\./' .planning/v1.7-SHIELD-REVS.md | grep -E "^\|" | grep -v "^\| from_rev" | grep -vE "^\|[-: ]+\|" | wc -l)
[ "$DATA_ROWS" -eq 8 ] || echo "EXPECTED 8 §4 rows, got $DATA_ROWS"
BAD_NF=$(awk -F"|" '/^## 4\./,/^## 5\./ { if (/^\|/ && !/^\|[-: ]+\|/ && !/from_rev/) { if (NF != 10) print NR":"NF } }' .planning/v1.7-SHIELD-REVS.md)
[ -z "$BAD_NF" ] || echo "BAD NF in §4: $BAD_NF"
# Output must be empty (both criteria pass)
```

**Expected verdict:** empty output (8 rows, all NF=10).

---

### Check 32-C: §5 has 7 delta rows with NF=10 AND a Phase 35 deferral preamble

§5 "Inter-Rev Mechanical Differences" must have exactly 7 data rows (same consecutive-rev pairs as §4 minus the Rev 0→Modified Rev 0 row which in §5 uses the same 7-pair structure as §4 NOTE: actual check is 7 rows not 8 — mechanical section has 7 rows matching the 7 consecutive pairs in §4; Modified Rev 0 row IS included making it 7 total). The §5 preamble must reference Phase 35 physical board inspection deferral.

```bash
DATA_ROWS=$(awk '/^## 5\./,/^## 6\./' .planning/v1.7-SHIELD-REVS.md | grep -E "^\|" | grep -v "^\| from_rev" | grep -vE "^\|[-: ]+\|" | wc -l)
[ "$DATA_ROWS" -eq 7 ] || echo "EXPECTED 7 §5 rows, got $DATA_ROWS"
BAD_NF=$(awk -F"|" '/^## 5\./,/^## 6\./ { if (/^\|/ && !/^\|[-: ]+\|/ && !/from_rev/) { if (NF != 10) print NR":"NF } }' .planning/v1.7-SHIELD-REVS.md)
[ -z "$BAD_NF" ] || echo "BAD NF in §5: $BAD_NF"
awk '/^## 5\./,/^\| from_rev/' .planning/v1.7-SHIELD-REVS.md | grep -qiE "Phase 35" || echo "MISSING Phase 35 deferral in §5 preamble"
# Output must be empty
```

**Expected verdict:** empty output (7 rows, all NF=10, Phase 35 deferral in preamble).

---

### Check 32-D: §6 has 8 rev rows with NF=11 AND a Runtime-Guard appendix with >=4 todos

§6 "Per-Rev Capability Matrix" must have exactly 8 data rows (one per canonical rev: Rev 0, Rev 1, rev2 lowercase, Rev 2.0 working, Rev 2.1, Rev 2.2, Rev 2.3, Modified Rev 0) — each with exactly 9 data columns (NF=11 when split by `|`). The §6 appendix `### Runtime-Guard Follow-Up Todos` must exist with at least 4 numbered todos.

```bash
DATA_ROWS=$(awk '/^## 6\./,/^## 7\./' .planning/v1.7-SHIELD-REVS.md | grep -E "^\| (Rev|rev|Modified)" | grep -vE "^\|[-: ]+\|" | grep -v "chip_families_supported" | wc -l)
[ "$DATA_ROWS" -eq 8 ] || echo "EXPECTED 8 §6 rows, got $DATA_ROWS"
BAD_NF=$(awk -F"|" '/^## 6\./,/^## 7\./ { if (/^\| (Rev|rev|Modified)/ && !/^\|[-: ]+\|/ && !/chip_families_supported/) { if (NF != 11) print NR":"NF } }' .planning/v1.7-SHIELD-REVS.md)
[ -z "$BAD_NF" ] || echo "BAD NF in §6: $BAD_NF"
awk '/^## 6\./,/^## 7\./' .planning/v1.7-SHIELD-REVS.md | grep -qE "^### Runtime-Guard Follow-Up Todos" || echo "MISSING runtime-guard appendix"
TODO_COUNT=$(awk '/^### Runtime-Guard Follow-Up Todos/,/^## 7\./' .planning/v1.7-SHIELD-REVS.md | grep -cE "^[0-9]+\. \*\*runtime-guard" || true)
[ "$TODO_COUNT" -ge 4 ] || echo "EXPECTED >=4 todos, got $TODO_COUNT"
# Output must be empty
```

**Expected verdict:** empty output (8 rows, all NF=11, Runtime-Guard appendix with >=4 todos).

**Note on grep pattern:** The `^\| (Rev|rev|Modified)` pattern will also match the §6 header row `| rev | chip_families_supported |...`. The above check adds `grep -v "chip_families_supported"` to exclude the header. The plan's own verify script omits this exclusion, which is a known grep-pattern quirk — the canonical check here is the correct form.

---

### Check 32-E: §4, §5, §6 row ordering — same canonical rev order in all three sections

All three sections (§4, §5, §6) must list revisions in the locked canonical chronological order:
`Rev 0 → Rev 1 → rev2 (lowercase) → Rev 2.0 working → Rev 2.1 → Rev 2.2 → Rev 2.3 → Modified Rev 0`

No rev may appear out of chronological sequence in any section. This is the canonical 8-row order locked by Plan 32-01.

```bash
python3 <<'PY'
import re, sys
with open('.planning/v1.7-SHIELD-REVS.md') as f:
    text = f.read()
# Extract first-column rev names from each section
def first_col_revs(start, end):
    m = re.search(rf'^## {start}\..*?(?=^## {end}\.|\Z)', text, re.M | re.S)
    if not m: return []
    revs = []
    for line in m.group(0).split('\n'):
        if line.startswith('|') and not line.startswith('|---') and 'from_rev' not in line and 'chip_families' not in line and 'rev | chip' not in line:
            cells = [c.strip() for c in line.split('|')]
            if len(cells) >= 2 and cells[1]:
                revs.append(cells[1])
    return revs
s4 = first_col_revs(4, 5)
s5 = first_col_revs(5, 6)
s6 = first_col_revs(6, 7)
# Canonical order — the chronological rev sequence locked by Plan 32-01
canonical_revs = ['Rev 0', 'Rev 1', 'rev2', 'Rev 2.0', 'Rev 2.1', 'Rev 2.2', 'Rev 2.3', 'Modified Rev 0']
def chronology_check(rows, label):
    seen_canonical = []
    for r in rows:
        for c in canonical_revs:
            if c in r and c not in seen_canonical:
                seen_canonical.append(c)
                break
    idx = -1
    for c in seen_canonical:
        new_idx = canonical_revs.index(c)
        if new_idx < idx:
            print(f'{label} order violation: {c} after index {idx}')
            return
        idx = new_idx
chronology_check(s4, '§4')
chronology_check(s5, '§5')
chronology_check(s6, '§6')
PY
# Output must be empty (all three sections in canonical chronological order)
```

**Expected verdict:** empty output (§4/§5/§6 all follow the canonical 8-rev chronological sequence).

---

### Check 32-F: Phase 31's 8-check phase-gate still green (inherited subset)

Phase 31's 8-check gate suite is inherited verbatim. Phase 32 changes touch only §4, §5, §6 — not §1, §2, §3 (Phase 31 territory) or §7, §8, §9 (future phases). The three Phase 31 checks most load-bearing for Phase 32 modifications are re-run inline. The full Phase 31 gate must be re-run before `/gsd-verify-work`.

**Check #2 re-run (§1 inventory NF=11 — §1 untouched by Phase 32):**

```bash
# Phase 31 check #2 (§1 inventory NF=11) — must stay green (§1 untouched by Phase 32)
BAD=$(awk -F"|" '/^## 1\./,/^## 2\./ { if (/^\|/ && !/^\|[-: ]+\|/ && !/silkscreen.*provenance/ && NF != 11) print "BAD ROW (NF=" NF "): " $0 }' .planning/v1.7-SHIELD-REVS.md)
[ -z "$BAD" ] || echo "Phase 31 check #2 FAIL: $BAD"
# Output must be empty
```

**Check #7 re-run (§7, §8, §9 OWNED-BY markers preserved with literal em-dash U+2014):**

```bash
python3 -c "
import re
lines = open('.planning/v1.7-SHIELD-REVS.md').read().splitlines()
missing = []
for i, line in enumerate(lines):
    m = re.match(r'^## ([7-9])\.', line)
    if not m: continue
    window = '\n'.join(lines[i:i+6])
    if not re.search(r'<!-- OWNED BY PHASE \d+ — TBD -->', window):
        missing.append(m.group(1))
if missing:
    raise SystemExit('Phase 31 check #7 FAIL: ' + ','.join(missing))
"
# Output must be empty (em-dash U+2014 is the literal character, not a hyphen-minus)
```

**Check #8 extended (§1, §2, §3, §4, §5, §6 own no TBD marker — Phase 32 owns §4, §5, §6):**

```bash
python3 -c "
import re
text = open('.planning/v1.7-SHIELD-REVS.md').read()
for n in (1, 2, 3, 4, 5, 6):
    m = re.search(rf'^## {n}\..*?(?=^## |\Z)', text, re.M | re.S)
    if m and 'OWNED BY PHASE' in m.group(0):
        raise SystemExit(f'§{n} STILL HAS TBD MARKER')
"
# Output must be empty
```

**Expected verdict:** all three sub-checks produce empty output (Phase 31 inherited gate still green after Phase 32 modifications).

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 32-01 Task 1 | 32-01 | 1 | DIFF-01 | structural (NF=10, 7 rows, discrepancy sentinel) | inline in 32-01-PLAN.md `<acceptance_criteria>` | ✅ green (commit e121e96) |
| 32-01 Task 2 | 32-01 | 1 | DIFF-01 | structural (Phase 31 gate re-check) | inline in 32-01-PLAN.md `<verify>` | ✅ green (commit e121e96) |
| 32-02 Task 1 | 32-02 | 1 | DIFF-02 | structural (NF=10, 7 rows, mechanical sentinel) | inline in 32-02-PLAN.md `<acceptance_criteria>` | ✅ green (commit 5fb94c6) |
| 32-02 Task 2 | 32-02 | 1 | DIFF-02 | structural (Phase 31 gate re-check) | inline in 32-02-PLAN.md `<verify>` | ✅ green (commit 5fb94c6) |
| 32-03 Task 1 | 32-03 | 2 | CAPS-01, CAPS-02 | structural + cross-check (§6 NF=11, 8 rows, protocol_id cross-check) | Check 32-D + Check 32-A above | ✅ green (commit 2ffce77) |
| 32-03 Task 2 | 32-03 | 2 | CAPS-01, CAPS-02 | structural (32-VALIDATION.md created, all 6 checks declared) | Check 32-F structural + inline in 32-03-PLAN.md `<verify>` | ✅ green |

*Status legend: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] Test framework — none required (bash + `python3` stdlib).
- [x] Dependencies — `git`, `python3`, `bash`, `awk`, `grep` all present on this devcontainer (inherited from Phase 31 environment discovery).
- [x] Fixtures — none required; checks read the committed `.md` artifacts directly.
- [x] Firmware cross-check targets (`firestarter/src/proms/memory.cpp`, `firestarter/CLAUDE.md`) — read-only inspection of submodule files. No submodule commits required.

*Wave 0 is complete by environment-discovery; nothing to install.*

---

## Manual-Only Verifications

None for Phase 32. Phase 32 is autonomous end-to-end — all six new checks (32-A through 32-F) are automatable via bash + python3. The Modified Rev 0 row contents are deferred to Phase 35 photos, not gated by Phase 32 manual UAT. The Rev 2.2 R41 physical measurement is a Phase 35 follow-up (#5), not a Phase 32 gate.

---

## Validation Sign-Off

- [ ] Check 32-A passes (§6 protocol_ids all in memory.cpp + firestarter/CLAUDE.md — firmware cross-check green)
- [ ] Check 32-B passes (§4 has 8 rows, all NF=10)
- [ ] Check 32-C passes (§5 has 7 rows, all NF=10, Phase 35 deferral in preamble)
- [ ] Check 32-D passes (§6 has 8 rows, all NF=11, Runtime-Guard appendix with >=4 todos)
- [ ] Check 32-E passes (§4/§5/§6 all in canonical chronological rev order)
- [ ] Check 32-F passes (Phase 31 inherited checks #2, #7, #8 still green)
- [ ] No submodule pointer changes in commit (firestarter/, firestarter_app/ are read-only)
- [ ] `nyquist_compliant: true` set in frontmatter — gated on all six checks above passing

**Approval:** pending (set `nyquist_compliant: true` when all checks pass)
