# Roadmap Recommendation (ZIP-Target Update)

## Current Target

Primary competition target remains ZIP-style baseline behavior (`zlib`).

## Updated Gate Status (2026-03-10)

- Phase 0: pass
- Phase 1: pass
- Phase 2 descriptor estimate-vs-actual: fail (real-coded gap remains large)
- Phase 3 scaling (ZIP-target framing): pass on synthetic, fail on broader corpora
- Phase 4 robustness: pass (current test budget)
- Phase 5 perf envelope: measured baseline established
- Phase 6 ZIP-class evaluation: fail

## Recommendation

1. Do not position the codec as a ZIP competitor in its current form.
2. Keep the project in research mode for structured-data niches.
3. If ZIP competition remains the goal, prioritize descriptor redesign for non-synthetic corpora before scaling further.

## Evidence

See `reports/zip_competition_results.md` for corpus-by-corpus ratio, speed, and memory results with charts.
