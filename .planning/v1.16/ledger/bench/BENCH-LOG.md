# Phase 90 — Bench Validation Log (LEDGER-02)

Per-protocol bench regression of the recomposed firmware against the v1.15 byte-exact
baseline. Every live silicon op is operator-gated (D-05). PASS = read-SHA (N≥3) **and**
write-cycle A→B final SHA both byte-identical to the v1.15 baseline (D-01). Any mismatch
is recorded FAIL-INVESTIGATE, never auto-passed (D-03). Gitlinks stay PINNED at b10 (D-06).

---

## Session Header

| Field | Value |
|-------|-------|
| Date | 2026-06-26 |
| Firmware-under-test (identity) | `firestarter` submodule HEAD **a296195** (Phase-89 recompose) |
| Version string (caveat) | `3.0.0b10` — NOT bumped at Phase 84; the version string does **not** distinguish the recompose from stock b10. The submodule commit `a296195` is the firmware-under-test identity (D / version_string_caveat). |
| Controller | **leonardo** on `/dev/ttyACM0` (`firestarter fw` confirmed pre- and post-flash) |
| Shield (oracle) | **Rev 2.0** — operator-confirmed silkscreen (the EEPROM HW byte reads "Rev 2.0-class" but cannot reliably distinguish Rev 2.0/2.2/Rev0; silkscreen is the mandatory oracle, D-09). |
| Build result | `pio run -e leonardo` → **Flash 87.7% (25136 B / 28672 B)**, RAM 78.1% (1999 B). Matches the expected recompose figure (RESEARCH §184). |
| Flash result | `pio run -t upload -e leonardo` → 25136 bytes written + **verified** (avrdude), SUCCESS. Operator-authorized; Leonardo EXEMPT from chip-out-before-sideload (D-06). |

### Image-SHA Sanity (BEFORE any silicon op)

`gen_test_image.py <size> <seed> <out>` — seed 1 = image A, seed 2 = image B. All 4 chips'
generated A/B SHAs are byte-identical to the v1.15 baseline (RESEARCH lines 123-128) — the
deterministic generator is byte-stable on this host. Any mismatch here would be a
generator/host problem; all matched, so we proceed to silicon.

| Chip | size (B) | img_A SHA (seed 1) | matches v1.15 | img_B SHA (seed 2) | matches v1.15 |
|------|----------|--------------------|---------------|--------------------|---------------|
| W29C020    | 262144 | `b2fc5cbfcc25be3daa0e8e88e6977c7da6164a6fcf9c577ca943da940a133457` | ✓ | `47304933ce388bfd97d23ea6bff1a5ed1f7728e99f2cc3e7d05c82a7c11ce58c` | ✓ |
| SST39SF040 | 524288 | `77a771b26acca207c670a22ade19f8d6f0258a79fefb789be2ea7a40f1662bbd` | ✓ | `a38b13b4d285756c1f385a75d0cdf89f72720764c21fd933ced75ebdd970b96b` | ✓ |
| W27C512    | 65536  | `604d957094f7cb1f98f50d7408f64e7720e5ae5d4acab8d1047a9a081645d637` | ✓ | `e16b2a5b26d99440a8e596963faa0f2d64fff4e1dd9682b93b2f8f1ddc326ab5` | ✓ |
| FM1608     | 8192   | `a89c4b45ae8a2dac63911f153cff29d4d59f8d61c5579f93a53e8d078ce5415d` | ✓ | `3c23e7fcbe88c5a09ab50cf8301e9adf884fcdd519b6f9fefc72583b34f75c90` | ✓ |

Images staged at `/tmp/firestarter_bench_p90/<chip>_img_{A,B}.bin`.

---

## Per-Chip Regression Blocks

> Sequencing (D-01): READ regression (N≥3) runs BEFORE the write-cycle per chip — the
> write overwrites the contents the read baseline measured. Preconditions per chip:
> operator confirms controller identity + port, confirms Rev 2.0 silkscreen, seats ONE
> chip, authorizes the live op.

<!-- Per-chip blocks appended below as the session proceeds (Task 2). -->
