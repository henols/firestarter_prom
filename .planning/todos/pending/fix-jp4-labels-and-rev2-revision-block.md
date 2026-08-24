---
title: "Fix JP4 labels + Rev-2 revision block in info jumper display"
date: 2026-07-02
priority: medium
---

# Fix JP4 labels + Rev-2 revision block in `info` jumper display

Safe, self-contained display fix. **No chip-database or firmware change** — does
NOT attempt to add the 3rd-position / 2516 support (that's the seed
`rev22-3pin-header-2516-family-support.md`).

## Scope

In [ic_layout.py:169-184](../../../firestarter_app/firestarter/ic_layout.py#L169-L184)
(`_get_rev2_jumper_settings_data`):

1. **Fix JP4's copy-paste labels.** `config_text` and `pin_text` are currently
   `"28pin"` / `"32pin"` (cloned from JP3) and render as meaningless text. JP4 is
   the VPP bypass jumper — its meaningful values are Open / Closed. Give it
   labels that describe VPP-on-pin-1, not pin count.

2. **Relabel the Rev-2 block** from `"2.0 & 2.1"` to cover all four revs that
   share this JP4 header: `"2.0, 2.1, 2.2 & 2.3"` (operator confirmed 2.2/2.3
   have the same JP4, plus a 3rd angled pin handled separately by the seed).

3. **Delete the dead `_get_rev2_2_jumper_settings_data`** method
   ([ic_layout.py:186-199](../../../firestarter_app/firestarter/ic_layout.py#L186-L199))
   and its commented-out call site
   ([ic_layout.py:656](../../../firestarter_app/firestarter/ic_layout.py#L659)) —
   it invents a phantom "JP5" that does not exist on the hardware.

## Acceptance

- `firestarter info <a 28-pin UV-EPROM>` prints a JP4 line with sensible
  Open/Closed labels (no "28pin, 32pin").
- The Rev-2 block header names 2.0–2.3.
- No `_get_rev2_2` / JP5 references remain.
- Existing tests + ruff/format/mypy gate stay green.

## Context

See `notes/info-jumper-display-design-audit.md` for the full audit.
