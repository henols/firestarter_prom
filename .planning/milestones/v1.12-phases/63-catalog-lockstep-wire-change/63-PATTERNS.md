# Phase 63: Catalog Lockstep Wire Change - Pattern Map

**Mapped:** 2026-06-11
**Files analyzed:** 3 edit/regen surfaces (no new files; all edits to existing files)
**Analogs found:** 3 / 3

## File Classification

| Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `tools/catalog/messages.toml` | config | transform (TOML source → generated outputs) | `[[messages]]` stanza for `MSG_ERR_MEM_TYPE_UNSUPPORTED` (0xAE) at lines 449–455 | exact |
| `firestarter/include/messages.h` | config (generated) | transform output | `#define MSG_ERR_MEM_TYPE_UNSUPPORTED 0xAE` at line 83 | exact |
| `firestarter_app/firestarter/messages.py` | config (generated) | transform output | `MSG_ERR_MEM_TYPE_UNSUPPORTED = 0xAE` at line 99; `CATALOG[0xAE]` block at lines 527–535 | exact |

## Tooling Inventory

| File | Role |
|---|---|
| `tools/catalog/sync_to_subrepos.sh` | Copies `messages.toml` + `codegen.py` byte-identically into both sub-repos, then invokes codegen for each |
| `tools/catalog/codegen.py` | Reads `messages.toml`, generates `messages.h` (C++) and `messages.py` (Python) |
| `firestarter/tools/catalog/codegen.py` | Sub-repo copy (byte-identical to meta; written by sync script) |
| `firestarter_app/tools/catalog/codegen.py` | Sub-repo copy (byte-identical to meta; written by sync script) |

## Pattern Assignments

### `tools/catalog/messages.toml` — TOML canonical edit

**Analog:** `[[messages]]` stanza for `MSG_ERR_MEM_TYPE_UNSUPPORTED` (0xAE), lines 449–455.

**Header comment (lines 6–8) — edit-only-here + sync convention:**
```
# Distribution: copied byte-identically into firestarter/tools/catalog/ and
# firestarter_app/tools/catalog/ by tools/catalog/sync_to_subrepos.sh.
# Edit ONLY this meta-repo copy; run the sync script after every edit.
```

**Sibling analog stanza — `MSG_ERR_MEM_TYPE_UNSUPPORTED` (lines 449–455):**
```toml
[[messages]]
id          = 0xAE
name        = "MSG_ERR_MEM_TYPE_UNSUPPORTED"
severity    = "ERROR"
format      = "Memory type 0x%02x not supported"
params      = [{ type = "u8", render = "hex_byte" }]
wire_format = "id_frame"
```

**Immediately-preceding ERROR-band tail (the last two entries before the gap, lines 572–578) — `MSG_ERR_MEM_SIZE_TOO_SMALL` at 0xBA, which is the current band tail:**
```toml
[[messages]]
id          = 0xBA
name        = "MSG_ERR_MEM_SIZE_TOO_SMALL"
severity    = "ERROR"
format      = "Memory size %lu too small for chip-id check"
params      = [{ type = "u32", render = "dec" }]
wire_format = "id_frame"
```

**New 0xBB stanza (D-01, locked) — insert immediately after the 0xBA block above:**
```toml
[[messages]]
id          = 0xBB
name        = "MSG_ERR_PROTOCOL_NOT_IMPLEMENTED"
severity    = "ERROR"
format      = "Protocol 0x%02x not implemented"
params      = [{ type = "u8", render = "hex_byte" }]
wire_format = "id_frame"
```

**Note on placement:** After the 0xBA block, the very next block in the file is the `# DATA (0xE0..0xEF)` section comment followed by `MSG_DATA_PROGRESS`. The new 0xBB stanza is inserted between the 0xBA block and that section comment. Source order is for human readability; codegen sorts by id ascending.

---

### `firestarter/include/messages.h` — generated C++ output

**Analog:** `#define MSG_ERR_MEM_TYPE_UNSUPPORTED   0xAE` at line 83; `#define MSG_ERR_MEM_SIZE_TOO_SMALL     0xBA` at line 95.

**Current ERROR-band tail region (lines 83, 95–96) showing the gap the new entry fills:**
```c
#define MSG_ERR_MEM_TYPE_UNSUPPORTED   0xAE
...
#define MSG_ERR_MEM_SIZE_TOO_SMALL     0xBA
#define MSG_DATA_PROGRESS              0xE0
```

**Expected post-regen diff shape — one new `#define` line inserted between 0xBA and 0xE0:**
```c
#define MSG_ERR_MEM_SIZE_TOO_SMALL     0xBA
#define MSG_ERR_PROTOCOL_NOT_IMPLEMENTED 0xBB
#define MSG_DATA_PROGRESS              0xE0
```

Column alignment of the new line matches the codegen's padded format. The exact column width is determined by `codegen.py`; the existing 0xAE line (`MSG_ERR_MEM_TYPE_UNSUPPORTED   0xAE`) uses a 3-space separator after the longest name in the block — the new name is longer, so the planner should verify codegen output rather than hand-predict padding.

---

### `firestarter_app/firestarter/messages.py` — generated Python output

**Analog:** Two locations — the module-level constant and the `CATALOG` dict entry.

**Module-level constant analog (lines 99, 111):**
```python
MSG_ERR_MEM_TYPE_UNSUPPORTED = 0xAE
...
MSG_ERR_MEM_SIZE_TOO_SMALL = 0xBA
```

**Expected post-regen diff for module-level constants — one new line after 0xBA:**
```python
MSG_ERR_MEM_SIZE_TOO_SMALL = 0xBA
MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB
```

**CATALOG dict entry analog for `MSG_ERR_MEM_TYPE_UNSUPPORTED` (lines 527–535):**
```python
    0xAE: MessageDef(
        id=0xAE,
        name="MSG_ERR_MEM_TYPE_UNSUPPORTED",
        severity=SEVERITY_ERROR,
        format="Memory type 0x%02x not supported",
        params=(("u8", "hex_byte"),),
        param_bytes=1,
        wire_format="id_frame",
    ),
```

**CATALOG dict entry analog for `MSG_ERR_MEM_SIZE_TOO_SMALL` (lines 635–643) — the current 0xBA tail:**
```python
    0xBA: MessageDef(
        id=0xBA,
        name="MSG_ERR_MEM_SIZE_TOO_SMALL",
        severity=SEVERITY_ERROR,
        format="Memory size %lu too small for chip-id check",
        params=(("u32", "dec"),),
        param_bytes=4,
        wire_format="id_frame",
    ),
```

**Expected post-regen diff for CATALOG — one new entry after 0xBA, before 0xE0:**
```python
    0xBB: MessageDef(
        id=0xBB,
        name="MSG_ERR_PROTOCOL_NOT_IMPLEMENTED",
        severity=SEVERITY_ERROR,
        format="Protocol 0x%02x not implemented",
        params=(("u8", "hex_byte"),),
        param_bytes=1,
        wire_format="id_frame",
    ),
```

`param_bytes=1` because the single `u8` param is one wire byte (matches 0xAE shape exactly).

---

## Shared Patterns

### Edit-only-in-meta-repo convention
**Source:** `tools/catalog/messages.toml` header, lines 6–8
**Apply to:** All three edit surfaces
Never hand-edit `firestarter/tools/catalog/messages.toml` or `firestarter_app/tools/catalog/messages.toml` directly. Only edit the meta-repo canonical copy, then run `tools/catalog/sync_to_subrepos.sh`.

### Codegen invocation via sync script
**Source:** `tools/catalog/sync_to_subrepos.sh` lines 79–95
The script runs `codegen.py` twice:
```bash
python3 "$META_REPO_CATALOG/codegen.py" \
    --catalog "$META_REPO_CATALOG/messages.toml" \
    --language cpp \
    --target "$FS_ROOT/include/messages.h"

python3 "$META_REPO_CATALOG/codegen.py" \
    --catalog "$META_REPO_CATALOG/messages.toml" \
    --language python \
    --target "$FA_ROOT/firestarter/messages.py"
```
**Apply to:** The single executor step that runs codegen. The script handles both sub-repos in one invocation.

### Python 3.11 drift trap
**Source:** D-04 in CONTEXT.md; `reference_devcontainer_py312_masks_ci_py39.md` memory note
**Apply to:** All codegen verification steps
The devcontainer has Python 3.12; CI uses Python 3.11. Codegen output that looks clean under 3.12 can fail the CI drift gate under 3.11. The drift gate is `codegen + git diff --exit-code`. Executor must validate under 3.11 before claiming green. Typical mechanism: locate the CI-matching interpreter (check `/usr/bin/python3.11` or the firestarter_app CI workflow for the exact invocation), run `python3.11 tools/catalog/codegen.py ...` or invoke the sync script with that interpreter on PATH.

### Drift gate verification
**Source:** `firestarter/.github/workflows/build.yml`; `firestarter_app/.github/workflows/ci.yml`
After codegen: in each sub-repo, run `codegen.py` again with no TOML changes, then `git diff --exit-code` on the generated file. Zero diff = gate green.

## No Analog Found

None. All three surfaces have exact analogs in the live codebase (the 0xAE sibling and the current 0xBA tail entry).

## Metadata

**Analog search scope:** `tools/catalog/`, `firestarter/include/`, `firestarter_app/firestarter/`
**Files scanned:** 5 source files (messages.toml, messages.h, messages.py, sync_to_subrepos.sh, codegen.py)
**Pattern extraction date:** 2026-06-11
