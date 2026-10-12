# Tests: IntegrityIncidentLedger

| Network | Address | Scanner it reads |
|---|---|---|
| Studionet | `0x950b551B18B31a79F3B4b3fDB89e2E7f2509a91D` | `0xc3D1e6967c71e647Cb3dA6465293c0FaE3D31931` |
| Bradbury | `0xF98F693eFe5Ccbc5885BBa3dBc23Dcde20e291d6` | `0x08101A9c188dB1737E231C25b5E641df92A3A3fD` |

Status legend: **RUN** means the case was executed and the transaction evidence is listed below and in [TEST.md](../TEST.md) (S = Studio). **DEFINED** means a ready test case that has not been run on these deployments. The ledger has no Bradbury tests yet.

## Test inputs

- `URL_B` (poisoned gist, scanned SUSPICIOUS): `https://gist.githubusercontent.com/behzadrigi/4a03df8a9f79bc88e4a302b5263f793a/raw`
- `URL_A_V2` (benign gist, scanned SAFE): `https://gist.githubusercontent.com/behzadrigi/4d29c99d2a7c47b5bbf98f4796b65a72/raw`

## Test cases

| ID | Case | Steps | Expected | Status |
|---|---|---|---|---|
| LG-1 | A SUSPICIOUS source is logged | `record_incident(URL_B)` | Incident id 0, `status = LOGGED` | RUN (S8) |
| LG-2 | An incident is logged once | `record_incident(URL_B)` again | Rejected: `Already logged` | RUN (S8) |
| LG-3 | A SAFE source cannot be logged | `record_incident(URL_A_V2)` | Rejected: `Only SUSPICIOUS sources can be logged as incidents` | DEFINED |
| LG-4 | An unscanned source cannot be logged | `record_incident("https://example.com/never-scanned")` | Rejected: `Source has not been scanned yet` | DEFINED |
| LG-5 | Incident data | `get_incident_data(0)` | `source_url` is URL_B, `scan_requester` is the scanning account, `reported_by` is the caller | DEFINED |
| LG-6 | Incident listing | `list_incidents()` | One incident after LG-1 | DEFINED |

## Evidence for the RUN cases

Explorer link: `https://explorer-studio.genlayer.com/tx/<hash>`.

### LG-1: SUSPICIOUS source logged

- Studio (S8): `record_incident(URL_B)`, tx `0x16391a654c429bce2746f5e7378c4665176e85e2d6e1a80135261572544eb67e`, incident id 0. The source had been scanned SUSPICIOUS by tx `0x9b393c5fcf10d775ffe8042b1164fa76427dee6b678a04b9d5688a8c5c45ce6c`.

### LG-2: logged once

- Studio (S8): `record_incident(URL_B)` again, tx `0x1079029065e2f1329b16b44d81602706a92bfd4f2ec4f5ac7e4194be4bbe70c6`, rejected with `Already logged`.
