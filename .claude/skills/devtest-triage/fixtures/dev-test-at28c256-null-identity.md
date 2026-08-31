<!-- FROZEN FIXTURE — devtest-triage skill-render verification (147-06). Do NOT regenerate this body from a live `to_dict()` output: this pins the gh#21/#32 half-answer shape (`fw_board_identity: null`, schema_version "1.2", host_version "3.0.0b15") that a current host build can no longer produce (F-01's fix makes fw_board_identity populate). Exercises the identity marker and the not-attributable clause; `hw_revision` is deliberately populated so this fixture does NOT also exercise the revision-marker path, keeping the two independently observable. -->

| Step | Verdict | Reason |
| ---- | ------- | ------ |
| id | NA | no chip-id in DB entry |
| read | OK | - |
| blank-check | BAD | - |
| write | BAD | - |
| verify | BAD | - |
| erase | NA | protocol 0x0D (28C family) has no erase operation; each page ... |

```json
{
  "schema_version": "1.2",
  "generated": "2026-08-07T12:07:39Z",
  "auto_capture": {
    "host_version": "3.0.0b15",
    "fw_board_identity": null,
    "hw_revision": "Rev 2.0-class, Override HW: Rev 2.3",
    "chip": "at28c256",
    "protocol": "0x0D",
    "chip_id_expected": null,
    "chip_id_actual": null,
    "chip_id_mismatch_reason": null
  },
  "transport_health": {
    "cobs_errors": "not measured",
    "crc_failures": "not measured",
    "retries": "not measured",
    "timeouts": "not measured",
    "transport_suspect": false
  },
  "steps": [
    {
      "op": "id",
      "verdict": "NA",
      "reason": "no chip-id in DB entry",
      "error_code": null,
      "fingerprint": null
    },
    {
      "op": "read",
      "verdict": "OK",
      "reason": "",
      "error_code": null,
      "fingerprint": null
    },
    {
      "op": "blank-check",
      "verdict": "BAD",
      "reason": "",
      "error_code": null,
      "fingerprint": null
    },
    {
      "op": "write",
      "verdict": "BAD",
      "reason": "",
      "error_code": null,
      "fingerprint": null
    },
    {
      "op": "verify",
      "verdict": "BAD",
      "reason": "",
      "error_code": null,
      "fingerprint": null
    },
    {
      "op": "erase",
      "verdict": "NA",
      "reason": "protocol 0x0D (28C family) has no erase operation; each page ...",
      "error_code": null,
      "fingerprint": null
    }
  ],
  "banner": {
    "n_ran": 3,
    "m_applicable": 3,
    "locked_steps": []
  },
  "voltage": {
    "vpp_before_mv": 11800,
    "vpp_after_mv": 11800,
    "vpe_before_mv": 13700,
    "vpe_after_mv": 13700,
    "vpp_mv": 11800,
    "vpe_mv": 13700
  },
  "is_submittable": true,
  "dedup_fingerprint": "00e121446ceb",
  "db_diff": {
    "current_support_status": "supported",
    "proposed_disposition": "suggests: candidate for community-fail (advisory)",
    "ladder_state": "community-fail"
  }
}
```
