---
title: KNOWN-STALE CITATIONS — milestone v1.33
phase_planted: 154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo
planted: 2026-08-23
closed_by: Phase 159 / REMAP-04
close_blocking: true
requirements: [SWEEP-12]
---

# `.planning/` citations into the swept source are KNOWINGLY STALE

> **This file is a marker, not a note.** Its removal is **close-blocking**: milestone v1.33
> cannot close while it exists. **Phase 159 / REMAP-04** removes it.

---

## 1. What is stale

As of Phase 154, **`.planning/` citations that target any file named in §2 below are stale**
— their `file:LINE` numbers no longer point at the text they quote.

**This is a deliberate decision (D-01), not an oversight.** Phase 154 stripped GSD planning
provenance out of both sub-repos' comments; Phases 155-158 then reduce firmware size, which
shifts the same lines again. D-10 records the measurement behind deferring the repair:
composing four successive mappings would create a **range-shrinking hazard** that one
composite mapping avoids, and **723** citations would otherwise be remapped **twice**, with
**41%** of that rework caused by four added `#include` lines alone. So the repair is done
**once**, at Phase 159, over the composite pre-154 → post-158 diff.

The window is safe because it is **structural, not a promise**: this file is the interface
to REMAP-04's close block (§4).

---

## 2. Which files

**143 swept source files.** The 6 further modified paths that are NOT sweep edits are listed after the table.

- `firestarter/include/boards/py32f071_pinmap_guard.h`
- `firestarter/include/boards/py32f071_rurp_shield.h`
- `firestarter/include/eprom.h`
- `firestarter/include/eprom_budget.h`
- `firestarter/include/firestarter.h`
- `firestarter/include/flash_5v_page.h`
- `firestarter/include/flash_nor_unlock.h`
- `firestarter/include/flash_utils.h`
- `firestarter/include/logging_id.h`
- `firestarter/include/rurp_config_storage.h`
- `firestarter/include/rurp_pinmap_guard.h`
- `firestarter/include/rurp_pinout.h`
- `firestarter/include/rurp_serial_utils.h`
- `firestarter/include/rurp_shield.h`
- `firestarter/include/rurp_vpp.h`
- `firestarter/src/boards/leonardo_rurp_shield.cpp`
- `firestarter/src/boards/rurp_serial_utils.cpp`
- `firestarter/src/boards/uno_rurp_shield.cpp`
- `firestarter/src/dev_tools.cpp`
- `firestarter/src/eprom_operations.cpp`
- `firestarter/src/firestarter.cpp`
- `firestarter/src/hardware_operations.cpp`
- `firestarter/src/json_parser.c`
- `firestarter/src/operation_utils.cpp`
- `firestarter/src/proms/eeprom_28c.cpp`
- `firestarter/src/proms/eprom_budget.cpp`
- `firestarter/src/proms/eprom_params.cpp`
- `firestarter/src/proms/flash_5v_page.cpp`
- `firestarter/src/proms/flash_nor_unlock.cpp`
- `firestarter/src/proms/flash_utils.cpp`
- `firestarter/src/proms/memory.cpp`
- `firestarter/src/rurp_vpp.cpp`
- `firestarter/test/native/avr/_shared/eprom_v131_expected_prechange.h`
- `firestarter/test/native/avr/test_cmd_admission/avr/pgmspace.h`
- `firestarter/test/native/avr/test_cmd_admission/host_stubs.cpp`
- `firestarter/test/native/avr/test_cmd_admission/test_cmd_admission.cpp`
- `firestarter/test/native/avr/test_cobs_cmd_frame/host_stubs.cpp`
- `firestarter/test/native/avr/test_cobs_cmd_frame/serial_read_mock.h`
- `firestarter/test/native/avr/test_cobs_cmd_frame/test_cobs_cmd_frame.cpp`
- `firestarter/test/native/avr/test_cobs_data_frame/host_stubs.cpp`
- `firestarter/test/native/avr/test_cobs_data_frame/test_cobs_data_frame.cpp`
- `firestarter/test/native/avr/test_data_input/avr/pgmspace.h`
- `firestarter/test/native/avr/test_data_input/host_stubs.cpp`
- `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp`
- `firestarter/test/native/avr/test_dispatch/avr/pgmspace.h`
- `firestarter/test/native/avr/test_dispatch/host_stubs.cpp`
- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp`
- `firestarter/test/native/avr/test_eeprom28c_sdp/host_stubs.cpp`
- `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp`
- `firestarter/test/native/avr/test_eprom_params_v131/host_stubs.cpp`
- `firestarter/test/native/avr/test_eprom_params_v131/test_eprom_params_v131.cpp`
- `firestarter/test/native/avr/test_flash_intel_vpp/avr/pgmspace.h`
- `firestarter/test/native/avr/test_flash_intel_vpp/host_stubs.cpp`
- `firestarter/test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp`
- `firestarter/test/native/avr/test_frame_vectors/host_stubs.cpp`
- `firestarter/test/native/avr/test_frame_vectors/serial_read_mock.h`
- `firestarter/test/native/avr/test_frame_vectors/test_frame_vectors.cpp`
- `firestarter/test/native/avr/test_loop_eprom_v131/host_stubs.cpp`
- `firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp`
- `firestarter/test/native/avr/test_messages/avr/pgmspace.h`
- `firestarter/test/native/avr/test_messages/host_stubs.cpp`
- `firestarter/test/native/avr/test_messages/serial_read_mock.h`
- `firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp`
- `firestarter/test/native/avr/test_not_implemented/avr/pgmspace.h`
- `firestarter/test/native/avr/test_not_implemented/host_stubs.cpp`
- `firestarter/test/native/avr/test_not_implemented/test_not_implemented.cpp`
- `firestarter/test/native/avr/test_pinmap_provisional/avr/pgmspace.h`
- `firestarter/test/native/avr/test_pinmap_provisional/host_stubs.cpp`
- `firestarter/test/native/avr/test_pinmap_provisional/test_pinmap_provisional.cpp`
- `firestarter/test/native/avr/test_read_timing/avr/pgmspace.h`
- `firestarter/test/native/avr/test_read_timing/host_stubs.cpp`
- `firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp`
- `firestarter/test/native/avr/test_sdp_harness/host_stubs.cpp`
- `firestarter/test/native/avr/test_sdp_harness/test_sdp_harness.cpp`
- `firestarter/test/native/avr/test_trace_eprom_v131/host_stubs.cpp`
- `firestarter/test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp`
- `firestarter/test/native/avr/test_val_5v_page/host_stubs.cpp`
- `firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp`
- `firestarter/test/native/avr/test_val_eeprom28c/host_stubs.cpp`
- `firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp`
- `firestarter/test/native/avr/test_val_eprom/host_stubs.cpp`
- `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp`
- `firestarter/test/native/avr/test_val_flash_intel/host_stubs.cpp`
- `firestarter/test/native/avr/test_val_flash_intel/test_val_flash_intel.cpp`
- `firestarter/test/native/avr/test_val_nor_unlock/host_stubs.cpp`
- `firestarter/test/native/avr/test_val_nor_unlock/test_val_nor_unlock.cpp`
- `firestarter/test/native/avr/test_val_sram/host_stubs.cpp`
- `firestarter/test/native/avr/test_val_sram/test_val_sram.cpp`
- `firestarter/test/native/avr/test_vpp_eprom_v131/host_stubs.cpp`
- `firestarter/test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp`
- `firestarter_app/firestarter/chip_test.py`
- `firestarter_app/firestarter/cli_handlers.py`
- `firestarter_app/firestarter/codec.py`
- `firestarter_app/firestarter/constants.py`
- `firestarter_app/firestarter/database.py`
- `firestarter_app/firestarter/diagnostic_report.py`
- `firestarter_app/firestarter/eprom_info.py`
- `firestarter_app/firestarter/eprom_operations.py`
- `firestarter_app/firestarter/firmware.py`
- `firestarter_app/firestarter/frame_parser.py`
- `firestarter_app/firestarter/ic_layout.py`
- `firestarter_app/firestarter/lock_status.py`
- `firestarter_app/firestarter/logging_utils.py`
- `firestarter_app/firestarter/main.py`
- `firestarter_app/firestarter/protection_readability.py`
- `firestarter_app/firestarter/py32_dfu.py`
- `firestarter_app/firestarter/sdp_capability.py`
- `firestarter_app/firestarter/sdp_honesty.py`
- `firestarter_app/firestarter/serial_comm.py`
- `firestarter_app/firestarter/submit.py`
- `firestarter_app/tests/conftest.py`
- `firestarter_app/tests/fixtures/planted_json_parser_key_string_drift.c`
- `firestarter_app/tests/fixtures/planted_json_parser_undispatched_key.c`
- `firestarter_app/tests/fixtures/planted_log_in_window.cpp`
- `firestarter_app/tests/test_characterization.py`
- `firestarter_app/tests/test_chip_resolver.py`
- `firestarter_app/tests/test_chip_test.py`
- `firestarter_app/tests/test_chip_test_sdp_leg.py`
- `firestarter_app/tests/test_cli_handlers.py`
- `firestarter_app/tests/test_consistency_check.py`
- `firestarter_app/tests/test_database_conversion.py`
- `firestarter_app/tests/test_decoder.py`
- `firestarter_app/tests/test_eprom_operations.py`
- `firestarter_app/tests/test_firmware_install.py`
- `firestarter_app/tests/test_frame_vectors.py`
- `firestarter_app/tests/test_ic_layout.py`
- `firestarter_app/tests/test_pulse_us_override.py`
- `firestarter_app/tests/test_py32_packaging.py`
- `firestarter_app/tests/test_revision_constants_parity.py`
- `firestarter_app/tests/test_sdp_honesty.py`
- `firestarter_app/tests/test_serial_comm.py`
- `firestarter_app/tests/test_submit.py`
- `firestarter_app/tests/test_val_wire_5v_page.py`
- `firestarter_app/tests/test_wire_dict_equivalence.py`
- `firestarter_app/tests/test_write_skip_erase_0x0d.py`
- `firestarter_app/tools/audit_coverage_matrix.py`
- `firestarter_app/tools/build_db.py`
- `firestarter_app/tools/check_devtest_orchestrator.py`
- `firestarter_app/tools/check_dispatch.py`
- `firestarter_app/tools/check_is_memory_cmd_no_ifdef.py`
- `firestarter_app/tools/diff_db.py`
- `firestarter_app/tools/gen_sdp_bus_config.py`
- `firestarter_app/tools/parse_devtest_issue.py`

**Modified, but NOT a sweep edit — listed so the set above is exact:**

- `firestarter/tests/golden/eprom_params_citations.json`
- `firestarter/tests/golden/protocol_branch_inventory.json`
- `firestarter/tests/test_config_schema_pinned.py`
- `firestarter_app/tests/test_dispatch_mirror.py`
- `firestarter_app/tests/test_parse_gate_admission.py`
- `firestarter_app/tests/test_sdp_table_parity.py`

Total modified paths: 149 = 143 swept + 6 not-a-sweep.

### The candidate set is wider than the swept set, deliberately

| Set | Size |
|---|---|
| **Candidate** files (every file under the sweep globs carrying ≥1 provenance hit) | **171** as recorded in the manifest header (169 measured at the pre-sweep shas, +2 being two of plan 03's new planted fixtures) |
| Candidate files **actually swept** | **144** |
| Candidate files left **untouched** | **27** |

The difference is intentional and every one of the 27 is attributed by name in
`.planning/v1.33/sweep-outcome-record.md` §2 — four Ruling B blob-sha exemptions, three
D-02 `CAP-0N` vocabulary exemptions, two plan-03 fixtures untouched by mandate, two named
survey false positives, three named narrow-treatment abstentions, and thirteen files whose
every hit is an ID-first line that D-03 **retains**.

Citations into those 27 files are **not** stale. Citations into the 143 above are.

---

## 3. How many citations

| Quantity | Value | Where recorded |
|---|---|---|
| Manifest rows (citations recorded) | **13,692** | `.planning/v1.33/sweep-citation-manifest.jsonl` |
| Citation **occurrences** | 13,290 | manifest header `_schema.counts` |
| Rows targeting a candidate swept file | 10,445 (10,169 comparable form) | `sweep-citation-manifest-report.md` |
| Rows targeting a file in the **actual** swept set | **9,343** | `sweep-outcome-record.md` §5 |
| **Shifting subset** (predicted to move) | **7,249** (7,076 comparable form) | `sweep-citation-manifest-report.md` |
| Rows flagged **`retarget: true`** | **815** | `sweep-outcome-record.md` §5 |
| Rows whose endpoint was already unreadable pre-sweep | 267 | `sweep-outcome-record.md` §5 |
| Distinct planning documents carrying a citation | 1,228 | plan 05's real-corpus dry run |

- The **record** is `.planning/v1.33/sweep-citation-manifest.jsonl` — 13,692 JSONL rows,
  generated at the pre-sweep shas `8695ee52…` / `6bfa6453…` and **not reconstructible after
  the sweep**.
- The **reconciliation** — every measured figure printed beside every recorded one, with
  each delta explained or explicitly marked part-unexplained — is
  `.planning/v1.33/sweep-citation-manifest-report.md` (Ruling G).

---

## 4. Who closes it, and that the close is BLOCKING

**Phase 159 / REMAP-04** closes this window. Removing this file is **REMAP-04's own
deliverable**, and that removal is **close-blocking**: **milestone v1.33 cannot close while
this file exists.**

Phase 159 applies `remap_citations.py` exactly **once**, over the composite
pre-154 → post-158 diff, then removes this marker.

**Why the window is safe rather than merely tolerated** (D-10):

- Composing four successive mappings (154, then each of 155-158) would create a
  **range-shrinking hazard** that a single composite mapping avoids — a range spanning a
  deleted block must *shrink*, not translate by a constant offset, and shrink does not
  compose cleanly across four hops.
- **723** citations would be remapped **twice** under the alternative, and **41%** of that
  rework is caused by **four added `#include` lines**.
- The roadmap's sweep-last fallback was **DECLINED** for exactly these measurements, and
  this marker is what makes the resulting staleness a **structural guarantee** instead of a
  promise.

---

## 5. What the closer needs

| Asset | Path | Note |
|---|---|---|
| The manifest | `.planning/v1.33/sweep-citation-manifest.jsonl` | 13,692 rows; both endpoints **and** both source texts on every range record |
| The remap tool | `.planning/v1.33/tools/remap_citations.py` | Built and proven in Phase 154; **not applied** there. Dry-run by default — `--apply` is required |
| Its unit tests | `.planning/v1.33/tools/test_remap_citations.py` | 21 legs, including two **anti-vacuity** legs that run the wrong implementation and assert it fails |
| The shared resolver | `.planning/v1.33/tools/citation_paths.py` | One resolver for the generator **and** the remapper, so a citation cannot resolve two ways |
| The corpus survey | `.planning/v1.33/tools/survey_provenance.py` | The hit oracle; note its per-file key is **`file_hits`**, while `files` is an integer **count** |
| The post-sweep record | `.planning/v1.33/sweep-outcome-record.md` | Byte-identity after-pair, the actual swept set, the residual attribution, the 815-row retarget subset |

### Three hard requirements on the closer

1. **Skip the 815 `retarget: true` rows BY NAME.** Their cited comment line did not survive
   verbatim — 786 reflowed (`replace`), 29 deleted (`delete`). Their `source_text` is
   preserved **unchanged** and each carries a hand-chosen `retarget_new_line`,
   `retarget_new_text` and a one-line `retarget_reason`. **Round-tripping them would
   manufacture false green**, which is precisely why they are flagged rather than
   renumbered. Also skip the 267 rows whose endpoint `text_status` is not `read`.
2. **`target_line` on every row — including all 815 retarget rows — is still the PRE-154
   anchor.** It was deliberately **not** advanced: Phase 159's old side is pre-154, and a
   row advanced to its post-154 value while its 12,877 siblings stayed pre-154 would be
   silently mis-mapped. The hand-chosen post-154 target lives in `retarget_new_line`.
3. **Pass the composite shas on argv, not from the manifest header.**
   `--pre-sweep-sha firestarter=<composite-old> --pre-sweep-sha firestarter_app=<the plan-12 app commit>`.
   The header's `pre_sweep_shas` records generation-time HEADs, and the app side's
   `source_text` was read from a working tree that already carried plan 03's edits (deferred
   item **D3**). Argv beats the header by design.

Two further known snags, both recorded rather than left to be rediscovered:

- **`.planning/STATE.md`'s 15 bindings no longer bind** — every plan's `state_updates` step
  rewrites that file. The tool **refuses** and names each one. Regenerate the manifest
  immediately before the remap, or exclude `STATE.md` from the corpus (deferred item **D4**).
- **A violation aborts the whole run.** Every document is planned before any byte is
  written, so an oracle mismatch anywhere means nothing is written anywhere — and a
  partially-applied run resumes correctly, because already-correct records are recognised as
  fixed points.

---

## 6. The known hazard being handed forward

**Phase 154 edited NOTHING under `.planning/milestones/`.** Verified, not asserted:
`git diff --name-only -- .planning/milestones` is empty against both the working tree and
the meta repo's pre-sweep sha. So
`reference_milestone_close_breaks_record_gates` — archived sections orphaning `lines=N`
counters — **cannot** have been tripped by this phase.

**But Phase 159 rewrites 1,302 citations that live under `.planning/milestones/`.** That is
where the archived-record gate hazard becomes real, and it belongs to **REMAP-01**, not to
Phase 154. Research §R6 established both halves of this.

---

*Planted by Phase 154 plan 12 (SWEEP-12). Removed by Phase 159 / REMAP-04, whose removal is
close-blocking for milestone v1.33.*
