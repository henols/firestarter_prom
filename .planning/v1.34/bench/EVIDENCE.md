# v1.34 Bench Evidence — 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur

> This document is generated from `bench/EVIDENCE.jsonl` by `tools/render_evidence.py` and is never hand-edited. Run `render_evidence.py --jsonl bench/EVIDENCE.jsonl --target bench/EVIDENCE.md --check` to verify no drift.

Board identity is established by an independent avrdude-signature probe (`tools/probe_board.py`, PROCEDURE.md P-02), never by a firmware-reported field; shield revision is operator-declared from the silkscreen (PROCEDURE.md P-01), because `hw_revision` cannot distinguish this rig's Rev 2.0 / Rev 2.2 / Modified Rev 0 shields.

## Close-out counting rule

Computed over the non-bring-up rows only: (number of rows with outcome=='validated') + (number of rows with outcome=='skipped-with-reason') == position_count_expected (20). The first term is 'positions holding a result'; the second is 'positions holding a named reason for absence' (a recorded skip, never a blank). Phase 166's CLOSE-01 close-out arithmetic is this equation evaluated as a script over rows, not a human count -- a silent gap between the row count and 20 is structurally visible as a nonzero remainder rather than something a reader has to notice.

## Positions (excludes bring-up rows)

| chip | family | board | shield | blank_state | op | sha256 | verdict | anomalies | position_id | cell_id | cell_slug | arm | target_env | board_signature | controller_string | shield_rev_declared | fw_sha | fw_readback_sha_judged | fw_readback_sha_whole_flash | fw_readback_judged_span_bytes | host_arm_sha | host_arm_porcelain_clean | host_arm_file | config_dir_sha | interpreter | dep_freeze_sha | eeprom_calibration | image_mask | image_stamp_width | image_sha | read_count | read_shas | app_verdict_unjudged | sha_verdict_judged | verdict_disagreement | write_duration_wallclock_s | write_duration_app_reported_s | commands | outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Bring-up rows — rig evidence, excluded from the 20-position count

| chip | family | board | shield | blank_state | op | sha256 | verdict | anomalies | position_id | cell_id | cell_slug | arm | target_env | board_signature | controller_string | shield_rev_declared | fw_sha | fw_readback_sha_judged | fw_readback_sha_whole_flash | fw_readback_judged_span_bytes | host_arm_sha | host_arm_porcelain_clean | host_arm_file | config_dir_sha | interpreter | dep_freeze_sha | eeprom_calibration | image_mask | image_stamp_width | image_sha | read_count | read_shas | app_verdict_unjudged | sha_verdict_judged | verdict_disagreement | write_duration_wallclock_s | write_duration_app_reported_s | commands | outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Reconciliation

0 validated + 0 skipped-with-reason = 0 of 20 positions accounted for (20 not yet recorded).

