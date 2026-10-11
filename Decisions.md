# Design Decisions

## Why scanning is a separate step from judging

If one model call both read a page and decided whether the page supports a
claim, a poisoned page could argue its own case in the same breath. Splitting
the work means the scanner only classifies text and never sees the claim, and
the reviewer never runs at all on a source the scanner rejected. The check
happens before the judgment, in contract logic, so it does not depend on the
judging model noticing the attack.

## Why strict equality on a two-way label

Both model-backed contracts ask for one word from a tiny fixed set. Independent
validators are far more likely to reproduce a single label exactly than a score
or a free-form answer. A continuous score with a tolerance band caused a
rejection on an earlier project because values inside the band could lead to
different outcomes, so no score is used here.

## Why an unreadable page counts as SUSPICIOUS

A page the validators could not read cannot be certified as safe. Treating
"could not read" as SAFE would let an attacker pass the scan by making the
fetch fail. The cost is that a temporary fetch outage can produce a false
SUSPICIOUS, which is the conservative direction.

## Why fetched text is wrapped as untrusted data

Detection can miss. As a second layer, the review prompt places the page text
between explicit markers and tells the model to treat it only as data. This
helps, but it is a mitigation and not a guarantee.

## Why two independent domains for corroboration

An attacker who controls one page has an easier job than one who must poison
two unrelated sites in a consistent way. The contract requires different
domains, identical claim text, and two separate SUPPORTED reviews.

## Why the ledger and corroboration contracts use no model

Aggregating results that consensus already finalized is bookkeeping. Adding
more model calls would add cost and risk without adding a safety property.

## Why identity comes from the transaction sender

Every submitter, requester and reporter field is taken from
`gl.message.sender_address` when the action happens, and downstream contracts
read it from the upstream record. No caller can supply an identity.

## Why there are no funds and no timestamps

No contract holds or moves GEN, which removes the custody risks that slowed an
earlier escrow project. `gl.block.timestamp` does not exist in this SDK
version, so no logic depends on time.

## Why every contract is plain ASCII with no undecorated methods

Studio refused to load a contract schema when the source contained non-ASCII
characters (typographic dashes inside a docstring and a prompt) and the file
had been pasted into the editor. All four files are now pure ASCII, helper
logic lives in module-level functions, and every instance method carries a
`@gl.public` decorator.

## Known limitations

1. **Detection lowers risk and does not remove it.** The scanner is itself a
   language model. Two attack texts were tested on-chain: a direct one
   ("ignore all previous instructions") and a subtler one that says the page is
   pre-verified and asks a reviewer to approve every claim. Both were flagged
   SUSPICIOUS. That is two samples, not a proof. The scanner is not a formal
   verifier, and an injection that does not read like an instruction may pass.

2. **A scan is permanent for a URL.** If a page is scanned SAFE and later
   changed to include an injection, `GuardedEvidenceReview` fetches the new
   content when it reviews a claim but does not run the scanner again. A
   production version would need a rule for expiring or repeating scans.

3. **Query strings are ignored.** URL normalization removes everything after
   `?`, so two URLs that differ only by query string share one scan result.

4. **Network timeouts happen on Bradbury.** One call returned LEADER_TIMEOUT on
   the public testnet and succeeded on retry with no change. A timed-out call
   writes nothing, so retrying is safe.
