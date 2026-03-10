# Final Mile Plan

Date: 2026-03-10
Goal: execute the recommendation plan to close the remaining ZIP-target gap.

## Plan

- [x] P1: Add compact literal-only container to reduce fixed wrapper overhead.
- [x] P2: Preserve mode identity and exact bit length in compact decode path.
- [x] P3: Add/adjust robustness + roundtrip tests for compact/framed variants.
- [x] P4: Run full validation (`pytest -q`) and 3-corpus benchmark/perf reruns.
- [x] P5: Update reports and README with final results.
- [x] P6: Commit and push.

## Results

- Test suite: `31 passed`.
- Best real mode on semi-structured: `57,800` bits vs `zlib 57,920` (`-120` bits).
- Best real mode on mixed-general: `31,792` bits vs `zlib 31,800` (`-8` bits).
- Wins are present but small; below the roadmap meaningful-margin threshold (`>=5%`).
