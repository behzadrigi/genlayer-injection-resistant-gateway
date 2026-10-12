# Tests: CrossSourceCorroboration

| Network | Address | Review contract it reads |
|---|---|---|
| Studionet | `0xec1b55703BD3ba898a62a236d4DfdC7Db188D71B` | `0xb49FE31694887FE0F1bBfCbcaf4F9324650e5Cf9` |
| Bradbury | `0x11F54DA78390FE47A1072CB036A89732933274b8` | `0x4C88A5Cc5CC05fE405827e07bB42e1CB460D2186` |

This contract's logic is unchanged in this revision. It was exercised in the first test round on the previous deployment, and it is deployed with the same source on both networks. The cases below are defined for the current deployments.

On Studio, claim 2 and claim 5 are REVIEWED and use the same domain, and claim 4 is still PENDING. On Bradbury, claim 0 is REVIEWED and claim 1 is PENDING.

Status legend: **DEFINED** is a ready test case that has not been run on these deployments.

| ID | Case | Steps (Studio ids) | Expected | Status |
|---|---|---|---|---|
| CO-1 | The two ids must differ | `corroborate(2, 2)` | Rejected: `Must provide two distinct claim ids` | DEFINED |
| CO-2 | Both claims must be reviewed | `corroborate(2, 4)` | Rejected: `Claim B has not been reviewed yet` | DEFINED |
| CO-3 | Sources must be on different domains | `corroborate(2, 5)` | Rejected: `Sources must come from independent domains` | DEFINED |
| CO-4 | Unknown claim | `corroborate(2, 99)` | Rejected: `Claim B not found` | DEFINED |
| CO-5 | Two domains corroborate | Scan a second source on a different domain (for example a Wikipedia page about the Eiffel Tower) as SAFE, submit and review the same claim text against it, then `corroborate(2, <new id>)` | `status = CORROBORATED`, the two domains differ in `get_corroboration_data` | DEFINED |
| CO-6 | A pair is used once | Repeat the call from CO-5 | Rejected: `This pair has already been corroborated` | DEFINED |
