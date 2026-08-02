# v1.23 Honesty Ledger — PY32F071 Integration

**Milestone:** v1.23 — PY32F071 Integration
**Firmware branch (`firestarter`):** `v1.23-py32f071-integration` · **HEAD at this writing:** `05c20bf59a4f0f73acf28d48d5dbbedab5724c5f`
**Host branch (`firestarter_app`):** `v1.23-py32f071-integration` · **HEAD at this writing:** `cc9452f4db9a814ffb221bab767c24db67288365`
**Meta branch:** `gsd/v1.23-py32f071-integration`
**Published cut tag:** **not yet observed.** Plan 130-15 fills this field after reading the real tag from `gh release list` against both repos; no version string is predicted here.
**Oracle:** software-only — native register trace (`pio test -e native` / `-e native_nodevtools`), host pytest (`firestarter_app`), source-scan gates (`tools/check_*.py`, this phase's `check_permitted_claims.py` / `check_record_corrections.py`), a local ARM configure+build (delta and byte-identity claims only), and two operator-authorised CI rehearsal dispatches of `beta-build.yml`. **No PY32F071 hardware exists**, so no board-level oracle contributed anything below.
**Generated:** 2026-08-02

**Composes with (cross-reference only — no data copied):**
- `.planning/REQUIREMENTS.md` §"Validation Ceiling" — the permitted-claim / forbidden-claim ceiling this ledger distils into evidence tiers
- `.planning/v1.23-FLASH-PATH-DECISION.md` — cross-reference only, no data copied, per that record's own line 28 ("this record's per-claim pairs are what CLOSE-02's honesty ledger consumes... by cross-reference")
- `.planning/research/SUMMARY.md` §"What Cannot Be Validated" — the raw material for the negative-space section below
- `.planning/phases/124-firmware-integration-merge/124-NONREGRESSION.md` §F4d — the A-5 discharge citation
- `.planning/phases/127-host-dfu-installer/127-NONREGRESSION.md` §7 — HOST-03's mock-only ceiling paragraph, cited rather than duplicated
- `.planning/phases/128-release-asset-fold/128-NONREGRESSION.md` §7 — REL-03/REL-04's stated seams
- `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-LEDGER.md` — the structural analog this document's shape follows

**Referenced and verified here, never edited.** `.planning/v1.23-FLASH-PATH-DECISION.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md` and `.planning/PROJECT.md` are all read by this document and none is written by it — this plan's own held-writes contract forbids it, and all five were independently brought green under `check_record_corrections.py` by plans 130-06 through 130-10 before this plan started.

---

## The ceiling, quoted verbatim

Attributed to `.planning/REQUIREMENTS.md` §"Validation Ceiling":

> **Permitted claims:** the target builds clean; the native and host suites pass at their recorded case *and* suite counts; the DFU sequence is exercised against device descriptors and mocks; host-side timing and sizes are measured where a tool exists to measure them.

**Forbidden claims:** cited by location rather than reproduced — `.planning/REQUIREMENTS.md:14`. This ledger does not repeat that line's five forbidden phrasings: doing so would trip this same document's own claim scanner (`check_permitted_claims.py`), which matches a phrase's shape regardless of quotation context, by design. That is the gate working as intended, not a defect to route around — the permitted-claims sentence quoted above is safe to reproduce because it contains no trigger shape.

**No PY32F071 hardware exists.** Every figure in this document has a software artifact as its subject — a golden register trace, a `pio run` size report, a pytest exit code, a source-scan result, a local or CI build log — never an observation made on a physical board.

---

## Status / claim key

- **`PERMITTED`** — a wording backed by a measured, re-runnable software artifact (a trace, a test, a source scan, a size report, a CI run).
- **`CONTEXT-ONLY`** — measured, cited for context, but explicitly not a gate.
- **`FORBIDDEN`** — the ceiling's forbidden claim. Appears in this ledger only as a citation of what is *not* claimed, never as prose asserting it.

## Sourcing key (Phase 129's vocabulary)

- **`[VERIFIED]`** / **`[VERIFIED: <evidence>]`** — a fact read from a file in this tree, or executed in this session.
- **`[CITED: <source>]`** — a fact from a published document or an external record (a CI run URL, a registry page).
- **`[ASSUMED — <reason>]`** — a reasoned inference, not directly sourced.
- **`[UNVERIFIED-UNTIL-SILICON]`** — anything whose truth depends on a PY32F071 part behaving as documented. No PY32F071 board exists, so every silicon-behaviour claim carries this tag regardless of documentation quality.

**These two axes answer orthogonal questions** — the status key says what may be *written*; the sourcing key says where the *fact* came from — and a row can legitimately be `PERMITTED` and `[ASSUMED]` at once: a permitted claim can rest on a reasoned inference, so long as the inference itself, not a silicon observation, is what is being claimed.

---

## Evidence tiers — weakest to strongest

This milestone's defining fact is that **all of it is software-only**: a green CMake configure and a published release asset are not comparable proof, so grouping claims by evidence tier — rather than one row per requirement category — is what keeps two adjacent rows from reading as equally strong. The six tiers below are ordered so the strength gradient is visible on the page; only the last two tiers touch anything published or decided about a physical board, and even there the permitted wording never extends past publication or decision, never to a board running.

### CI-compile-only

| Class | Permitted wording | Evidence (measured, with source) | Explicitly does NOT prove |
|---|---|---|---|
| **The ARM target configures and compiles** `PERMITTED` `[VERIFIED: CI run 30722352902]` | The PY32F071 target reaches a successful CMake configure and links a complete image inside CI, after the version bump, in the same job as the three AVR images. | MERGE-02 (Phase 124); the REL-01 step-order proof (`128-NONREGRESSION.md` §2.1: version/auto-commit/arm/Release step indices strictly increasing) plus a real dispatch, CI run `30722352902` — 22/22 steps `success`. | That the resulting image executes anything once written to a part — a successful compile says nothing about runtime behaviour. |
| **The version string is embedded correctly** `PERMITTED` `[VERIFIED: CI run 30722352902 step summary]` | The published image's version string matches the release version the host will compare against the tag (REL-01). | `128-NONREGRESSION.md` §3.5 — the run's own step-summary pass line, naming the dispatched version and board suffix. | Anything about the image beyond the string it embeds. |
| **A deliberately-broken ARM leg cannot silently take down the AVR release** `PERMITTED` `[VERIFIED: CI run 30722537152]` | A planted ARM-configure failure is contained: the three AVR `.hex` assets still publish, and the release step still succeeds, with a warning annotation naming the missing py32 asset. | `128-NONREGRESSION.md` §3.7–§3.9, a second real CI dispatch against a deliberately broken source-list entry (reproducing the historical C-1 defect on purpose). | That the failure-containment machinery has ever been exercised against a *real*, non-planted ARM regression — this is a planted-fault rehearsal, not an observed incident. |

### AVR-measured

| Class | Permitted wording | Evidence (measured, with source) | Explicitly does NOT prove |
|---|---|---|---|
| **AVR flash and RAM recorded for all three targets** `PERMITTED` `[VERIFIED: 124-NONREGRESSION.md §F4d]` | Leonardo flash **does not grow** (26072→26016, −56 B); Uno-class growth is **≤64 B, recorded** (Uno +22 B, uno328pb +28 B); RAM is unchanged on every target — measured against the BASE-01 baseline. | `check_size_baseline.py --policy merge05`, run and recorded in `124-NONREGRESSION.md` §F4d: `PASS: uno(flash=23954/32256[+22<=64],ram=1573/2048[=]), uno328pb(flash=24004/32384[+28<=64],ram=1579/2048[=]), leonardo(flash=26016/28672[-56<=0],ram=2014/2560[=])`. | Anything about behaviour — a size delta is not a behaviour proof; the golden register traces (below) carry that half. |
| **The native suite passes at its recorded count** `PERMITTED` `[VERIFIED]` | `pio test -e native` and `-e native_nodevtools` both report **141 test cases / 17 suites**, matching the BASE-01/Phase-123 baseline, unchanged by the merge or any later plan. | `124-NONREGRESSION.md`, re-confirmed by `128-NONREGRESSION.md` §2.8/§2.9. | That any of this exercises code compiled for the ARM target — `native` runs the AVR-family emulation host, never the ARM cross-compile. |
| **Golden register traces are byte-identical** `PERMITTED` `[VERIFIED]` | The merge's macro-to-`static inline` conversions and the portability shim are behaviour-identical to the pre-merge tree, proven per-array (not whole-file-hash) for `_shared/sdp_expected.h` and the other golden trace arrays. | `124-NONREGRESSION.md` §4/§5. | Anything about the ARM backend, which emits no register trace this harness records (see the ARM bus-trace oracle gap, below). |
| **The AVR flash-constraint decision — discharged at Phase 124** `PERMITTED` `[VERIFIED: 124-NONREGRESSION.md §F4d]` | The operator-visible flash constraint is restated as *"Leonardo flash must not grow; Uno-class growth ≤ 64 B, recorded"* — discharged, not merely satisfied on paper: `124-NONREGRESSION.md` §F4d's own pass line is the single citation naming all three deltas, closing the single-source gap research (A-5) had flagged for the ATmega328PB figure with an independently-built 328PB image. | `124-NONREGRESSION.md` §F4d, lines 100/505–510. | Any absolute figure for the ARM target — this row is entirely about the three AVR targets. |

### native-simulated

| Class | Permitted wording | Evidence (measured, with source) | Explicitly does NOT prove |
|---|---|---|---|
| **Dual-slot flash-config storage, covered against a fake backend** `PERMITTED` `[VERIFIED]` | CFG-05's dual-slot CRC32 storage design is covered on `native` against a fake backend across six named states: blank, newest-wins, CRC rejection, both-slots-corrupt, an interrupted write, and slot alternation. | Phase 126 plan SUMMARYs; `REQUIREMENTS.md` CFG-05. | That the target part's own flash-erase/write hardware behaves as the fake backend simulates — the fake backend is a native-host stand-in, never the part's own flash controller. |

### mock-only

| Class | Permitted wording | Evidence (measured, with source) | Explicitly does NOT prove |
|---|---|---|---|
| **`DFU_UPLOAD` readback, asserted against a mock** `PERMITTED` `[ASSUMED — the mock behaves exactly as instructed, per 127-NONREGRESSION.md §7]` | HOST-03's readback-and-verify sequence (the verify-result enum, the read-back step, the verify step, and all four of its outcomes) is exercised against a mock USB device that answers exactly as it is told, and fails soft when the device reports it cannot upload. | `127-NONREGRESSION.md` §7's self-contained paragraph: a matching backing image produces a verified outcome, an altered byte produces a mismatch outcome, a short slice produces a truncation failure. | That any of this sequence has ever exchanged a byte with a real bootloader. What is proven is that the flasher's own logic responds correctly to told answers, and nothing beyond that — this is one of CLOSE-02's four named minimum-coverage items. |
| **DFU opcode anchoring, independently sourced where possible** `PERMITTED` `[CITED: usb.org DFU 1.1 spec]` for the DFU-1.1 half; `CONTEXT-ONLY` `[UNVERIFIED-UNTIL-SILICON]` for the vendor-bootloader-specific half | The DFU 1.1 request codes, functional-descriptor type, and the upload-capability mask are anchored to literals fetched independently from `usb.org`, not imported from the module under test. | `127-NONREGRESSION.md` §Criterion 4 (`tests/test_dfu_opcode_anchors.py`, 7 tests). | That the vendor-bootloader-specific half of this anchor is independently confirmed — HOST-06's own residual states that source remains network-unreachable; see the residuals list below. |
| **The DFU sequence exercised against descriptors and mocks generally** `PERMITTED` `[VERIFIED]` | The whole py32 DFU client — discovery, class-based interface matching, the dialect fork, envelope refusal — is exercised against synthetic USB device descriptors and mock transports across the host test suite. | `127-NONREGRESSION.md` §2/§5. | Which of the two dialect branches a real bootloader would actually take — this fork has never been exercised against a real device by anyone, anywhere, per this project's own research. |

### real-published-artifact

| Class | Permitted wording | Evidence (measured, with source) | Explicitly does NOT prove |
|---|---|---|---|
| **A named, versioned release asset — pending observation** `PERMITTED`, pending `[ASSUMED — the publication mechanism is CI-proven via rehearsal; the real cut has not yet been observed, owed to plan 130-15]` | Once observed, the only permitted claim here is about **publication**: a file with a specific name, carrying a specific version string, became a downloadable release asset on the firmware repository's release page. Two operator-authorised rehearsal dispatches already demonstrated the mechanism at the CI level (see the CI-compile-only tier above), but no real, non-rehearsal cut has been observed by this plan. | `128-NONREGRESSION.md` §3 (the two rehearsal runs); the actual cut awaits `gh release list`, read by plan 130-15. | Anything about the published image running, booting, or installing — publication is the entire claim, and at the time this ledger is written it is not yet even a discharged claim. |

### decision-only-unverified

| Class | Permitted wording | Evidence (measured, with source) | Explicitly does NOT prove |
|---|---|---|---|
| **The provisional pin map** `PERMITTED` (as a decision) / **FORBIDDEN** to assert as fact — cited `.planning/REQUIREMENTS.md:16` `[ASSUMED — the VPP-sense pin follows the vendor's own ADC example; no schematic exists]` | A pin assignment exists so the target compiles before a schematic: the eight data lines, six control lines, and a VPP-sense channel. This is a placeholder that describes no existing PCB, chosen only to match the vendor's own reference example, nothing more. | `v1.23-FLASH-PATH-DECISION.md` §1.5/§3 R5; `include/boards/py32f071_rurp_shield.h`'s provisional-pin-map marker. | That any assignment is correct once a schematic exists. This is one of CLOSE-02's four named minimum-coverage items outright — see the negative-space section below for the mechanical enforcement this map still lacks. |
| **The USB identity decision** `PERMITTED` (as a decision) `[VERIFIED: firestarter@05c20bf]` / the ship-gate binding itself `[UNVERIFIED-UNTIL-SILICON]` because no board yet exists to ship | The descriptor now presents pid.codes' documented private-testing pair, replacing the silicon vendor's own registered pair the board previously presented; the value swap is confined to one source file, proven by a local ARM delta pass (one recompiled translation unit, numerically unchanged section sizes, a differing image hash). | `130-03-SUMMARY.md`; `.planning/v1.23-FLASH-PATH-DECISION.md` §5. | That an allocation under the community VID exists, or that the ship-gate binding — no board ships, no identity advertised, until a real allocation exists — has been satisfied. See the D-17 negative-space row below; this decision does not resolve that gate. |

<!-- gsd:write-continue -->
