# v1.34 Chip Sweep Evidence — 162-chip-11-part-dev-test-sweep-on-the-reference-rig

> This document is generated from `bench/CHIP-EVIDENCE.jsonl` by `tools/render_chip_evidence.py` and is never hand-edited. Run `render_chip_evidence.py --jsonl bench/CHIP-EVIDENCE.jsonl --target bench/CHIP-EVIDENCE.md --check` to verify no drift.

Each row is produced by `firestarter dev test <chip>` on Leonardo + Rev 2.0, v1.33 firmware, and copied out of the frozen config dir by `tools/append_chip_evidence.py` -- never hand-entered.

## Close-out counting rule

Computed over rows with arm=='v133' ONLY (arm=='control' rows are excluded per control_rerun_exclusion): (number of such rows with outcome=='validated') + (number of such rows with outcome=='skipped-with-reason') == position_count_expected (11), where 11 is the v1.15 physical inventory -- ten parts actually run (write scope for each defined by DERIVE-PLAN.json) plus the 2516's own named-absence row (named_absence_convention). The first term is 'positions holding a produced report artifact'; the second is 'positions holding a named reason for absence' (the 2516 row, or any other recorded skip -- never a blank). This equation is evaluated as a script over rows by Phase 166's CLOSE-01, never as a human count -- a silent gap between the row count and 11 is structurally visible as a nonzero remainder rather than something a reader has to notice.

## Positions (arm == 'v133')

| chip | family | board | shield | blank_state | op | sha256 | verdict | anomalies | position_id | cell_id | cell_slug | arm | target_env | board_signature | controller_string | shield_rev_declared | fw_sha | fw_readback_sha_judged | fw_readback_sha_whole_flash | fw_readback_judged_span_bytes | host_arm_sha | host_arm_porcelain_clean | host_arm_file | config_dir_sha | interpreter | dep_freeze_sha | eeprom_calibration | report_schema_version | host_version | fw_board_identity | hw_revision | protocol | chip_id | step_verdicts | step_run_counts | step_durations_s | step_error_codes | step_fingerprints | read_divergence | write_target | write_coverage | banner | sdp_hold_state | db_diff | transport_health | dedup_fingerprint | repeat_policy | exit_code | report_json_path | report_json_sha256 | report_md_path | report_md_sha256 | vpp_target_mv | vpp_real_mv | vpp_firmware_mv | vpp_shortfall_mv | prior_disposition | prior_disposition_source | prior_dispositions_all | divergence_verdict | known_carried | control_rerun_for | jp4_position | uv_slot | reseat_count | commands | dedup_query_outcome | read_consistency_followup | named_absence | outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Excluded rows — divergence-arbitration control re-runs

A row whose arm is 'control' is a divergence-arbitration re-run under D-17, not a sweep position -- it is excluded from the 11-position reconciliation (close01_counting_rule) and reconciled separately (chip_sc04_rule). This is the structural analogue of EVIDENCE.jsonl's BRINGUP- prefix exclusion, but keyed on `arm` rather than on a cell_id prefix: the chip sweep runs one cell (CHIP) for its whole run, so position_id's own __v133__/__control__ segment already keeps a control re-run's id distinct from the primary position it arbitrates, and a second exclusion mechanism keyed on a prefix would be redundant with the one this file already carries.

| chip | family | board | shield | blank_state | op | sha256 | verdict | anomalies | position_id | cell_id | cell_slug | arm | target_env | board_signature | controller_string | shield_rev_declared | fw_sha | fw_readback_sha_judged | fw_readback_sha_whole_flash | fw_readback_judged_span_bytes | host_arm_sha | host_arm_porcelain_clean | host_arm_file | config_dir_sha | interpreter | dep_freeze_sha | eeprom_calibration | report_schema_version | host_version | fw_board_identity | hw_revision | protocol | chip_id | step_verdicts | step_run_counts | step_durations_s | step_error_codes | step_fingerprints | read_divergence | write_target | write_coverage | banner | sdp_hold_state | db_diff | transport_health | dedup_fingerprint | repeat_policy | exit_code | report_json_path | report_json_sha256 | report_md_path | report_md_sha256 | vpp_target_mv | vpp_real_mv | vpp_firmware_mv | vpp_shortfall_mv | prior_disposition | prior_disposition_source | prior_dispositions_all | divergence_verdict | known_carried | control_rerun_for | jp4_position | uv_slot | reseat_count | commands | dedup_query_outcome | read_consistency_followup | named_absence | outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Divergence table

| chip | prior_disposition_source | prior_disposition | step_verdicts | divergence_verdict | known_carried |
| --- | --- | --- | --- | --- | --- |

## Reconciliation

0 validated + 0 skipped-with-reason = 0 of 11 positions accounted for (11 not yet recorded).

SC#4: count(control)=0 == count(v133 rows whose divergence_verdict starts 'diverges')=0: holds. Every control row's control_rerun_for names an existing diverging v133 row: yes. No two control rows share the same control_rerun_for: yes. Total runs this cell records: 10 + N = 10 + 0 = 10 (the roadmap's reading is 11 + N = 11 + 0 = 11; this file deliberately uses 10, not 11, as the run-count base, because the 2516 is a named absence -- never seated, never run -- and contributes 0 to this term).

