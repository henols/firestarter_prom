---
id: info-list-type-vpp-divergence
title: Route `firestarter list` Type/VPP column through electrical.type (parity with `info`)
captured: 2026-06-10
status: completed
completed: 2026-06-10
type: enhancement
target_milestone: v1.11
priority: medium
related_phase: 60
resolves_phase: 61
---

> **RESOLVED by Phase 61 (2026-06-10).** `print_eprom_list_table` now routes the
> Type label and VPP column through the shared `resolve_type_label` helper on the
> same `electrical.type` source as `info` (D-04 single source of truth); VPP gate
> parity (`vpp_mv > 0 AND electrical-type != "SRAM"`, D-03) suppresses the spurious
> SRAM VPP. Verified 7/7 (61-VERIFICATION truth #1/#2); parametrized list-vs-info
> parity test covers the EEPROM display set + UV-EPROM control + SRAM control.


# `info` vs `list` Type/VPP label divergence (IN-01 from Phase 60 review)

## The issue

Phase 60 rerouted `firestarter info`'s Type / erasability / VPP rendering to derive from
the DB `electrical.type` ground truth. The `firestarter list` table
(`print_eprom_list_table` in `firestarter_app/firestarter/eprom_info.py:337`) was left
out of scope and still keys on the mem_type int: it calls
`get_chip_type_string(ic.get("type", 0))` (1 → "EPROM") and gates its VPP column on
`ic.get("type") == 1`.

As a result the two views now disagree for the EEPROM-family chips this milestone
targets — e.g. `firestarter info W27C512` shows `Type: EEPROM` while `firestarter list`
still shows `EPROM` for the same chip, and the two disagree on the VPP column. This is a
direct, intended consequence of the Phase 60 reframing (flagged as **IN-01**, Info
severity, in `.planning/phases/60-display-layer-decode-correctness/60-REVIEW.md`), but it
reads as a bug to users.

## Proposed fix

Route the list table's Type label and VPP column through the same `electrical.type`
source the `info` path now uses, mirroring the SRAM-suppression and EEPROM-family rules
from `build_specifications` (incl. WR-01: SRAM carries `vpp_mv=12000` as a decode artifact
and must not show VPP). Add a parametrized list-view test covering the EEPROM display set
{W27C512, SST27VF512, …}, the UV-EPROM control set, and an SRAM control so the two views
stay consistent.

## Why deferred

Out of Phase 60's stated scope (display-layer `info` correctness). Captured here so the
divergence is addressed deliberately rather than silently before the v1.11 beta cut.
