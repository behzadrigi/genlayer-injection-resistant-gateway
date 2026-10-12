# Tests: IntegrityIncidentLedger

| Network | Address | Scanner it reads |
|---|---|---|
| Studionet | `0x950b551B18B31a79F3B4b3fDB89e2E7f2509a91D` | `0xc3D1e6967c71e647Cb3dA6465293c0FaE3D31931` |
| Bradbury | `0xF98F693eFe5Ccbc5885BBa3dBc23Dcde20e291d6` | `0x08101A9c188dB1737E231C25b5E641df92A3A3fD` |

Status legend: **RUN** has transaction evidence in [TEST.md](../TEST.md) (S = Studio). **DEFINED** is a ready test case that has not been run on these deployments.

| ID | Case | Steps | Expected | Status |
|---|---|---|---|---|
| LG-1 | A SUSPICIOUS source is logged | `record_incident(URL_B)` | Incident id 0, `status = LOGGED` | RUN (S8) |
| LG-2 | An incident is logged once | `record_incident(URL_B)` again | Rejected: `Already logged` | RUN (S8) |
| LG-3 | A SAFE source cannot be logged | `record_incident(URL_A_V2)` | Rejected: `Only SUSPICIOUS sources can be logged as incidents` | DEFINED |
| LG-4 | An unscanned source cannot be logged | `record_incident("https://example.com/never-scanned")` | Rejected: `Source has not been scanned yet` | DEFINED |
| LG-5 | Incident data | `get_incident_data(0)` | `source_url` is URL_B, `scan_requester` is the scanning account, `reported_by` is the caller | DEFINED |
