# Published artifacts

Every file below is fixed. `python verify.py files` recomputes each hash from the bytes in this
repository and compares it with `manifest.json`.

| File | SHA-256 | Bytes | What it is |
|---|---|---|---|
| `sl2026_1/commitments_sl2026_1.json` | `311dbed3747f30f7014dd15a9589f6365a2c8ae8cec0e146f55fc94d389411f8` | 142,454 | Batch 001. Chain root: 1,985 commitment hashes, published 17 Aug 2026 while every outcome was still unknown. |
| `sl2026_1/commitments_sl2026_1_batch002.json` | `02bf57ba4183a0b510d72b60d45417e71cda73b6eb5bdaa3bb67a9bf105b63a7` | 108,167 | Batch 002. 767 further commitments, chained to batch 001 by hash, published 12 Oct 2026. |
| `sl2026_1/commitments_map_sl2026_1_batch001.json` | `cfe25c6a782f478f0777b31abe3ccfac6bb909714316ac35b3e667a4e4b66a22` | 393,089 | Which signing each batch-001 commitment belongs to (league, season, player, club). No verdicts. |
| `sl2026_1/keys_manifest_sl2026_1_batch001.json` | `4279d09dcda1704b42ee1820bcb3803bca546b580f10c75c3879848372b46ec0` | 111,938 | The population batch 001 covers, the sampling rule, and the checksum of the sealed salt file. |
| `sl2026_1/protocol_addendum_sl2026_1_v1_1.json` | `97d6e988373ba28be80fb2a05aedbe8eba52d7e98ae8166e309186ddf9d7ab01` | 1,965 | Addendum of 17 Aug 2026 closing two rules earlier wording left ambiguous. Changes no published hash. |
| `sl2026_1/cumulative_manifest_sl2026_1.json` | `6074d9e5a7dade383fbdb0c779532321210b11800f9151c95ff993152fc7cb61` | 2,784 | The full chain fixed before any beacon is read: every batch, its hash, its count, and the hash of the deduplicated union. |
| `retrospective/sample_2024.csv` | `3f757edd95cb2345b1e5ae70cf5285e9fd5564e25d3079218ab8b3049340eb60` | 5,478 | Retrospective pilot, 2024: the 100 signings the 2025-01-01 Bitcoin block selected, with verdict and real outcome. |
| `retrospective/sample_2025.csv` | `74f470e9975fdebde1d89a918ca09282139020aed4f8f648f8b230fd6e2ac523` | 5,473 | Retrospective pilot, 2025: the 100 signings the 2026-01-01 Bitcoin block selected, with verdict and real outcome. |
| `retrospective/population_2024.csv` | `571ca2b6ed7d69dfbb21c751b52718cc86ae3bb6e12e09b6c71eda44ea374858` | 122,414 | The 4,010 signings the 2024 sample was drawn from. |
| `retrospective/population_2025.csv` | `32939924d774260260d6358ce3ff531ff13998a1bb4c48d58715514ae8fa541e` | 139,623 | The 4,549 signings the 2025 sample was drawn from. |
| `retrospective/meta.json` | `ecf1a8136e591642c85e6523430e6c59780d2477bac70a78af58624d8cd4fe2a` | 631 | Block height, block hash and selection rule for each retrospective sample. |

Generation SL 2026.1: **2,752 commitments** in 2 chained batches.
Hash of the deduplicated union: `03185d75ed75f7fb6e91a4050853f56e6192ef6ac53137a8214b9b8ce88b8c1b`
