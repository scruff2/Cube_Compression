# Corpus Plan (Phase 1)

This project uses three corpus families for fair evaluation:

1. Structured synthetic
- exact-repeat
- prefix-variant
- family-mixture
- shifted-overlap

2. Semi-structured narrow-domain (to be added when available)
- expected source: user-provided domain-specific binary corpus

3. Mixed general reference
- small public-style mix for sanity checks against general-purpose codecs

## Split policy

For each corpus family:
- fixed train/test split files
- deterministic generation or deterministic selection seed

## Current presets

See `configs/presets/` for run-ready benchmark presets.
