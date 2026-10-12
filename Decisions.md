# Design decisions

Each decision lists what was chosen, why, and what it costs.

## D1. Bind the SAFE result to content with an immutable digest (not a re-scan per review)

The steward offered two valid designs: re-scan inside every review, or verify an immutable content binding before judgment. This project uses the binding.

- The scanner records a SHA-256 digest of the exact page text next to the verdict.
- The claim copies that digest when it is submitted.
- The review compares the live page digest with the bound digest before judging.

Why: a re-scan inside every review would run a second model classification per review, which costs more and can disagree with the first scan about the same page. The digest check is deterministic, cheap, and leaves an on-chain proof of exactly which content was approved.

Cost: scan records are write-once (see D6).

## D2. The digest is part of consensus

The digest is computed inside both the leader function and every validator function, from each node's own fetch, and strict equality is required on the verdict and the digest. A validator never accepts a digest computed by another node.

## D3. Hash check and judgment use the same fetch

In `review_claim` the page is fetched once per validator, hashed, compared, and only then passed to the judge. There is no gap between checking the content and using it, so the page cannot change between the two steps.

## D4. The digest covers the full text, the classifier covers the first 3000 characters

The scanner hashes the whole rendered text, so a change anywhere in the page changes the digest. The classifier reads the first 3000 characters and the review reads the first 2500. Everything the review can see was therefore inside the classified window.

## D5. The claim is bound at submission, and the scan status is re-checked at review

`submit_claim` refuses a source that is not SAFE or has no digest. `review_claim` re-reads the scan status as a defensive check, but the digest comparison is the authoritative guard.

## D6. Scan records are write-once

A URL can be scanned once. A second `scan_source` for the same canonical URL fails with `Already scanned`. This is what stops an old SAFE record from being overwritten by a different page.

Cost and mitigation: a page that legitimately changes cannot be re-approved under the same URL. It is scanned again under a different URL form, for example the same address with a query string. This works because query strings are preserved (D8). Another cost is that anyone can scan a URL first; if the page is unreadable at that moment the record is SUSPICIOUS and stays that way, so the alternative URL form is also the recovery path.

## D7. Fail closed

- An unreadable or empty page is SUSPICIOUS with an empty digest.
- A model response that is not a clear label defaults to SUSPICIOUS (scanner) or UNSUPPORTED (review).
- `submit_claim` refuses a record with an empty digest.
- If the digest does not match, `review_claim` reverts and the claim stays PENDING.

## D8. Query strings are preserved, unusual URLs are rejected

Stripping the query string made `page?id=1` and `page?id=2` share one record. Canonicalization now keeps the query. Other normalization is limited to trimming, `http` to `https`, a trailing slash, and spaces. The host is not lower-cased: two spellings of the same host produce two records, never one shared record, which is the safe direction. URLs with characters outside the allowed set (including fragments) are rejected rather than merged.

## D9. Strict equality as the equivalence principle

Verdicts are small labels and the digest is an exact string, so strict equality is the right check. Anything looser would let validators disagree about content and still reach consensus.

## D10. Corroboration depends on the review contract only

A claim becomes REVIEWED only if its page matched the scanned digest, so corroboration inherits the binding without repeating it. Domain independence compares the host after removing `www.`. Subdomains of one site count as different domains.

## D11. The incident ledger uses no model

Logging an incident is a deterministic read of the scan record: only SUSPICIOUS sources, once each. A ledger that depended on a model would add a second place where an injection could act.

## D12. Pure ASCII source

The deployment parser failed on non-ASCII characters in an earlier round. All four files are pure ASCII and the submitted source is the deployed source.

## D13. A digest is network-independent

The digest depends only on the rendered page text, not on the network or the node. The same page produced the identical digest on Studionet and on Bradbury (`5656dfe1ac39d0f6d4a484f22939c927942c45c13d417e29edbc83cea905e312`), so a digest recorded on one network can be compared with a fresh fetch anywhere.

## D14. Timeouts are rejections, not corrupted state

A scan or review does a live web fetch and a model call, and validators must agree. On the public testnet this can exceed the consensus window and return `VALIDATORS_TIMEOUT`. That outcome rejects the transaction without writing state, so the call can be retried with the same input. This happened once during testing (scan on Bradbury) and the retry succeeded with no change to the contract or the input.

## Known limitations

- **Dynamic pages.** A page whose rendered text changes between fetches (ads, timestamps) gives validators different digests, so scans and reviews fail closed. Use stable sources such as gists or static pages.
- **Text, not bytes.** The digest covers the rendered text, so a change that does not alter the text (for example an invisible markup change) is not detected, and does not need to be, because the judge only sees the text.
- **Write-once scans.** See D6.
- **Truncated windows.** Content past 3000 characters is hashed but not classified, and content past 2500 characters is not judged. Long sources should be split into focused pages.
- **Subdomain independence.** See D10.
- **Public testnet timeouts.** See D14.
