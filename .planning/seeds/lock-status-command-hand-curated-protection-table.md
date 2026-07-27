---
title: "lock-status command backed by hand-curated protection table"
trigger_condition: "post-v1.21 milestone selection — candidate when picking the next feature milestone"
planted_date: 2026-07-10
source: /gsd-explore session (infoic.xml protection-flags investigation)
---

# Seed: `firestarter lock-status <chip>` — read chip protection state

## The idea

A new host command (+ firmware ops) that queries a chip's write-protection state
on families where it is **documented as readable**, and refuses gracefully on
families where it is not.

Reference doc: `firestarter_app/doc/lockable-proms.md` — family-level master list
of protection mechanisms, readability, and permanence for JEDEC parallel
NOR/EEPROM-flash.

## Why hand-curated (the key finding)

Investigated whether minipro's `infoic.xml` (commit `a8efaed`) could supply the
protection metadata. **Verdict: no** — see
`.planning/notes/infoic-xml-protection-flags-research.md`. The XML has only two
boolean protect bits (flags 0x4000/0x8000) that gate an opaque TL866 firmware
opcode; W29C020C (readable permanent boot-block) is flag-identical to W29EE011
(SDP-only, unreadable), and the entire AMD Autoselect readable-sector-protect
group carries zero protection bits.

So the database axis must be a **hand-curated table**, keyed at family level:

```text
protection_kind:   none | software_data_protection | sector_protection |
                   boot_block_lock | block_lock | ...
status_readable:   yes | no | partial
unlockability:     command_reversible | high_voltage_reversible |
                   irreversible | unknown
```

lockable-proms.md already IS this table in prose; the work is transcribing the
RURP-relevant subset into structured data (JSON overlay or build_db.py table).

## Scope shape (from the exploration)

Two axes, cost lives in the firmware:

1. **Database axis** — hand-curated protection table for chips in
   chip_database.json. Small: the RURP-reachable set collapses to ~3
   command-set families.
2. **Firmware axis** — per-family query sequences:
   - **AMD Autoselect** (`AA-55-90`, read sector addr → 00h/01h): Am29F,
     SST/W49F/MX29F/M29F/AT49F classes — covers most bench-validated flash.
   - **Winbond Product-ID mode boot-block status**: W29C020C/W29C040 — the
     family behind the v1.17 locked-boot-block RCA
     (`project_v117_w29c040_locked_bootblock`).
   - **SDP-only families** (AT29C, AT28C, W29EE, X28C, SST39SF): no readable
     state → the command must return "not readable on this family", never
     garbage.

## Payoffs

- `dev test` / write-path pre-flight: "this chip has a locked boot block —
  full-range verify will fail" (would have short-circuited the v1.17 W29C040
  mystery).
- Community diagnostic reports (v1.21 `dev test`) could include lock state on
  supported families.
- Distinguishes chip-state failures from transport/algorithm failures.

## Related

- Todo: `.planning/todos/pending/decode-infoic-flags-bits-14-15-protect-metadata.md`
  (independent, cheap; can land first)
- Note: `.planning/notes/infoic-xml-protection-flags-research.md`
- Memory/lesson: W29C040 permanently-locked first-16K boot block (v1.17 RCA)
