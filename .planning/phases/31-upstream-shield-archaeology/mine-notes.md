# Phase 31 — Upstream Git-History Mine Notes (scratch)

**Source:** `.planning/v1.7/upstream-rurp/` (cloned from `https://github.com/AndersBNielsen/Relatively-Universal-ROM-Programmer`)
**Mined:** 2026-05-22
**Clone HEAD SHA:** `9178d8419e5f651a3e23ad040da16cb4f8c14269`
**Consumed by:** Plan 05 §1 inventory fill + §3 detect-HW fill

> **Note on re-clone:** The upstream-rurp directory at `/workspaces/.planning/v1.7/upstream-rurp/` was
> empty at Plan 04 start (Plan 01's executor populated it in an ephemeral worktree that was cleaned up).
> This executor re-cloned from the same upstream URL. HEAD SHA matches Plan 01's recorded SHA
> (`9178d8419e5f651a3e23ad040da16cb4f8c14269`), confirming identical upstream state.

---

## Pass 1 — Current state of `hardware/` on `main`

Command: `git -C .planning/v1.7/upstream-rurp log --all --pretty=format:'%h %ai %s' -- hardware/ | head -100`

Output:
```
e615783 2025-10-27 21:30:56 +0100 Add rev2 pdf schematics
7c8f262 2025-08-17 23:17:29 +0200 2716 / TMS2532 support
c2bd111 2025-06-24 13:15:42 +0200 Rev 2.3
545c824 2025-03-24 18:19:32 +0100 Merge pull request #14 from AndersBNielsen/Fused
a6fde57 2025-03-24 18:18:54 +0100 Plot PDF
234e836 2025-01-16 14:46:32 +0100 Merge pull request #11 from AndersBNielsen/Fused
50a6ea4 2024-12-20 08:30:21 +0100 Rev2.1
339f42d 2024-11-22 21:52:49 +0100 U5 changed to a socket part
f3c9ed0 2024-11-22 21:48:50 +0100 Fuse in schematic
28e0239 2024-10-17 11:35:22 +0200 Rev2
a252e39 2024-10-08 07:22:00 +0200 Rev2
220660e 2024-10-04 14:18:37 +0200 Power through address lines
e2032eb 2024-09-20 10:03:01 +0200 Fiddle with pin naming
beebd7a 2024-07-05 14:03:50 +0200 10k LED R
9fd07eb 2024-06-27 09:34:41 +0200 Change 4k7 to 10k R for green LEDs
e41329e 2024-05-17 23:27:37 +0200 Arduino sketch now successfully reads a ROM to serial.. Slowly.
9e126a7 2024-05-15 11:59:16 +0200 Initial Arduino Firmware Prototype
b84e9e0 2024-04-30 10:49:24 +0200 Rev1 PCB - Includes voltage divider on Arduino Analog Pin 2.
bbeffc6 2024-04-18 23:29:21 +0200 Green LED's .. yes
486f3d1 2024-04-18 23:28:53 +0200 Hardware release day update!
8b315d3 2024-04-01 23:45:24 +0200 PCB probably somewhat complete
c0d37be 2024-03-28 08:20:29 +0100 Getting ready for PCB..
4ba4602 2024-03-15 12:14:23 +0100 Working on a breadboard
```

Per-subdir introductions (`git log --diff-filter=A` for each `hardware/Rev2.X/`):
```
--- hardware/Rev2.1 ---
50a6ea4 2024-12-20 08:30:21 +0100 Rev2.1

--- hardware/Rev2.2 ---
c2bd111 2025-06-24 13:15:42 +0200 Rev 2.3

--- hardware/Rev2.3 ---
c2bd111 2025-06-24 13:15:42 +0200 Rev 2.3

--- hardware/rev2 ---
28e0239 2024-10-17 11:35:22 +0200 Rev2
a252e39 2024-10-08 07:22:00 +0200 Rev2
```

**Key observation:** `hardware/Rev2.2/` subdir was NOT introduced until the "Rev 2.3" commit (c2bd111,
2025-06-24). Anders archived the Rev2.2 gerbers at the same time he created Rev2.3. No standalone
`hardware/Rev2.2/*.kicad_sch` file was ever committed; only `Rev2.2-gerbers.zip` + CSV BOM files.

### hardware/ tree on main (current HEAD)

```
hardware/PinHeader_1x03_P2.54mm_Vertical.kicad_mod
hardware/PinHeader_1x03_P2.54mm_Vertical_With_SolderJumper.kicad_mod
hardware/RelativelyUniversalROMProgrammer.kicad_pcb
hardware/RelativelyUniversalROMProgrammer.kicad_prl
hardware/RelativelyUniversalROMProgrammer.kicad_pro
hardware/RelativelyUniversalROMProgrammer.kicad_sch        ← Rev2.3 schematic (renamed from W27C512Programmer.kicad_sch)
hardware/RelativelyUniversalROMProgrammerRev2.3-back.jpg
hardware/RelativelyUniversalROMProgrammerRev2.3.jpg
hardware/RelativelyUniversalROMProgrammerRev2.3.pdf
hardware/Rev2.1/RURP-Rev2.1.zip                            ← Rev2.1 gerbers
hardware/Rev2.1/W27C512Programmer-top-pos.csv
hardware/Rev2.1/W27C512ProgrammerBOM.csv
hardware/Rev2.2/Rev2.2-gerbers.zip                         ← Rev2.2 gerbers
hardware/Rev2.2/W27C512Programmer-top-pos-jlc.csv
hardware/Rev2.2/W27C512Programmer-top-pos.csv
hardware/Rev2.2/W27C512Programmer.csv
hardware/Rev2.3/jlcpcb/production_files/BOM-RelativelyUniversalROMProgrammer.csv
hardware/Rev2.3/jlcpcb/production_files/CPL-RelativelyUniversalROMProgrammer.csv
hardware/Rev2.3/jlcpcb/production_files/GERBER-RelativelyUniversalROMProgrammer.zip
hardware/Rev2.3/jlcpcb/project.db
hardware/_autosave-RelativelyUniversalROMProgrammer.kicad_sch
hardware/fp-info-cache
hardware/r_network08-smd10.kicad_sym
hardware/rev2/W27C512Programmer-top-pos.csv
hardware/rev2/W27C512Programmerbom.csv
hardware/rev2/rev2-1316.zip                                ← Rev2 (pre-2.1) gerbers
```

---

## Pass 2 — Tag enumeration

Command: `git -C .planning/v1.7/upstream-rurp tag --sort=-creatordate`

Output:
```
(empty — no tags in the upstream repository)
```

**Finding:** Zero tags. The upstream repo uses branch-based version management, not tags. D-04's
"tag enumeration" pass returns empty output — this is itself a noteworthy finding (no semver tags).

---

## Pass 3 — Deletions from `main`

Command: `git -C .planning/v1.7/upstream-rurp log --all --diff-filter=D --pretty=format:'%h %ai %s' -- hardware/`

Output:
```
c2bd111 2025-06-24 13:15:42 +0200 Rev 2.3
28e0239 2024-10-17 11:35:22 +0200 Rev2
```

Per-file deletion detail:
```
COMMIT c2bd111 2025-06-24 13:15:42 +0200 Rev 2.3
hardware/UniversalProgrammerRev0b0.zip
hardware/UniversalProgrammerRev1b0.zip
hardware/W27C512Programmer-top-pos-Rev0.csv
hardware/W27C512Programmer.kicad_sch-bak
hardware/W27C512Programmer.pdf
hardware/W27C512ProgrammerBOM-Rev0.csv
hardware/W27C512ProgrammerBOM-Rev1.csv

COMMIT 28e0239 2024-10-17 11:35:22 +0200 Rev2
hardware/W27C512Programmer-bottom-pos.csv
hardware/W27C512Programmer.xml
hardware/W27C512ProgrammerBOM-Rev2.csv
hardware/rev2/Rev2-gerbers.zip
```

**Key finding:** `UniversalProgrammerRev0b0.zip` and `UniversalProgrammerRev1b0.zip` were DELETED from
`main` root in commit c2bd111 ("Rev 2.3", 2025-06-24). Prior to that commit, they lived at
`hardware/UniversalProgrammerRev0b0.zip` on main. The deletion provenance for Rev0 and Rev1 is
`removed-from-main` (D-02 terminology). Their `removed_commit` = `c2bd111`.

They still exist on the `origin/rev2.0` branch (confirmed in Pass 4) and on `origin/Rev2.1` branch.

---

## Pass 4 — Walk rev-named branches (case-insensitive `/rev[ -]?\d/i`)

Command: `git -C .planning/v1.7/upstream-rurp branch -r | grep -iE 'rev[ -]?[0-9]'`

Output:
```
  origin/Rev2.1
  origin/Rev2.3
  origin/rev2.0
```

### Per-branch `git ls-tree -r` output

#### origin/rev2.0
```
hardware/PinHeader_1x03_P2.54mm_Vertical.kicad_mod
hardware/PinHeader_1x03_P2.54mm_Vertical_With_SolderJumper.kicad_mod
hardware/UniversalProgrammerRev0b0.zip     ← Rev0 gerbers (blob 884ccf9f)
hardware/UniversalProgrammerRev1b0.zip     ← Rev1 gerbers (blob 82a425d4)
hardware/W27C512Programmer-top-pos-Rev0.csv
hardware/W27C512Programmer-top-pos-Rev1.csv
hardware/W27C512Programmer.kicad_pcb
hardware/W27C512Programmer.kicad_prl
hardware/W27C512Programmer.kicad_pro
hardware/W27C512Programmer.kicad_sch       ← Rev2.0 schematic (blob d2a7f691) — current working schematic on rev2.0 branch
hardware/W27C512Programmer.kicad_sch-bak
hardware/W27C512Programmer.pdf
hardware/W27C512Programmer.svg
hardware/W27C512ProgrammerBOM-Rev0.csv
hardware/W27C512ProgrammerBOM-Rev1.csv
hardware/fp-info-cache
hardware/r_network08-smd10.kicad_sym
hardware/rev2/W27C512Programmer-top-pos.csv
hardware/rev2/W27C512Programmerbom.csv
hardware/rev2/rev2-1316.zip               ← Rev2 (pre-2.1) gerbers (shared with main)
```

**Note:** Rev0 and Rev1 are NOT separate git revisions with their own `.kicad_sch` tracked directly —
they are zip archives containing gerbers + CSVs. The `W27C512Programmer.kicad_sch` on `rev2.0` is the
Rev2.0 working schematic, not Rev0 or Rev1.

#### origin/Rev2.1
```
hardware/PinHeader_1x03_P2.54mm_Vertical.kicad_mod
hardware/PinHeader_1x03_P2.54mm_Vertical_With_SolderJumper.kicad_mod
hardware/Rev2.1/RURP-Rev2.1.zip            ← Rev2.1 gerbers (blob e11aa0b5)
hardware/Rev2.1/W27C512Programmer-top-pos.csv
hardware/Rev2.1/W27C512ProgrammerBOM.csv
hardware/UniversalProgrammerRev0b0.zip     ← still present on Rev2.1 branch (same blob 884ccf9f)
hardware/UniversalProgrammerRev1b0.zip     ← still present on Rev2.1 branch (same blob 82a425d4)
hardware/W27C512Programmer-top-pos-Rev0.csv
hardware/W27C512Programmer.kicad_pcb
hardware/W27C512Programmer.kicad_pro
hardware/W27C512Programmer.kicad_sch       ← Rev2.1 schematic (blob f3b7a521) — key artifact
hardware/W27C512Programmer.kicad_sch-bak
hardware/W27C512Programmer.pdf
hardware/W27C512ProgrammerBOM-Rev0.csv
hardware/W27C512ProgrammerBOM-Rev1.csv
hardware/fp-info-cache
hardware/r_network08-smd10.kicad_sym
hardware/rev2/W27C512Programmer-top-pos.csv
hardware/rev2/W27C512Programmerbom.csv
hardware/rev2/rev2-1316.zip
```

**Rev 2.1 schematic found:** `hardware/W27C512Programmer.kicad_sch` (blob f3b7a521) on branch
`origin/Rev2.1`. This is the authoritative Rev2.1 KiCad schematic — NOT inside a zip.

#### origin/Rev2.3
```
hardware/PinHeader_1x03_P2.54mm_Vertical.kicad_mod
hardware/PinHeader_1x03_P2.54mm_Vertical_With_SolderJumper.kicad_mod
hardware/RelativelyUniversalROMProgrammer.kicad_pcb
hardware/RelativelyUniversalROMProgrammer.kicad_prl
hardware/RelativelyUniversalROMProgrammer.kicad_pro
hardware/RelativelyUniversalROMProgrammer.kicad_sch   ← Rev2.3 schematic (blob fe35bd78) — renamed from W27C512Programmer
hardware/RelativelyUniversalROMProgrammerRev2.3-back.jpg
hardware/RelativelyUniversalROMProgrammerRev2.3.jpg
hardware/RelativelyUniversalROMProgrammerRev2.3.pdf
hardware/Rev2.1/RURP-Rev2.1.zip
hardware/Rev2.1/W27C512Programmer-top-pos.csv
hardware/Rev2.1/W27C512ProgrammerBOM.csv
hardware/Rev2.2/Rev2.2-gerbers.zip                    ← Rev2.2 gerbers archived
hardware/Rev2.2/W27C512Programmer-top-pos-jlc.csv
hardware/Rev2.2/W27C512Programmer-top-pos.csv
hardware/Rev2.2/W27C512Programmer.csv
hardware/Rev2.3/jlcpcb/production_files/BOM-RelativelyUniversalROMProgrammer.csv
hardware/Rev2.3/jlcpcb/production_files/CPL-RelativelyUniversalROMProgrammer.csv
hardware/Rev2.3/jlcpcb/production_files/GERBER-RelativelyUniversalROMProgrammer.zip
hardware/Rev2.3/jlcpcb/project.db
hardware/_autosave-RelativelyUniversalROMProgrammer.kicad_sch
hardware/fp-info-cache
hardware/r_network08-smd10.kicad_sym
hardware/rev2/W27C512Programmer-top-pos.csv
hardware/rev2/W27C512Programmerbom.csv
hardware/rev2/rev2-1316.zip
```

---

## Pass 5 — All-refs fallback (rev-list across tags + remotes)

Command: `git -C .planning/v1.7/upstream-rurp log --all --source --pretty=format:'%h %S %s' -- hardware/ | head -80`

Output:
```
e615783 refs/remotes/origin/rev2.0 Add rev2 pdf schematics
7c8f262 refs/remotes/origin/Rev2.3 2716 / TMS2532 support
c2bd111 refs/remotes/origin/Rev2.3 Rev 2.3
545c824 refs/remotes/origin/Rev2.3 Merge pull request #14 from AndersBNielsen/Fused
a6fde57 refs/remotes/origin/Rev2.1 Plot PDF
234e836 refs/remotes/origin/Rev2.3 Merge pull request #11 from AndersBNielsen/Fused
50a6ea4 refs/remotes/origin/Rev2.1 Rev2.1
339f42d refs/remotes/origin/rev2.0 U5 changed to a socket part
f3c9ed0 refs/remotes/origin/Rev2.1 Fuse in schematic
28e0239 refs/remotes/origin/rev2.0 Rev2
a252e39 refs/remotes/origin/rev2.0 Rev2
220660e refs/remotes/origin/rev2.0 Power through address lines
e2032eb refs/remotes/origin/rev2.0 Fiddle with pin naming
beebd7a refs/remotes/origin/rev2.0 10k LED R
9fd07eb refs/remotes/origin/rev2.0 Change 4k7 to 10k R for green LEDs
e41329e refs/remotes/origin/rev2.0 Arduino sketch now successfully reads a ROM to serial.. Slowly.
9e126a7 refs/remotes/origin/rev2.0 Initial Arduino Firmware Prototype
b84e9e0 refs/remotes/origin/rev2.0 Rev1 PCB - Includes voltage divider on Arduino Analog Pin 2.
bbeffc6 refs/remotes/origin/rev2.0 Green LED's .. yes
486f3d1 refs/remotes/origin/rev2.0 Hardware release day update!
8b315d3 refs/remotes/origin/rev2.0 PCB probably somewhat complete
c0d37be refs/remotes/origin/rev2.0 Getting ready for PCB..
4ba4602 refs/remotes/origin/rev2.0 Working on a breadboard
```

**All-refs confirms:** No hidden orphaned commits. The three `origin/rev2.0`, `origin/Rev2.1`,
`origin/Rev2.3` refs cover the complete `hardware/` history. No Rev2.2 branch exists (Rev2.2
is only captured as an archived gerber zip on main + Rev2.3 branch).

---

## Zip-archive listings (Finding #2 — Rev0 + Rev1 live as inline zips)

### UniversalProgrammerRev0b0.zip (from rev2.0 branch + formerly on main root until c2bd111)

Extracted via: `git show origin/rev2.0:hardware/UniversalProgrammerRev0b0.zip | unzip -l /dev/stdin`

```
Archive:  UniversalProgrammerRev0b0.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
      293  2024-04-07 12:05   W27C512Programmer-NPTH.drl
     4525  2024-04-07 12:05   W27C512Programmer-PTH.drl
     2797  2024-04-07 12:04   W27C512Programmer-job.gbrjob
     1009  2024-04-07 12:04   W27C512Programmer-Edge_Cuts.gbr
     6854  2024-04-07 12:04   W27C512Programmer-B_Mask.gbr
    17948  2024-04-07 12:04   W27C512Programmer-F_Mask.gbr
    87150  2024-04-07 12:04   W27C512Programmer-B_Silkscreen.gbr
   104807  2024-04-07 12:04   W27C512Programmer-F_Silkscreen.gbr
      472  2024-04-07 12:04   W27C512Programmer-B_Paste.gbr
    12698  2024-04-07 12:04   W27C512Programmer-F_Paste.gbr
   342859  2024-04-07 12:04   W27C512Programmer-B_Cu.gbr
   461285  2024-04-07 12:04   W27C512Programmer-F_Cu.gbr
(plus __MACOSX/ entries)
---------                     -------
  1045337                     24 files
```

**Finding:** Rev0 zip contains ONLY gerbers — no `.kicad_sch` inside the zip. The Rev0 schematic
is the `W27C512Programmer.kicad_sch` at the git object level on `origin/rev2.0` (living outside
the zip). Gerber date: 2024-04-07.

### UniversalProgrammerRev1b0.zip (from rev2.0 branch + formerly on main root until c2bd111)

```
Archive:  UniversalProgrammerRev1b0.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
      294  2024-04-30 07:59   W27C512Programmer-NPTH.drl
     4595  2024-04-30 07:59   W27C512Programmer-PTH.drl
     2797  2024-04-30 07:59   W27C512Programmer-job.gbrjob
     1009  2024-04-30 07:59   W27C512Programmer-Edge_Cuts.gbr
     6854  2024-04-30 07:59   W27C512Programmer-B_Mask.gbr
    18165  2024-04-30 07:59   W27C512Programmer-F_Mask.gbr
    86800  2024-04-30 07:59   W27C512Programmer-B_Silkscreen.gbr
   107757  2024-04-30 07:59   W27C512Programmer-F_Silkscreen.gbr
      472  2024-04-30 07:59   W27C512Programmer-B_Paste.gbr
    12915  2024-04-30 07:59   W27C512Programmer-F_Paste.gbr
   344269  2024-04-30 07:59   W27C512Programmer-B_Cu.gbr
   463535  2024-04-30 07:59   W27C512Programmer-F_Cu.gbr
---------                     -------
  1049462                     12 files
```

**Finding:** Rev1 zip contains ONLY gerbers — no `.kicad_sch`. Rev1 gerber date: 2024-04-30.
Rev1 commit note: "Includes voltage divider on Arduino Analog Pin **2**" (A2, not A3!).
The A3-ADC scheme came later in the Rev2 → Rev2.x lineage.

### rev2-1316.zip (from hardware/rev2/ on main + rev2.0 + Rev2.1 + Rev2.3 branches)

```
Archive:  rev2-1316.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
   236264  2024-10-11 11:15   W27C512Programmer-B_Cu.gbr
     4640  2024-10-11 11:15   W27C512Programmer-B_Mask.gbr
      460  2024-10-11 11:15   W27C512Programmer-B_Paste.gbr
   173202  2024-10-11 11:15   W27C512Programmer-B_Silkscreen.gbr
      997  2024-10-11 11:15   W27C512Programmer-Edge_Cuts.gbr
   336666  2024-10-11 11:15   W27C512Programmer-F_Cu.gbr
    17912  2024-10-11 11:15   W27C512Programmer-F_Mask.gbr
    14725  2024-10-11 11:15   W27C512Programmer-F_Paste.gbr
   218996  2024-10-11 11:15   W27C512Programmer-F_Silkscreen.gbr
     2791  2024-10-11 11:15   W27C512Programmer-job.gbrjob
      269  2024-10-11 11:16   W27C512Programmer-NPTH.drl
     4779  2024-10-11 11:16   W27C512Programmer-PTH.drl
(plus __MACOSX/ entries)
---------                     -------
  1013657                     24 files
```

**Finding:** Rev2 (pre-2.1, denominated "rev2" lowercase) gerbers dated 2024-10-11. This is the
early "Rev2" hardware released before Rev2.1 designation. The `hardware/rev2/` subdir is a
deprecated dump — the gerbers predate the Rev2.1 introduction commit (50a6ea4, 2024-12-20).

### RURP-Rev2.1.zip (from hardware/Rev2.1/ on main + Rev2.1 + Rev2.3 branches)

```
Archive:  RURP-Rev2.1.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
     4997  2024-12-02 10:14   W27C512Programmer-PTH.drl
   257924  2024-12-02 10:14   W27C512Programmer-B_Cu.gbr
     5065  2024-12-02 10:14   W27C512Programmer-B_Mask.gbr
      460  2024-12-02 10:14   W27C512Programmer-B_Paste.gbr
   195368  2024-12-02 10:14   W27C512Programmer-B_Silkscreen.gbr
      199  2024-12-02 10:14   W27C512Programmer-bottom-pos.csv
      997  2024-12-02 10:14   W27C512Programmer-Edge_Cuts.gbr
   337672  2024-12-02 10:14   W27C512Programmer-F_Cu.gbr
    18023  2024-12-02 10:14   W27C512Programmer-F_Mask.gbr
    14841  2024-12-02 10:14   W27C512Programmer-F_Paste.gbr
   218918  2024-12-02 10:14   W27C512Programmer-F_Silkscreen.gbr
     2791  2024-12-02 10:14   W27C512Programmer-job.gbrjob
      269  2024-12-02 10:14   W27C512Programmer-NPTH.drl
(plus __MACOSX/ entries)
---------                     -------
  1059743                     26 files
```

**Finding:** Rev2.1 gerbers dated 2024-12-02 (committed to git 2024-12-20 in `50a6ea4`).
No `.kicad_sch` inside the zip — just gerbers + BOM CSV. The schematic lives as a tracked
git object `hardware/W27C512Programmer.kicad_sch` (blob f3b7a521) on `origin/Rev2.1` branch.

### Rev2.2-gerbers.zip (from hardware/Rev2.2/ on main + Rev2.3 branch)

```
Archive:  Rev2.2-gerbers.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
     4910  2025-04-28 19:09   W27C512Programmer-PTH.drl
   259810  2025-04-28 19:09   W27C512Programmer-B_Cu.gbr
     5099  2025-04-28 19:09   W27C512Programmer-B_Mask.gbr
      460  2025-04-28 19:09   W27C512Programmer-B_Paste.gbr
   197098  2025-04-28 19:09   W27C512Programmer-B_Silkscreen.gbr
      997  2025-04-28 19:09   W27C512Programmer-Edge_Cuts.gbr
   329623  2025-04-28 19:09   W27C512Programmer-F_Cu.gbr
    18391  2025-04-28 19:09   W27C512Programmer-F_Mask.gbr
    15185  2025-04-28 19:09   W27C512Programmer-F_Paste.gbr
   226437  2025-04-28 19:09   W27C512Programmer-F_Silkscreen.gbr
     2791  2025-04-28 19:09   W27C512Programmer-job.gbrjob
      269  2025-04-28 19:09   W27C512Programmer-NPTH.drl
(plus __MACOSX/ entries)
---------                     -------
  1063026                     24 files
```

**Finding:** Rev2.2 gerbers dated 2025-04-28 (the date in CHAT-INTEL when Anders mentioned "10k
version resistor for Rev 2.2"). COMMITTED to git in c2bd111 (2025-06-24 — Rev2.3 commit).
No `.kicad_sch` inside the zip — only gerbers. The Rev2.2 schematic was the working
`hardware/W27C512Programmer.kicad_sch` (blob f3b7a521 — SAME blob as Rev2.1!).

**Gerber silkscreen header for Rev2.2:** `%TF.ProjectId,W27C512Programmer,...,rev?*%`
(no rev number set in the Rev2.2 gerber header — operator's silkscreen photos will be needed
for the verbatim silkscreen string per SILK-01). Gerber presence of R41 and JP4 confirmed:
`%TO.C,R41*%` and `%TO.C,JP4*%` appear in `W27C512Programmer-F_Silkscreen.gbr`.

---

## Per-rev R41 / JP4 / A3 grep (for §3 Existing Detect-HW Scheme fill in Plan 05)

Schematic files were extracted from git objects to `/tmp/rurp-extract/` and grepped.
Note: `/tmp/` is not committed; paths below reference git blobs for reproducibility.

### Rev 2.0 (branch: origin/rev2.0 — `hardware/W27C512Programmer.kicad_sch`, blob d2a7f691)

Schematic line counts: 25,552 lines

```
R41 at lines 17520, 17581
JP4 at lines 21311, 21363
A3  at lines 4025, 4280, 12338, 12368 (address bus label "A3" + ADC net label "A3")
```

R41 value: **`4k7`** (4.7kΩ) — line 17528: `(property "Value" "4k7"`
JP4 value: `P1_VPP_JMP` (2-pin VPP jumper) — line 21319: `(property "Value" "P1_VPP_JMP"`
ADC pin: A3 label present in schematic
Notes: R41 was already present in Rev2.0 working schematic. The Rev2.0 branch is the active
development branch that became Rev2.1. R41 first appeared in the schematic at commit a252e39
("Rev2", 2024-10-08) which is an ancestor of the rev2.0 branch tip.

### Rev 2.1 (branch: origin/Rev2.1 — `hardware/W27C512Programmer.kicad_sch`, blob f3b7a521)

Schematic line counts: 26,675 lines

```
R41 at lines 18232, 18293
JP4 at lines 22300, 22352
A3  at lines 3959, 5113, 12888, 12932
```

R41 value: **`4k7`** (4.7kΩ) — line 18240: `(property "Value" "4k7"`
JP4 value: `P1_VPP_JMP` (1x2 pin VPP jumper) — footprint: `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical`
ADC pin: A3 label present (same UUIDs as Rev2.0 labels — likely derived from same project)
Notes: Rev2.1 schematic blob f3b7a521 is also the blob at `hardware/W27C512Programmer.kicad_sch`
in the parent of Rev2.3 introduction (b0ec7d7) — confirming Rev2.2 used the SAME schematic as
Rev2.1 (unchanged between Rev2.1 and Rev2.2).

### Rev 2.2 (no standalone branch — archived as Rev2.2-gerbers.zip; schematic = Rev2.1 blob f3b7a521)

Rev2.2 schematic MD5: identical to Rev2.1 (confirmed: `md5sum` outputs match).
Rev2.2 schematic file: was `hardware/W27C512Programmer.kicad_sch` on main before c2bd111 (Rev2.3 commit).

R41 value: **`4k7`** (same as Rev2.1, same blob)
JP4 value: `P1_VPP_JMP` (same as Rev2.1)
ADC pin: A3 (same)

**DISCREPANCY FLAG for Plan 05:** CHAT-INTEL §1 records Anders stating "10k version resistor for
Rev 2.2" (2025-04-28). The Rev2.2-gerbers.zip is dated 2025-04-28 (same day). BUT the schematic
blob for Rev2.2 (W27C512Programmer.kicad_sch at b0ec7d7) shows R41 = 4k7, not 10k. The 10k value
only appears in the Rev2.3 schematic (introduced c2bd111, 2025-06-24). Possible explanations:
(a) Anders committed the "10k" gerbers for Rev2.2 but never updated the schematic to match;
(b) The "10k" value in the chat referred to an intent that was deferred to Rev2.3;
(c) The Rev2.2-gerbers.zip (dated 2025-04-28) represents a schematic state NOT committed to git
(local KiCad work). This discrepancy MUST be resolved in Plan 05 §3 fill.

### Rev 2.3 (branch: origin/Rev2.3 AND main — `hardware/RelativelyUniversalROMProgrammer.kicad_sch`, blob fe35bd78)

Main branch and Rev2.3 branch share the same blob (MD5 match confirmed). Schematic renamed
from `W27C512Programmer.kicad_sch` → `RelativelyUniversalROMProgrammer.kicad_sch` in c2bd111.

Schematic line counts: 28,007 lines (both blobs identical)

```
R41 at lines 20582, 20645
JP4 at lines 2941 (pin ref in symbol def), 22562, 22617
A3  at lines 3644, 4798, 12619, 12663
```

R41 value: **`10k`** (10kΩ) — line 20591: `(property "Value" "10k"`
JP4 value: `P1_VPP_JMP` (2x2 pin VPP jumper in Rev2.3) — footprint changed to
`Connector_PinHeader_2.54mm:PinHeader_2x02_P2.54mm_Vertical` (from 1x2 in Rev2.1/2.2)
ADC pin: A3 (same label UUIDs as Rev2.1/2.0)
Schematic title block: `(rev "2.3")`, company "Anders Nielsen"
Notes: Rev2.3 is confirmed schematic-only change from Rev2.2's perspective (Anders stated
"silkscreen-only diff" per CHAT-INTEL 2026-07-03 — but the schematic shows R41 value CHANGED
from 4k7 to 10k AND JP4 footprint changed from 1x2 to 2x2 header. This is more than silkscreen.
Plan 05 should flag this for Phase 32 diff analysis.)

---

## Key schematic blobs (for git show reproducibility)

| Rev | Branch | Path | Blob SHA | Lines |
|-----|--------|------|----------|-------|
| Rev2.0 working | origin/rev2.0 | `hardware/W27C512Programmer.kicad_sch` | d2a7f691 | 25,552 |
| Rev2.1 | origin/Rev2.1 | `hardware/W27C512Programmer.kicad_sch` | f3b7a521 | 26,675 |
| Rev2.2 (= Rev2.1 blob) | main (at b0ec7d7) | `hardware/W27C512Programmer.kicad_sch` | f3b7a521 | 26,675 |
| Rev2.3 / main | origin/Rev2.3 + main | `hardware/RelativelyUniversalROMProgrammer.kicad_sch` | fe35bd78 | 28,007 |

---

## Findings summary (for Plan 05 consumption)

| Rev | Provenance | State | Introduced commit (SHA) | Removed commit | Schematic path | Gerber path | Photo dir | Notes |
|-----|------------|-------|--------------------------|----------------|----------------|-------------|-----------|-------|
| (silkscreen TBD — plan 03 photos) | on-main | on-hand-photographed | c2bd111 (Rev 2.3, 2025-06-24) | — | `hardware/RelativelyUniversalROMProgrammer.kicad_sch` (blob fe35bd78) | `hardware/Rev2.3/jlcpcb/production_files/GERBER-RelativelyUniversalROMProgrammer.zip` | — | Rev2.3; silkscreen-only diff per Anders CHAT-INTEL; MINE shows R41 4k7→10k AND JP4 1x2→2x2 change (more than silkscreen); upstream-only (operator doesn't own one); state=upstream-only |
| (silkscreen TBD — plan 03 photos) | on-main | on-hand-photographed | c2bd111 (Rev 2.3, 2025-06-24) | — | `hardware/W27C512Programmer.kicad_sch` (blob f3b7a521 — same as Rev2.1) | `hardware/Rev2.2/Rev2.2-gerbers.zip` (gerber date 2025-04-28) | `.planning/v1.7/photos/rev-2-2/` | Rev2.2; no standalone schematic; schematic blob = Rev2.1; DISCREPANCY: CHAT says 10k but schematic/gerber shows 4k7 |
| (silkscreen TBD — plan 03 photos) | on-main | on-hand-photographed | 50a6ea4 (Rev2.1, 2024-12-20) | — | `hardware/Rev2.1/` → `RURP-Rev2.1.zip` (gerbers); schematic at `hardware/W27C512Programmer.kicad_sch` (blob f3b7a521) on `origin/Rev2.1` | `hardware/Rev2.1/RURP-Rev2.1.zip` | — | Rev2.1; R41=4k7; JP4=P1_VPP_JMP (1x2); R41 introduced in Oct 2024 (a252e39), predates Rev2.1 commit; upstream-only (operator doesn't own one) |
| not-recovered | on-main (hardware/rev2/ lowercase) | upstream-only | 28e0239 (Rev2, 2024-10-17) | — | inside `hardware/rev2/rev2-1316.zip` (gerbers only, 2024-10-11) | `hardware/rev2/rev2-1316.zip` | — | Pre-Rev2.1 "rev2" dump; deprecated; R41 already in schematic at a252e39 (ancestor); schematic blob not identified separately from rev2.0 working sch |
| not-recovered | branch-archived:origin/rev2.0 (removed from main c2bd111) | upstream-only | b84e9e0 (Rev1 PCB, 2024-04-30) | c2bd111 (2025-06-24) | `UniversalProgrammerRev1b0.zip` (gerbers only) + BOM CSVs | `hardware/UniversalProgrammerRev1b0.zip` (blob 82a425d4) | — | Rev1; voltage divider on A2 (not A3); R41 designator NOT present in Rev1 era; removed from main at c2bd111 |
| not-recovered | branch-archived:origin/rev2.0 (removed from main c2bd111) | upstream-only | 486f3d1 (Hardware release day, 2024-04-18) or 8b315d3 (2024-04-01) | c2bd111 (2025-06-24) | `UniversalProgrammerRev0b0.zip` (gerbers only — no .kicad_sch in zip) | `hardware/UniversalProgrammerRev0b0.zip` (blob 884ccf9f) | — | Rev0; gerbers only in zip; schematic was `W27C512Programmer.kicad_sch` on rev2.0 branch (not inside zip); no R41 in pre-Rev2 schematic era |
| (silkscreen TBD — plan 05) | n/a — operator board derived from Rev0 | on-hand-photographed | n/a | — | Cross-refs to `hardware/UniversalProgrammerRev0b0.zip` (gerbers) + `hardware/W27C512Programmer.kicad_sch` (blob d2a7f691 on origin/rev2.0) | n/a | `.planning/v1.7/photos/rev-0-modified/` (Plan 05) | Modified Rev0 with hardware-bug-A/B rework; operator's third board; row populated by Plan 05 after photo session |

---

## Additional Key Findings for Plan 05

### Finding A: No tags, branch-based versioning only
The upstream repo has zero git tags. Version management is entirely through rev-named branches
(`rev2.0`, `Rev2.1`, `Rev2.3`). Note: NO `Rev2.2` branch exists — Rev2.2 is only captured as
`Rev2.2-gerbers.zip` archived in the `Rev 2.3` commit (c2bd111).

### Finding B: R41 was introduced in Rev2 (Oct 2024), NOT Rev2.1 (Dec 2024)
Commit `a252e39` (2024-10-08, "Rev2") is the first commit where `R41` appears in
`hardware/W27C512Programmer.kicad_sch`. This CONTRADICTS CHAT-INTEL §1 attribution of R41
introduction to Rev2.1. The correct attribution: R41 first appeared in "Rev2" (the pre-2.1
PCB redesign, Oct 2024), using ADC pin A3 from the start.

### Finding C: R41 value discrepancy — 4k7 (Rev2.0–Rev2.2) vs 10k (Rev2.3)
- Rev2.0 working schematic (blob d2a7f691): R41 = 4k7
- Rev2.1 schematic (blob f3b7a521): R41 = 4k7
- Rev2.2 schematic (= Rev2.1 blob f3b7a521): R41 = 4k7
- Rev2.3 schematic (blob fe35bd78): R41 = **10k**
CHAT-INTEL §1: "10k version resistor for Rev 2.2" (Anders, 2025-04-28). The git evidence
shows the 10k was introduced in Rev2.3, not Rev2.2. Either the gerbers diverged from the
committed schematic, or the chat statement was forward-looking / the change was deferred.
Plan 05 §3 must note this discrepancy explicitly.

### Finding D: JP4 footprint changed Rev2.1→Rev2.3
- Rev2.1/2.2: JP4 footprint = `PinHeader_1x02_P2.54mm_Vertical` (1×2 pin)
- Rev2.3: JP4 footprint = `PinHeader_2x02_P2.54mm_Vertical` (2×2 pin)
This is not a "silkscreen-only" change — it's a physical connector change. Plan 05 should
flag this for Phase 32 mechanical diff.

### Finding E: Rev2.2 has no standalone .kicad_sch in git
Rev2.2 schematic was never committed as a discrete file in a `hardware/Rev2.2/` subdir.
The Rev2.2 "state" is: working schematic = Rev2.1 blob (f3b7a521) + gerbers in
`Rev2.2-gerbers.zip` (dated 2025-04-28). No `kicad_sch` inside the gerber zip.

### Finding F: Rev2.3 not silkscreen-only (despite CHAT-INTEL claim)
CHAT-INTEL records Anders saying Rev2.3 is "silkscreen-only diff vs Rev2.2." The schematic
diff shows: (1) R41 value 4k7 → 10k; (2) JP4 footprint 1x2 → 2x2; (3) schematic file renamed.
This is a substantive schematic change, not silkscreen-only. Phase 32 diff should document this.

### Finding G: Rev1 used A2 not A3
Commit b84e9e0 ("Rev1 PCB — Includes voltage divider on Arduino Analog Pin 2.") confirms
the ADC detect scheme was on pin A2 in Rev1. The migration to A3 happened somewhere in the
Rev2 era. R41 designator does not appear in the pre-Rev2 schematic history.
