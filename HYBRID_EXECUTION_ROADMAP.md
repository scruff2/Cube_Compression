# Hybrid Compression Roadmap

Date: 2026-03-10
Objective: close remaining gap to `zlib` on non-synthetic corpora by adding hybrid fallback behavior.

## Milestones

- [x] M1: Add stream-level literal fast path for framed real modes (`fixed`, `local`, `entropy`).
- [x] M2: Add decode support and corruption handling tests for the new fast path.
- [x] M3: Run full test suite and regenerate 3-corpus benchmark + perf evidence.
- [x] M4: Refresh README and reports with post-hybrid results.
- [x] M5: Commit and push.

## Success Criteria

- All tests pass.
- Exact decode remains lossless.
- Non-synthetic best-real bits improve or hold; no correctness regressions.

## Result Summary

- Test gate: `pytest -q` => `31 passed`.
- Semi-structured narrow best-real: `58,064` bits vs `zlib 57,920` (delta `+144` bits).
- Mixed general best-real: `31,944` bits vs `zlib 31,800` (delta `+144` bits).
- Structured synthetic remains a strong win.
