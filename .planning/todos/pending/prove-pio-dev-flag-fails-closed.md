---
created: 2026-07-28T00:00:00Z
title: Prove the PlatformIO dev-tools build flag fails CLOSED (empirical, not assumed)
area: firmware
resolves_phase: 999.15
files:
  - firestarter/platformio.ini ([env] build_flags — the DEV_TOOLS leak)
  - firestarter/src/dev_tools.cpp (dt_set_registers / dt_set_address — the symbols to check)
  - firestarter/include/firestarter.h (CMD_DEV_ADDRESS / CMD_DEV_REGISTER guards, line 42)
  - .planning/notes/dev-tools-gating-channel-split.md (design this de-risks)
---

## Problem

The channel-split gating design (see `notes/dev-tools-gating-channel-split.md`) needs a
PlatformIO mechanism that turns `DEV_TOOLS` **off by default** and **on only in the dev
environment / pre-release build**. The obvious mechanism is fail-**open** and would silently
defeat the entire feature:

```ini
build_flags = -D DEV_TOOLS=${sysenv.FIRESTARTER_DEV_TOOLS}
```

With the variable unset this plausibly expands to `-D DEV_TOOLS=`, which still **defines** the
macro (as empty), so every `#ifdef DEV_TOOLS` guard stays true and the dev commands leak into
every release build. That is the exact bug class being removed — `-D DEV_TOOLS` currently
leaking from the shared `[env]` block into `uno` / `uno328pb` / `leonardo` *and* `native`.

This must be **measured**, not reasoned about. A design that assumes the expansion behaviour
and gets it backwards ships dev tools in the stable release while all its tests pass.

## Task

Run the matrix and record the result:

1. Try the two candidate shapes:
   - `-D DEV_TOOLS=${sysenv.FIRESTARTER_DEV_TOOLS}` (suspected fail-open)
   - `${sysenv.FIRESTARTER_DEV_FLAGS}` carrying the whole flag, i.e. env var value is
     literally `-D DEV_TOOLS` (suspected fail-closed — the safe shape)
2. For each, build with the variable **set** and **unset**: `pio run -e leonardo`.
3. Do **not** trust the build log or the flash-size delta as the oracle. Check the linked
   binary for the symbols:
   ```bash
   avr-nm .pio/build/leonardo/firmware.elf | grep -iE 'dt_set_registers|dt_set_address'
   ```
   Absent in both = gated. Present with the var unset = fail-open, mechanism rejected.
4. Also confirm `pio test -e native` still passes with `DEV_TOOLS` **absent** — grep says
   nothing under `firestarter/test/` references `DEV_TOOLS` or `CMD_DEV_*`, so this should
   hold, but the shared-`[env]` inheritance means it has never actually been exercised without
   the flag.

## Why symbol-checking, not exit codes

A `pio run` that succeeds proves nothing about whether the guards fired — the guarded code
compiles fine either way. And a flash-size comparison is a weak oracle here: v1.22 Phase 117
already produced a +204 B Leonardo delta that contradicted a size-based prediction
(`project_v122_phase117_closed`). The symbol table is the only direct evidence that
`dev_tools.cpp` did not link.

## Acceptance

- A recorded before/after `avr-nm` capture for the chosen mechanism, both var-set and
  var-unset, on at least one AVR target.
- An explicit statement of which mechanism was chosen and which was rejected, with the
  observed expansion behaviour — so the phase does not re-derive it.
