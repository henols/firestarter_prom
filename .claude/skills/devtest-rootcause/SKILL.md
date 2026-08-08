---
name: devtest-rootcause
description: Investigate the firestarter code behind a triaged `dev test` chip failure and fix the real defect — a decode bug in the database generator, or a genuine bug in the host app or firmware. Knows that chip_database.json is generated and must never be hand-edited. Use when asked to investigate why an EPROM fails, root-cause a dev test issue, fix a chip's pinout or protocol or VPP, correct the database generator, act on the datasheet findings left on an issue, or make a chip like at28c256 or w27e257 work.
---

# Root-cause a `dev test` failure in the code

Takes the datasheet findings `devtest-triage` left on an issue and turns them into a
fix in the **right** file. The hard part is not the fix, it is knowing which files may
be edited at all.

**Self-contained.** `scripts/infoic_lookup.py` is stdlib-only and owns its decode
tables outright — it never imports `build_db.py`, so it works even with
`firestarter_app` absent. `--check` guards against the copy drifting (see §1).

That is distinct from the **regeneration commands** in §4 (`build_db.py`,
`diff_db.py`, `check_dispatch.py`). Those are the project's own build and gate steps —
the thing being fixed — exactly like `pytest` or `pio run`. A skill must not
reimplement or shadow them; regenerating the database means running the real generator.

```bash
APP=/workspaces/firestarter_app
FW=/workspaces/firestarter
S=/workspaces/.claude/skills/devtest-rootcause/scripts

python3 $S/infoic_lookup.py AT28C256        # what upstream actually says about the chip
python3 $S/infoic_lookup.py --check         # our tables still agree with build_db.py?
python3 $S/seed_debug_session.py 32         # seed a GSD debug session from the issue
```

## The fix surface — read this before editing anything

| File | Status | May you edit it? |
|---|---|---|
| `$APP/firestarter/data/chip_database.json` | **GENERATED** by `tools/build_db.py` | **NEVER.** Edits are erased on the next regen. Fix the generator, regenerate |
| `$APP/tools/build_db.py` | authored — the decoder | Yes, subject to the proof rule below |
| `$APP/firestarter/data/pinouts.json` | authored — input to the generator, never written by it | Yes. This is where a wrong socket wiring is really fixed |
| `$APP/tools/extra_chips.json` | authored supplement | Only for chips **absent from infoic.xml entirely** (2516, 2532). Not an override for a chip upstream already has |
| `$APP/firestarter/*.py` | authored host app | Yes — real bugs |
| `$FW/src/`, `$FW/include/` | authored firmware | Yes — real bugs. Cannot be verified without bench hardware; say so |
| `$FW/include/messages.h` | **GENERATED** from the meta repo's `messages.toml` | Never hand-edit; regenerate |

### The proof rule

**The generator may not emit a field it cannot prove from `infoic.xml`.**

Every value in a database entry must be *decoded from an attribute upstream actually
carries*. Do not add invented fields, per-chip lookup tables keyed on part number, or
hand-maintained override stacks. Three such guess tables were deliberately deleted in
Phase 70; do not reintroduce the pattern under a new name.

If a chip decodes wrongly, the bug is in **how an existing attribute is interpreted**
— `flags`, `voltages`, `protocol_id`, `variant`, `pin_map`, `type` — and the fix
belongs in the function that interprets it. If the information genuinely is not in
`infoic.xml`, the honest outcome is to report that, not to invent a field.

> Known pre-existing exception, flagged rather than copied: `_PAGE_SIZE_BY_PART` in
> `build_db.py` adds a `page_size` field from `[CITED:]` **datasheets**, not from
> `infoic.xml`. It predates this rule and is the exact shape the rule forbids. Do not
> extend it or add siblings to it. Upstream carries `infoic_page_size_raw` for this,
> which is the principled seam if page size ever needs revisiting.

## 1. See what upstream actually says

```bash
python3 $S/infoic_lookup.py AT28C256
```

Real output:

```
=== AT28C256,AT28C256@SOIC28,AT28C256E,...,AT28HC256L   [ATMEL]   (INFOICT76) ===
  matched           : AT28C256, AT28C256@SOIC28   packages: (unqualified), SOIC28
  flags & 0x10      = SET   -> electrically erasable   (raw flags 0xC010)
  voltages & 0xF0   = 0x00  -> VPP 12V   (option bits 0x0)
  protocol_id       = 0x07  -> programming.algorithm, before any safety flip
  variant           = 0x4126 (lo=0x26, hi=0x41)  -> resolve_pinout_key()
  pin_map           = 0x0C14 (lo=0x14 = pm_idx)  -> resolve_pinout_key()
  type              = 1 (EEPROM)
  code_memory_size  = 32768 (0x8000)  -> electrical.size_bytes
```

The script owns its decode tables rather than importing the generator, so it stays
usable standalone. The cost of a private copy is drift, so verify it after touching
`build_db.py`:

```bash
python3 $S/infoic_lookup.py --check
```

```
ok: MINIPRO_XML_URL matches build_db.py
ok: VPP_VOLTAGES matches build_db.py (16 entries)
```

It reads the generator **as text** (`ast.literal_eval`, never importing or running it —
running it would regenerate the database) and exits 1 naming any key that disagrees.
With `firestarter_app` absent it prints `SKIP` and exits 0; the lookup still works.

Never "improve" a table value from memory. An earlier draft of this script guessed
`0x80` as 18V when it is **13.5V**, which would have "proved" a decode bug in W27E257
that does not exist. Transcribe, then run `--check`.

`--raw` dumps every attribute verbatim when you need one the decoder ignores.

Three things this output will trip you on:

- **Package suffixes.** Upstream names are qualified — `W27E257@DIP28`. Some parts
  appear *only* suffixed. DIP is the package this project programs; a PLCC/SOIC row
  legitimately carries a different `protocol_id` and pinout and is not evidence of a bug.
- **A part appears once per upstream database** (`INFOICT76`, `INFOIC2PLUS`, `INFOIC`)
  and the rows can disagree — the legacy `INFOIC` row for AT28C256 says
  `protocol_id=0x31`. Check which database `build_db.py` consumes before treating a
  row as authoritative.
- **Not found means not found.** `infoic_lookup.py 2516` exits 1 — and 2516 is one of
  exactly two chips in `extra_chips.json`. That is the supplement's whole remit.

Compare against what shipped:

```bash
cd $APP && firestarter info -a at28c256
python3 -c "
import json,re
d=json.load(open('firestarter/data/chip_database.json'))
for m,cs in d.items():
    for e in cs:
        if 'AT28C256' in e.get('part_number',''):
            print(m, json.dumps(e, indent=2))"
```

**A difference is not automatically a bug.** `build_db.py` deliberately flips 5V
parallel EEPROMs from upstream's `0x07` to `0x0D` so a 12V rail is never driven into a
5V part — that is why AT28C256 ships as algorithm `13` despite upstream saying `0x07`.
Read the rule and its comment before "correcting" it. Likewise the `vpp: "12V"` on that
part is a faithful decode of VPP index `0x00`; protocol `0x0D` never routes it.

## 2. Decide which layer is at fault

| Evidence from triage | Layer | Where |
|---|---|---|
| Pin map disagrees with the datasheet DIP view | pinout data | `pinouts.json` if the key's wiring is wrong; `resolve_pinout_key()` if the wrong key was chosen |
| Wrong `electrical.type` / erase capability | decode | `classify()` — the `flags & 0x10` axis, not `protocol_id` |
| Wrong VPP | decode | the VPP index table; mask `voltages & 0xF0`, never `& 0xFF` |
| Wrong algorithm/protocol | decode | `classify()` and the safety-flip rules in `main()` |
| Wrong pulse timing | decode | `interpret_timing()` |
| Chip missing from the DB entirely | supplement | `extra_chips.json`, only if absent from `infoic.xml` |
| Right data, wrong behaviour on the wire | host | `$APP/firestarter/eprom_operations.py`, `serial_comm.py`, `chip_resolver.py` |
| Right command, wrong hardware sequence | firmware | `$FW/src/proms/*.cpp` for the protocol, `src/eprom_operations.cpp` |

Firmware protocol implementations map to the constants in `$FW/include/proto_constants.h`
(`eprom.cpp`, `eeprom_28c.cpp`, `flash_5v_page.cpp`, `flash_nor_unlock.cpp`,
`flash_intel.cpp`, `sram.cpp`). Constants and flag bits are duplicated between
`$APP/firestarter/constants.py` and `$FW/include/firestarter.h` — change both together.

## 3. Hand the fix to `gsd-debug`

Once §2 says *which layer* is at fault but not *why*, stop reasoning in this context
and run the fix through a GSD debug session. That gets the scientific-method loop,
a persistent session file that survives a context reset, and atomic commits.

Seed the session first — the whole point of the handoff is that the debugger inherits
the datasheet work instead of redoing it:

```bash
python3 $S/seed_debug_session.py 32                    # from the triaged issue
python3 $S/seed_debug_session.py 32 --slug at28c256-sdp-write
```

```
[debug] Session: /workspaces/.planning/debug/at28c256-sdp-write.md
[debug] Status: investigating
[debug] Carried over 5 eliminated hypotheses from triage
```

It reads the issue and the `devtest-triage` comment, then writes a standard GSD debug
session file with `Symptoms` and `Context` filled from the report, and every **MATCH**
row of the triage table pre-recorded under `Eliminated`:

```
- hypothesis: Pin map (28-DIP) is wrong
  evidence: datasheet says §2.4 pins 1–28; database has `DIP28_28C256` —
            triage cross-check verdict MATCH — all 28 pins agree
```

Rows that were *not* proven dead (a `LOW` or `represented` verdict) are deliberately
left out — only a settled question gets eliminated. A PASS report is refused: that is
`devtest-triage` territory, not a debug session.

The script then prints the spawn prompt. **Spawn `gsd-debugger` directly:**

```
Agent(prompt=<the printed prompt>, subagent_type="gsd-debugger",
      description="Debug at28c256-sdp-write")
```

**Do not spawn `gsd-debug-session-manager`, and do not invoke `/gsd-debug` for this.**
In this devcontainer agents launch in the background and the manager's nested spawn
does not complete: it returns a bogus "waiting…" message with the session file
untouched, while an orphaned debugger keeps running. Two debuggers then race the same
serial port and confound every hardware reading. One level, directly, is the rule here.
Before spawning, check no earlier debugger is still alive on the port.

The printed prompt already carries the §0 fix-surface rules verbatim. That is not
decoration: `gsd-debugger` has Write access and no knowledge that
`chip_database.json` is generated — without those constraints it will "fix" the JSON
and the change will vanish at the next regen. If you write the prompt yourself, carry
them, plus the hardware note that `dev test` always writes and needs operator consent.

When the debugger returns, continue at §4 — a debug session does not exempt a database
change from the regen-and-diff proof.

## 4. Regenerate and prove the change

Never edit the JSON. After changing the generator:

```bash
cd $APP
python3 tools/build_db.py            # fetches the pinned infoic.xml SHA, rewrites the DB
python3 tools/diff_db.py             # per-chip diff vs tools/baseline/ — the review artifact
python3 tools/check_dispatch.py      # GATE-03 safety: no 12V handler on a no-VPP-pin part
git diff --stat firestarter/data/chip_database.json
```

`build_db.py` takes no arguments and **runs the full regen on any invocation** —
there is no `--help`. It is deterministic against the pinned SHA: on an unmodified
tree it reproduces the shipped file byte for byte, so any diff is *yours*.

Read `diff_db.py` output as the evidence for the change. A one-chip fix that moves
hundreds of chips means the decode change was too broad — that is the signal this
pipeline exists to give you.

Then the app's own gates:

```bash
cd $APP && python3 -m pytest -o addopts="" -q
```

Doubling `-q` hides the count line, hence the `-o addopts=""`. If the baseline chip
count changes, `tools/baseline/` must be re-anchored deliberately and explained — not
quietly refreshed to make a test pass.

For firmware:

```bash
cd $FW && pio run -e uno && pio test
```

A firmware protocol change cannot be validated without a chip on the bench. Say that
explicitly rather than implying the fix is confirmed.

## 5. Close the loop

Report on the issue what changed and what remains unproven:

```bash
gh issue comment 32 --repo henols/firestarter_prom --body-file /tmp/fix.md
```

Leave the issue **open** until a fresh `dev test` run passes on hardware — a code fix
is not a validation. Only `devtest-triage` closes issues, and only on a PASS report.

## Hard rules

- `chip_database.json` is generated. Editing it is always wrong.
- No generator field without proof in `infoic.xml`. No per-chip guess tables.
- `extra_chips.json` adds chips upstream lacks; it does not override chips upstream has.
- Never weaken `check_dispatch.py` (GATE-03) to make a change pass. It exists to stop
  12V reaching a 5V part's WE/address pin — a hardware-damage guard, not a lint.
- Do not "fix" `PROTO_PHANTOM_0x35` / `0x39` spelling in `proto_constants.h`; those
  substrings are deliberate.
- File-changing work in this project goes through GSD so it lands with atomic commits
  and state tracking. An unexplained failure goes to a seeded debug session (§3); an
  already-diagnosed one-line fix can go to `/gsd-quick`. Route there rather than
  committing around the gate.
- Spawn `gsd-debugger` **directly**, one level. Never `gsd-debug-session-manager`, and
  never two debuggers at once — they race the serial port and confound the readings.
- Any prompt handed to a debugger must carry the fix-surface rules. It has Write access
  and does not otherwise know the database is generated. `seed_debug_session.py`
  includes them; if you hand-write a prompt, include them yourself.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Database edit vanished | You edited the generated JSON. Fix `build_db.py` or `pinouts.json`, regenerate |
| `build_db.py` prints many `WARN: skipping … unknown protocol_id` | Normal. Upstream carries families firestarter has no handler for |
| `diff_db.py` shows hundreds of changed chips | Decode change too broad. Narrow the condition |
| `WARN: resolved pinout key 'X' not in pinouts.json` | `resolve_pinout_key()` returned a key with no definition — add the wiring or fix the resolution |
| `check_dispatch.py` reports violations | A 12V-handler chip has no `vpp-pin`. Fix the classification, never the gate |
| Chip not found by `infoic_lookup.py` | Check the part really is absent, not just package-suffixed — the script already splits on `@`. If genuinely absent → `extra_chips.json` territory |
| Fetch of infoic.xml is slow | 17.8 MB. It caches to `$TMPDIR/infoic-<sha>.xml`; reuse it |
| Debugger edited `chip_database.json` | Its prompt lacked the fix-surface rules. Revert, reseed with `seed_debug_session.py`, respawn |
| Session manager returns "waiting…" and nothing changed | Known devcontainer failure. Spawn `gsd-debugger` directly instead (§3) |
| `seed_debug_session.py` refuses a PASS issue | Correct — a PASS goes to `devtest-triage` to be closed and logged |
| `--check` reports DRIFT | `build_db.py` changed. Update the table in `infoic_lookup.py` to match the generator — the generator is authoritative, not this script |
