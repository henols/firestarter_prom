<p align="left"><img src="https://raw.githubusercontent.com/henols/firestarter_app/refs/heads/main/images/firestarter_logo.png" alt="Firestarter EPROM Programmer" width="200"></p>

# Firestarter

**An EPROM programmer built from an Arduino and the RURP shield.**

It reads, writes, erases and verifies EPROM, EEPROM, Flash and SRAM chips —
the 24, 28 and 32-pin parallel DIP parts found in arcade boards, home
computers, synthesisers and industrial equipment from the 1980s and 1990s.
746 chips across 59 manufacturers are in its database.

If you have a vintage board with a socketed ROM on it, this is a way to read
that chip, keep a copy, and put a new one back.

## Getting started

**→ [Start here](https://github.com/henols/firestarter_prom/wiki)** — what you
need, how to install it, and how to read your first chip.

## Documentation

Everything lives in the [wiki](https://github.com/henols/firestarter_prom/wiki):

- [Programming Protocols](https://github.com/henols/firestarter_prom/wiki/Programming-Protocols) — how each chip family is driven, and which chips each one covers
- [Pin Maps](https://github.com/henols/firestarter_prom/wiki/Pin-Maps) — pin maps for every supported family, and the DIP24 adapter
- [Chip Database Fields](https://github.com/henols/firestarter_prom/wiki/Chip-Database-Fields) — what the database records about each chip
- [Shield Revisions](https://github.com/henols/firestarter_prom/wiki/Shield-Revisions) — telling the RURP shield revisions apart
- [Lockable PROMs](https://github.com/henols/firestarter_prom/wiki/Lockable-PROMs) — which flash families can report write protection
- [Testing Chips](https://github.com/henols/firestarter_prom/wiki/Testing-Chips) — checking a chip against real hardware and reporting what happened

## The repositories

| Repository | What it is |
|---|---|
| **firestarter_prom** (this one) | The project hub — documentation wiki and the issue tracker for all three repositories |
| [firestarter](https://github.com/henols/firestarter) | The AVR firmware that runs on the Arduino and drives the chip |
| [firestarter_app](https://github.com/henols/firestarter_app) | The `firestarter` command you run on your computer |

The two are used together and are versioned in lockstep — the CLI installs the
matching firmware for you.

## Reporting a problem

**[Open an issue here](https://github.com/henols/firestarter_prom/issues)**,
whichever part it concerns. The firmware and CLI repositories do not have their
own trackers.

If a chip did not work, say which chip, which board, and include everything the
command printed — see [Testing Chips](https://github.com/henols/firestarter_prom/wiki/Testing-Chips).
