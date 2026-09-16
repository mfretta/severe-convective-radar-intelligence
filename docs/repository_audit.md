# Repository audit

## Existing material retained

The repository contained one real radar archive directory, `2026-08-30/`, with 2,045 native Rainbow `.vol` files. This is the authoritative source archive and is retained without modification.

## Existing material replaced or added

No prior executable code, tests, documentation, Bronze/Silver/Gold datasets, frontend, backend, notebooks, or configuration were present. SC Sentinel therefore starts with a clean implementation rather than adapting an unrelated project.

## Safeguard

Source files are never used as an output directory. All generated metadata and later derived products live beneath `data/`, while the native archive remains read-only by pipeline convention.
