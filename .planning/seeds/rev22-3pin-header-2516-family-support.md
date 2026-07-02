---
title: "Rev 2.2/2.3 3-pin header + 2516-family jumper support"
trigger_condition: "Queued as milestone v1.24 (Jumper-Display Correctness & 2516-Family Support) — activate when that milestone is scoped"
planted_date: 2026-07-02
---

# Rev 2.2/2.3 3-pin header + 2516-family jumper support

`firestarter info` cannot represent the 3rd position of the Rev 2.2/2.3 JP4
header, and the chip database carries no signal to drive it. This seed captures
what a real fix requires — it is **not** a display-only change.

## The hardware fact (operator)

Rev 2.2 and Rev 2.3 shields have a **3-pin angled header** (not the 2-pin
Open/Closed of Rev 2.0/2.1). The 3rd position exists to support the **TI 2516
family** (TMS2516 / TMS2532).

## Why the current model can't express it

- `jp4_rev2 ∈ {Open, Closed}` is binary — no 3rd state
  ([ic_layout.py:169-184](../../firestarter_app/firestarter/ic_layout.py#L169-L184)).
- The 2516 family is **indistinguishable** from ordinary 24-pin EPROMs by every
  existing chip-database field: `pin_count` (all 24), `vpp` (all 25V, shared with
  M2716/ETC2716), `pinout` (2516 collides with 2716 on `DIP24_2716`), `algorithm`
  (all `0x0B`).

## What a fix needs (blockers)

1. **New per-chip DB field** flagging TI-25xx parts — the datasheet-confirmed
   distinguisher is that the program strobe lands on **pin 20 (PD/PGM)** on the
   TI parts vs **pin 18** on Intel parts. Something like a `pgm-on-pin-20` flag or
   a distinct pinout key. Requires `build_db.py` support since it can't be derived
   from `infoic.xml` fields already parsed.
3. **Firmware verification** — confirm what pin firmware algorithm `0x0B`
   actually strobes, and whether the 3-position jumper physically reroutes that
   strobe to pin 20. The jumper is only half the routing; firmware must target the
   right pin (see research questions 2026-07-02).
4. **3-state jumper model** in `ic_layout.py` + display, replacing the binary JP4.
5. **Bench validation** on a real Rev 2.2/2.3 board with an actual 2516/2532
   (operator owns Rev 2.2).

## Related

- Note: `notes/info-jumper-display-design-audit.md`
- Todo (the safe subset, do first): `todos/pending/fix-jp4-labels-and-rev2-revision-block.md`
- Research questions appended to `research/questions.md` (2026-07-02)
