---
schema_version: 1
open_count: 3
waived_count: 0
fixed_count: 0
total_count: 3
last_updated: 2026-09-06T12:58:56.445Z
---

# Broken Windows Ledger

> Cross-phase defect register. With `workflow.windows_enforce` enabled, `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 172 | unrun-verify | .planning/phases/172-policy-one-tracker-protected-main/172-06-PLAN.md |  | Task 3's literal <automated> verify scripts (hardcoded Integration:15368:always bypass actor, three-fresh-creates assumption, 4998759-absence assertion) were never executed as written -- D-10's reversal to amend-in-place made their literal assertions false by design. Equivalent adapted checks were run manually and recorded in evidence/172-06-ruleset-readback.txt. | open |  | 2026-09-01T21:40:44.829Z |  |
| 2 | 172 | deviation | .planning/phases/172-policy-one-tracker-protected-main/172-06-PLAN.md |  | D-10 (delete-and-recreate henols/firestarter's ruleset 4998759) REVERSED at the Task 1 checkpoint:decision gate to Option B (amend 4998759 in place via PUT, create only firestarter_app fresh) after the incumbent was measured identical to the prom canary on every non-volatile field. No DELETE was issued anywhere in this plan. | open |  | 2026-09-01T21:40:45.364Z |  |
| 3 | 178 | deviation | .planning/REQUIREMENTS.md |  | Task 2's verify script cited a stale chip_test.py:2524-2541 (already stale by the time this plan ran); repaired to the re-derived chip_test.py:2567-2574 instead | open |  | 2026-09-06T12:58:56.445Z |  |

````json
[
  {
    "id": 1,
    "kind": "unrun-verify",
    "phase": "172",
    "file": ".planning/phases/172-policy-one-tracker-protected-main/172-06-PLAN.md",
    "line": null,
    "description": "Task 3's literal <automated> verify scripts (hardcoded Integration:15368:always bypass actor, three-fresh-creates assumption, 4998759-absence assertion) were never executed as written -- D-10's reversal to amend-in-place made their literal assertions false by design. Equivalent adapted checks were run manually and recorded in evidence/172-06-ruleset-readback.txt.",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-01T21:40:44.829Z",
    "resolved_at": null
  },
  {
    "id": 2,
    "kind": "deviation",
    "phase": "172",
    "file": ".planning/phases/172-policy-one-tracker-protected-main/172-06-PLAN.md",
    "line": null,
    "description": "D-10 (delete-and-recreate henols/firestarter's ruleset 4998759) REVERSED at the Task 1 checkpoint:decision gate to Option B (amend 4998759 in place via PUT, create only firestarter_app fresh) after the incumbent was measured identical to the prom canary on every non-volatile field. No DELETE was issued anywhere in this plan.",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-01T21:40:45.364Z",
    "resolved_at": null
  },
  {
    "id": 3,
    "kind": "deviation",
    "phase": "178",
    "file": ".planning/REQUIREMENTS.md",
    "line": null,
    "description": "Task 2's verify script cited a stale chip_test.py:2524-2541 (already stale by the time this plan ran); repaired to the re-derived chip_test.py:2567-2574 instead",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-09-06T12:58:56.445Z",
    "resolved_at": null
  }
]
````
