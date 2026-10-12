# SigningLab — public verification

SigningLab evaluates football signings and tells its clients, for each one, whether the move is
worth making. This repository exists so that nobody has to take our word for how often we are right.

Before an outcome is known, we publish a cryptographic fingerprint of every verdict we issue.
After the season closes, a public source of randomness that nobody controls picks which of those
verdicts we must open. We then publish the originals, and anyone can check that the fingerprints
match and compare the verdicts with what actually happened on the pitch.

The point is the order of events. The fingerprints are already here, timestamped by this
repository's history. They cannot be rewritten later to fit the results.

**Generation SL 2026.1 — 2,752 commitments in 2 chained batches, published 17 Aug and 12 Oct 2026.
Reveal due at season close, 2027.**

## Check it yourself

No dependencies, no network, Python 3.8 or newer:

```
git clone https://github.com/signinglab/signinglab
cd signinglab
python verify.py
```

That runs three checks:

- **files** — every artifact hashes to the value recorded in `manifest.json`.
- **chain** — each batch names its predecessor by hash, so no batch can be swapped or back-dated.
- **union** — the set of commitments that the reveal will be drawn from is exactly the published
  batches, with nothing added and nothing dropped.

You can also reproduce the draw. Given the beacon block hash, `python verify.py sample --beacon
<block_hash>` prints precisely which commitments must be revealed. Running it before the block
exists is impossible; running it after is deterministic, and it is how you confirm we revealed the
entries the beacon chose rather than the ones that happened to look good.

## How a commitment is built

```
commitment = sha256( "league|season|player_key|club_key|verdict|generation" + "|" + salt )
```

The salt is 16 random bytes, different for every record, held sealed and published only for the
entries the beacon selects. Without it the verdict cannot be recovered from the hash, not even by
trying all the possibilities: that is what keeps the commitment binding without disclosing it.

`player_key` and `club_key` are public identifiers, so the commitment is tied to a specific player
joining a specific club and cannot be quietly re-pointed at a different signing later.

## What is in here

| Path | |
|---|---|
| `sl2026_1/` | The commitment batches for generation SL 2026.1, the population each covers, and the cumulative manifest that fixes the chain before any beacon is read. |
| `retrospective/` | A 2024 and 2025 pilot run of the same protocol, already revealed. Each sample carries the verdict and the real outcome, so the hit rate is yours to compute. |
| `manifest.json`, `MANIFEST.md` | Every published file with its SHA-256 and byte size. |
| `PROTOCOL.md` | The rules in full, including what happens at reveal time and what we do if something goes wrong. |
| `verify.py` | The verifier. Standard library only, so you can read all of it. |

## What is not in here

Model architecture, features, weights, scores and thresholds are not published and are not part of
the commitment. The commitment covers the binary recommendation a client sees, and nothing else.
Verdicts for the open generation stay with our clients; this repository publishes their fingerprints,
not their contents.

That is the trade being made: you get a statistical guarantee that the verdicts were fixed in
advance and honest when fixed, without us handing over the product itself.

## Append-only

Nothing here is edited or deleted. A correction is published as a new file that names the superseded
file by hash. The git history is the record, and every batch is also tagged as a release at the
moment it is published.

---
SigningLab · [signinglab.com](https://signinglab.com) · verification artifacts licensed CC BY 4.0
