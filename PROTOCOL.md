# Protocol SL-COMMIT-v1

The rules below were fixed before the commitments were published and are reproduced here in full.
Each generation's own JSON files restate them; where wording differs, the JSON published at the
time governs, and `sl2026_1/protocol_addendum_sl2026_1_v1_1.json` records the one clarification
issued so far.

## 1. Commit

For every verdict issued in a generation, SigningLab computes

```
commitment = sha256( "league|season|player_key|club_key|verdict|generation" + "|" + salt_hex )
```

and publishes the commitment hash. The salt is 16 random bytes per record, generated once and held
sealed. Published alongside the hashes: the issuing date, the count, the per-league counts, and the
population covered (league, season, player key, club key) — never the verdict.

Commitments are published while the outcomes they refer to are unknown. A verdict that is not
committed at that moment cannot be committed later for that generation.

## 2. Chain

A generation may be committed in several batches, because signings keep arriving through the
transfer window. Each batch after the first records `prev_file` and `prev_sha256`, the SHA-256 of
the batch before it. Changing any earlier batch therefore breaks every batch that follows.

Before any beacon is read, a cumulative manifest is published listing every batch, its hash, its
count, the total, and the SHA-256 of the deduplicated union of all commitment hashes. The union is
the sampling universe. It is computed as the lowercase hex hashes, deduplicated, sorted ascending as
strings, each followed by a single newline, concatenated, UTF-8 encoded.

## 3. Freeze outcomes

At season close, before any beacon is read, SigningLab computes the outcome for the **entire**
committed population, freezes that file and publishes its SHA-256. This comes first on purpose: it
removes any room to decide what counts as a success after seeing which entries were selected.

## 4. Read the beacon

The beacon is the hash of the first Bitcoin block mined on or after the announced cutoff, which for
generation SL 2026.1 is 2027-07-01 00:00 UTC. The cutoff is announced before the commitments are
published. Nobody, SigningLab included, can predict or influence that block hash.

## 5. Select

```
score = sha256( "SL-SAMPLE-v1|" + beacon + "|" + commitment_hash )
```

over the deduplicated union. The selected entries are the `K = min(100, N)` smallest scores, hex
ascending. The rule is deterministic: given the beacon, anyone reproduces the selection exactly, and
`python verify.py sample --beacon <block_hash>` does it.

## 6. Reveal

For the selected entries only, SigningLab publishes the payload (league, season, player key, club
key, verdict, generation), the salt, and the frozen outcome. Each hash is then recomputed from the
revealed payload by anyone who cares to, and the verdicts are compared with what happened.

The rest of the set stays closed. Its hashes remain published and remain binding for any future
reveal.

## Why a sample is enough

Because the selection is unpredictable, every commitment has to be honest when it is made. Replacing
or back-dating even a small share of the set is caught with high probability by a draw of 100: at 5%
tampering the chance of going undetected is about 0.95^100, roughly 1 in 170. Publishing the full
labeled set instead would hand over the product.

The sample proves integrity. It is not the accuracy claim by itself: the accuracy claim is the
comparison of the revealed verdicts against the frozen full-population outcomes, both of which are
pinned by hashes published before the beacon.

## Failure cases, stated in advance

- **A salt is lost.** The affected entries can no longer be revealed. They are reported as
  unrevealable, by hash and count, in the reveal publication. Nothing else is adjusted. Unrevealable
  entries are not replaced by substitutes in the draw.
- **A recomputed hash does not match.** It is published as a mismatch, with the payload and salt that
  were used, so that third parties can confirm the failure independently.
- **The beacon block is contested** (a reorg at the cutoff height). The canonical chain's block at
  that height six blocks later governs, and the block height and hash used are published.
- **A commitment turns out to be malformed.** It is left in place. A new file documents the defect
  and names the affected hashes; the original is never edited.

## Retrospective pilot

`retrospective/` applies the same selection mechanics to the already-closed 2024 and 2025 seasons,
using the first Bitcoin block of each following year. Those samples are fully revealed, with verdict
and real outcome per row, and the populations they were drawn from are published next to them. They
demonstrate the mechanics end to end; they are not a substitute for the live commitment above, since
the outcomes were already known when the pilot was built. That limitation is the reason the live
protocol exists.
