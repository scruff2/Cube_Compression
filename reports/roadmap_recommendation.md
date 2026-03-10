# Roadmap Recommendation (ZIP-Target Update)

## Current Target

Primary competition target is now ZIP-style baseline behavior (`zlib`) rather than family-aware structured coding.

## Updated Gate Status

- Phase 0: pass
- Phase 1: pass_with_limitations (real large narrow-domain corpus still missing)
- Phase 2 descriptor estimate-vs-actual: still weak vs idealized estimates
- Phase 3 scaling (ZIP-target framing): pass

## Recommendation

Continue execution under ZIP-target framing with the next priorities:

1. Speed and memory characterization of winning real modes vs zlib.
2. Robustness hardening (format/integrity/fuzzing).
3. Broader corpus pack to verify wins are not synthetic-only.

## Important Caveat

Cube still trails family-aware on many runs. This does not block ZIP-target progress, but should be documented as a separate in-domain efficiency gap.
