# Contract reference

All four contracts are pure ASCII Python for the GenLayer runtime, use `gl.nondet.web.render(url, mode='text')` and the `gl.vm.run_nondet_unsafe` leader/validator pattern, and handle no funds.

## Shared URL rules

Every contract that accepts a URL canonicalizes it the same way:

- surrounding whitespace is removed and a trailing `/` is trimmed
- `http://` is upgraded to `https://`
- spaces inside the URL are removed
- the query string is **kept** (this is the fix for distinct resources sharing one record)
- the result must match `https?://` + a dotted host + an optional path made of letters, digits, `_ - . / ? % & =`; anything else, including fragments, is rejected rather than merged with another URL

## SourceIntegrityScanner

Classifies a page and records exactly which content produced the verdict.

**Storage**

| Field | Meaning |
|---|---|
| `scans: TreeMap[str, ScanRecord]` | one record per canonical URL |
| `url_log: TreeMap[u256, str]` | insertion order for listing |

`ScanRecord`: `source_url`, `requester`, `verdict` (SAFE or SUSPICIOUS), `content_hash` (SHA-256 hex of the rendered page text, empty when the page was unreadable), `status` (SCANNED).

**Methods**

| Method | Type | Behavior |
|---|---|---|
| `scan_source(source_url)` | write | Validates the URL, refuses a URL that already has a record (`Already scanned`), fetches the page, classifies the first 3000 characters, hashes the full text |
| `get_scan_status(source_url)` | view | `SAFE`, `SUSPICIOUS` or `NOT_SCANNED` |
| `get_scan_data(source_url)` | view | JSON with `source_url`, `requester`, `verdict`, `content_hash`, `status`, or `NOT_FOUND` |
| `list_scans()` | view | `url:verdict` pairs |

**Consensus.** Strict equality on `verdict` and `content_hash`. Both are computed inside the leader and inside every validator from that node's own fetch.

**Fail-closed rules.** An unreadable or empty page is SUSPICIOUS with an empty hash. A response that is not a clear label defaults to SUSPICIOUS.

## GuardedEvidenceReview

Judges a claim only against the exact content that was scanned SAFE.

**Storage.** `claims: TreeMap[u256, ClaimRecord]`, `next_id`, `scanner_contract`.

`ClaimRecord`: `claim_id`, `agent`, `claim`, `source_url`, `source_hash` (the scanner digest bound at submission), `verdict`, `status` (PENDING or REVIEWED).

**Methods**

| Method | Type | Behavior |
|---|---|---|
| `submit_claim(claim, source_url)` | write | Requires a scan record with verdict SAFE and a non-empty hash; stores the hash in the claim. Errors: `Source has not been integrity-scanned yet`, `Source failed the integrity scan - cannot use as evidence`, `Scan record is missing a content hash` |
| `review_claim(claim_id)` | write | Re-checks the scan status, then every validator re-fetches the page, recomputes the digest, compares it with `source_hash`, and only on a match judges the claim as SUPPORTED or UNSUPPORTED. Errors: `Claim not found`, `Already reviewed`, `Source content changed since scan - cannot review under stale scan` |
| `get_claim_status(claim_id)` | view | PENDING, REVIEWED or NOT_FOUND |
| `get_claim_data(claim_id)` | view | JSON of the claim including `source_hash` and `verdict` |
| `list_claims()` | view | `id:status` pairs |

**Consensus.** Strict equality on `content_hash_matches` and `verdict`. A page that differs from the bound digest makes every validator return `content_hash_matches = false`, and the transaction is rejected, so the claim stays PENDING.

**Prompt hygiene.** The fetched text is wrapped as untrusted data and the first 2500 characters are used. That window is inside the 3000 characters the scanner classified.

## CrossSourceCorroboration

Corroborates one statement across two reviewed claims.

**Methods**

| Method | Type | Behavior |
|---|---|---|
| `corroborate(claim_id_a, claim_id_b)` | write | Requires two distinct claims, both REVIEWED, with identical claim text and sources on different domains (after removing `www.`); the pair can be used once. Status is CORROBORATED when both verdicts are SUPPORTED, otherwise NOT_CORROBORATED |
| `get_corroboration_data(id)` | view | JSON with both claim ids, both domains and the status |
| `list_corroborations()` | view | `id:status` pairs |

Errors: `Must provide two distinct claim ids`, `This pair has already been corroborated`, `Claim A not found`, `Claim B not found`, `Claim A has not been reviewed yet`, `Claim B has not been reviewed yet`, `Could not determine source domains`, `Sources must come from independent domains`.

Content binding is enforced upstream: a claim can only be REVIEWED if its page matched the scanned digest, so this contract does not repeat the check.

## IntegrityIncidentLedger

Deterministic record of sources that failed the scan. It never calls a model.

**Methods**

| Method | Type | Behavior |
|---|---|---|
| `record_incident(source_url)` | write | Reads the scan record; only a SUSPICIOUS source can be logged, once. Errors: `Source has not been scanned yet`, `Only SUSPICIOUS sources can be logged as incidents`, `Already logged` |
| `get_incident_data(incident_id)` | view | JSON with `source_url`, `scan_requester`, `reported_by`, `status` |
| `list_incidents()` | view | incident listing |
