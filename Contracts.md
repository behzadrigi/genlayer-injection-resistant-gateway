# Contracts

## 1. SourceIntegrityScanner

**Pattern:** non-deterministic, Equivalence Principle consensus with strict
equality on a two-way label (`SAFE` or `SUSPICIOUS`).

**Purpose:** fetches a URL with `gl.nondet.web.render(url, mode='text')` and
asks one narrow question: does this text try to instruct or manipulate a
language model that reads it? It does not judge any claim.

**Public methods:** `scan_source`, `get_scan_status`, `get_scan_data`,
`list_scans`.

**Safety properties**
- A URL can be scanned only once (`Already scanned`). The key is the
  normalized URL (http upgraded to https, trailing slash and query string
  removed).
- A page that returns no readable text is classified SUSPICIOUS, never SAFE.
- Validators each fetch and classify the page themselves and must reach the
  exact same label.
- `get_scan_status` returns `NOT_SCANNED` for unknown URLs, so downstream
  contracts can tell "never scanned" apart from "scanned and safe".

## 2. GuardedEvidenceReview

**Pattern:** non-deterministic, strict equality on `SUPPORTED` or
`UNSUPPORTED`.

**Purpose:** judges whether a source supports a claim, but only after the
source passed the scanner.

**Public methods:** `submit_claim`, `review_claim`, `get_claim_status`,
`get_claim_data`, `list_claims`.

**Safety properties**
- `agent` is `gl.message.sender_address`, never a parameter.
- `review_claim` reads the scan result from `SourceIntegrityScanner` on-chain.
  It reverts with `Source has not been integrity-scanned yet` for an unscanned
  source and with `Source failed the integrity scan` for a SUSPICIOUS one. The
  model is never asked to judge a source that failed the scan.
- The page is fetched again at review time and passed to the model inside a
  block labeled as untrusted data.
- A claim can be reviewed once. The record is written only after consensus
  succeeds.

## 3. CrossSourceCorroboration

**Pattern:** fully deterministic. It adds no model calls of its own.

**Purpose:** combines two reviewed claims into one corroboration result.

**Public methods:** `corroborate`, `get_corroboration_data`,
`list_corroborations`.

**Safety properties**
- Both claims are read from `GuardedEvidenceReview`'s state.
- Both must be `REVIEWED`, must have the exact same claim text, and must come
  from different domains.
- The status is `CORROBORATED` only if both verdicts are `SUPPORTED`.
- A pair of claim ids can be corroborated once, in either order.

## 4. IntegrityIncidentLedger

**Pattern:** fully deterministic.

**Purpose:** a permanent public record of sources the scanner flagged.

**Public methods:** `record_incident`, `get_incident_data`, `list_incidents`.

**Safety properties**
- The verdict is read from the scanner's own state. A source that was never
  scanned, or that scanned SAFE, cannot be logged.
- A URL can be logged once.
- The record keeps both the original scan requester and the reporter.
