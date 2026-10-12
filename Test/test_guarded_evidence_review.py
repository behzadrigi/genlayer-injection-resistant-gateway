# Tests: GuardedEvidenceReview

| Network | Address | Scanner it reads |
|---|---|---|
| Studionet | `0xb49FE31694887FE0F1bBfCbcaf4F9324650e5Cf9` | `0xc3D1e6967c71e647Cb3dA6465293c0FaE3D31931` |
| Bradbury | `0x4C88A5Cc5CC05fE405827e07bB42e1CB460D2186` | `0x08101A9c188dB1737E231C25b5E641df92A3A3fD` |

Status legend: **RUN** has transaction evidence in [TEST.md](../TEST.md) (S = Studio, B = Bradbury). **DEFINED** is a ready test case that has not been run on these deployments.

| ID | Case | Steps | Expected | Status |
|---|---|---|---|---|
| RV-1 | Claim is bound to the scan digest | `submit_claim(CLAIM, URL_A_V2)`, `get_claim_data(id)` | `source_hash` equals the scan `content_hash`, `status = PENDING` | RUN (S2, B2) |
| RV-2 | Review succeeds on unchanged content | `review_claim(id)` | `content_hash_matches = true`, `verdict = SUPPORTED`, `status = REVIEWED` | RUN (S3, B2) |
| RV-3 | Page changed after the scan is refused | Submit a claim, edit the gist to the tamper text, `review_claim(id)` | Rejected: `Source content changed since scan - cannot review under stale scan`; `get_claim_status` stays `PENDING` | RUN (S4, B3) |
| RV-4 | Injection added after the scan is refused | Edit the gist to the injection text, `review_claim(id)` | Same rejection; a new `scan_source` of the URL is rejected with `Already scanned` | RUN (S5) |
| RV-5 | Restoring the content restores review | Restore the original text, submit a new claim, `review_claim` | `content_hash_matches = true`, `SUPPORTED` | RUN (S6) |
| RV-6 | A SUSPICIOUS source cannot be used | `submit_claim("Any claim here", URL_B)` | Rejected: `Source failed the integrity scan - cannot use as evidence` | RUN (S8) |
| RV-7 | An unscanned source cannot be used | `submit_claim(CLAIM, "https://example.com/never-scanned")` | Rejected: `Source has not been integrity-scanned yet` | DEFINED |
| RV-8 | A claim is reviewed once | `review_claim` on a REVIEWED claim | Rejected: `Already reviewed` | DEFINED |
| RV-9 | Empty claim | `submit_claim("", URL_A_V2)` | Rejected: `Claim cannot be empty` | DEFINED |
