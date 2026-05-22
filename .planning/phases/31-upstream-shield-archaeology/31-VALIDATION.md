---
phase: 31
slug: upstream-shield-archaeology
status: draft
nyquist_compliant: false
wave_0_complete: true
created: 2026-05-22
---

# Phase 31 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
>
> **Phase shape:** Doc-only archaeology. Nyquist Dimension 8 acceptance = structural completeness over committed `.md` artifacts and gitignored substrate. No test framework needed — checks are bash one-liners and short `python3` stdlib scripts. See `31-RESEARCH.md §Validation Architecture` for full rationale.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | none (bash + `python3` stdlib: `xml.etree`, `csv`, `re`, `os`) |
| **Config file** | none — checks are inline in PLAN `<acceptance_criteria>` blocks |
| **Quick run command** | `bash .planning/phases/31-upstream-shield-archaeology/scripts/validate-task.sh <task-id>` (planner creates per-task helpers as needed; default = inline bash one-liner per task) |
| **Full suite command** | `bash .planning/phases/31-upstream-shield-archaeology/scripts/validate-all.sh` (planner ships this — runs all 8 phase-gate checks below) |
| **Estimated runtime** | < 5 seconds (all-bash, no network, no compile) |

---

## Sampling Rate

- **After every task commit:** Run the task-local acceptance check inline (e.g. `git check-ignore` for gitignore tasks, `unzip -l` for the mine task, `ls .planning/v1.7/photos/<rev-slug>/silkscreen.jpg` for each photo task).
- **After every plan wave:** Re-run all task-local checks in the wave.
- **Before `/gsd-verify-work`:** All 8 phase-gate checks (below) must produce empty output / expected verdict.
- **Max feedback latency:** ~1 second per task check; ~5 seconds for the full phase gate.

---

## Per-Task Verification Map

> The planner fills this map task-by-task. Each plan's `<acceptance_criteria>` block supplies the concrete command. Template row:

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| _filled by planner_ | _filled_ | _filled_ | HW-INV-0X / SILK-01 | — (no security surface — desk-side docs) | structural completeness | structural | `bash -c '...'` (per `<acceptance_criteria>`) | ✅ inline in PLAN | ⬜ pending |

*Status legend: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Phase Gate Acceptance Criteria

These eight checks are the Nyquist Dimension 8 contract for Phase 31. **All must produce empty output (or the explicitly noted verdict) before `/gsd-verify-work`.**

### 1. Gitignore is functionally correct
> Per Research Finding #9: D-11's two-line pattern as written does NOT re-include `.md` files. Phase 31 ships the corrected three-line pattern.

```bash
# Each must produce the expected verdict
git check-ignore -v .planning/v1.7/notes/CHAT-INTEL.md      # → matches the .md re-include rule
git check-ignore -v .planning/v1.7/MODIFICATIONS.md         # → matches the .md re-include rule
git check-ignore -v .planning/v1.7/upstream-rurp/           # → matches the directory ignore rule
git check-ignore -v .planning/v1.7/photos/                  # → matches the directory ignore rule
# Smoke: nothing under .planning/v1.7/ except .md files appears in `git status`
git status --porcelain | grep '.planning/v1.7/' | grep -v '\.md$'   # → no output
```

### 2. Inventory rows have all 9 D-10 columns filled
```bash
awk -F'|' '
  /^## 1\. Inventory/, /^## 2\./ {
    # Markdown table rows have leading + trailing |, so NF = columns + 2 = 11 for 9 columns
    if (/^\|/ && !/^\|[-: ]+\|/ && !/silkscreen.*provenance/ && NF != 11) {
      print "BAD ROW (NF=" NF "): " $0
    }
  }
' .planning/v1.7-SHIELD-REVS.md
# Output must be empty
```

### 3. Every `state=on-hand-photographed` row has its photo dir + minimum files
```bash
python3 <<'PY'
import os
with open('.planning/v1.7-SHIELD-REVS.md') as f:
    for line in f:
        if 'on-hand-photographed' in line and line.startswith('|'):
            cells = [c.strip() for c in line.split('|')[1:-1]]
            photo_dir = cells[7]   # 8th of 9 D-10 columns
            if not os.path.isdir(photo_dir):
                print(f"MISSING DIR: {photo_dir}")
                continue
            for required in ('top.jpg', 'bottom.jpg', 'silkscreen.jpg'):
                if not os.path.exists(os.path.join(photo_dir, required)):
                    print(f"MISSING FILE: {photo_dir}/{required}")
PY
# Output must be empty
```

### 4. Every `provenance=removed-from-main` row has a non-blank `removed_commit`
```bash
python3 <<'PY'
with open('.planning/v1.7-SHIELD-REVS.md') as f:
    for line in f:
        if 'removed-from-main' in line and line.startswith('|'):
            cells = [c.strip() for c in line.split('|')[1:-1]]
            removed_commit = cells[4]   # 5th of 9 D-10 columns
            if not removed_commit or removed_commit in ('—', '-', ''):
                print(f"MISSING removed_commit: {line.strip()}")
PY
# Output must be empty
# NOTE: Rev 0 / Rev 1 may legitimately be removed-from-main with `branch-archived:origin/rev2.0`
# in the removed_commit column if no main-side deletion happened. Convention finalized by planner;
# this check only requires non-blank.
```

### 5. MODIFICATIONS.md has one upstream-schematic cross-reference per rework region
```bash
# Citation convention: "Cross-ref: <zip-path>::<schematic-file> §<area>"
N_REFS=$(grep -c '^Cross-ref:' .planning/v1.7/MODIFICATIONS.md)
N_REWORK=$(ls .planning/v1.7/photos/rev-0-modified/rework-*.jpg 2>/dev/null | wc -l)
[ "$N_REFS" -ge "$N_REWORK" ] || echo "TOO FEW CROSS-REFS: refs=$N_REFS reworks=$N_REWORK"
# Output must be empty
```

### 6. CHAT-INTEL.md has dated direct quotes for the D-12 key claims
```bash
for key in "R41 on A3" "JP1/JP3mod" "10k version resistor" "branches for the previous" "gerbers"; do
  if ! grep -E '^> .* 20[0-9]{2}-[0-9]{2}-[0-9]{2}:.*' .planning/v1.7/notes/CHAT-INTEL.md | grep -qi "$key"; then
    echo "MISSING QUOTE matching: $key"
  fi
done
# Output must be empty
```

### 7. Scaffold §4-§9 carry their `<!-- OWNED BY PHASE 3X — TBD -->` markers (D-09)
```bash
python3 <<'PY'
import re
with open('.planning/v1.7-SHIELD-REVS.md') as f:
    lines = f.read().splitlines()
for i, line in enumerate(lines):
    m = re.match(r'^## ([4-9])\.', line)
    if not m:
        continue
    window = '\n'.join(lines[i:i+6])
    if '<!-- OWNED BY PHASE' not in window:
        print(f"MISSING marker after §{m.group(1)} at line {i+1}: {line}")
PY
# Output must be empty
```

### 8. Phase 31 owns §1 + §2 + §3 content (no TBD leftover)
```bash
python3 <<'PY'
import re
with open('.planning/v1.7-SHIELD-REVS.md') as f:
    text = f.read()
for n in (1, 2, 3):
    m = re.search(rf'^## {n}\..*?(?=^## |\Z)', text, re.MULTILINE | re.DOTALL)
    if not m:
        print(f"MISSING §{n}")
        continue
    if 'OWNED BY PHASE' in m.group(0):
        print(f"§{n} STILL HAS TBD MARKER — must be filled by Phase 31")
PY
# Output must be empty
```

---

## Wave 0 Requirements

- [x] Test framework — none required (bash + `python3` stdlib).
- [x] Dependencies — `git`, `python3`, `unzip`, `awk`, `grep` all VERIFIED present on this devcontainer (Research §Environment Availability).
- [x] Fixtures — none required; checks read the committed `.md` artifacts directly.

*Wave 0 is complete by environment-discovery; nothing to install.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Silkscreen-version strings on operator boards are captured **verbatim** (per SILK-01) | SILK-01 | Reading text off a physical PCB requires human eyes + a macro photo | Operator photographs `silkscreen.jpg` per `<rev>/`; copy-pastes the exact characters (including capitalization, spacing, periods) into the inventory `silkscreen` column. Acceptance check #3 verifies the photo exists; verbatim-fidelity is operator-attested at commit time. |
| Modified Rev 0 rework cuts/jumpers identified against the upstream Rev 0 schematic | HW-INV-03 | Tracing PCB rework requires visual inspection by the operator | Operator inspects each cut/jumper on the board against the upstream Rev 0 schematic (recovered in earlier task); records each modification under a heading in `MODIFICATIONS.md` with a `Cross-ref:` line. Acceptance check #5 verifies one cross-ref per `rework-*.jpg`; correctness of the trace is operator-attested. |
| KiCad schematic visual inspection (if desired) for §3 R41 / JP4 / A3 verification | HW-INV-02, D-07 | `kicad-cli` not installed on devcontainer; visual inspection is operator's local KiCad | Operator opens the per-rev `.kicad_sch` in local KiCad if grep-extraction of R41/JP4/A3 designators leaves ambiguity. Acceptance check is grep-based; visual is optional. |

---

## Validation Sign-Off

- [ ] All tasks have an inline acceptance check (bash one-liner or python3 stdlib) in `<acceptance_criteria>`
- [ ] Sampling continuity: every task has at least one structural check; no 3 consecutive tasks lack one
- [ ] All 8 phase-gate checks pass (output empty / verdict-as-noted)
- [ ] No watch-mode flags (N/A — no test framework)
- [ ] Feedback latency < 5s phase-gate full suite
- [ ] `nyquist_compliant: true` set in frontmatter after gate passes

**Approval:** pending
