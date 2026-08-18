# Validated EPROMs

Chips whose community `dev test` sweep passed every applicable step. One row per
closed issue. Appended by the `devtest-triage` skill.

`Firmware` is `not reported` where the report's `auto_capture.fw_board_identity` was
null — the host cannot read the firmware prerelease suffix, so it is not inferred from
the host version.

| Chip | Protocol | Pinout | Size | Host | Firmware | Issue | Closed |
|------|----------|--------|------|------|----------|-------|--------|
| fm1608 | 0x28 | DIP28_JEDEC_SRAM_8K | 0x2000 | 3.0.0b11 | not reported | #18 | 2026-08-08 |
| sst39sf020 | 0x06 | DIP32_SST39SF040 | 0x40000 | 3.0.0b15 | not reported | #25 | 2026-08-08 |
