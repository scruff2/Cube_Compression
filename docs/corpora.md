# Corpus Plan (Phase 1)

This project uses three corpus families for fair ZIP-target evaluation:

1. Structured synthetic
- source: generated synthetic phrase families (`v1_4_variable`)
- purpose: controlled stress tests for route-descriptor behavior

2. Semi-structured narrow-domain
- source: locked requirements-document pack (`corpora/phase1/semi_structured_narrow`)
- purpose: repetitive technical prose domain where shared structures may help

3. Mixed general reference
- source: locked mix of code/config/docs/binary bytes (`corpora/phase1/mixed_general`)
- purpose: sanity-check against broader ZIP-style usage patterns

## Split policy

For each corpus family:
- fixed train/test split files
- deterministic generation or deterministic file-list selection
- split manifests saved under each corpus directory

## One-command preset runner

Run any family preset with:

```bash
python -m cube_codec.cli benchmark-preset --preset <preset.json>
```

Available Phase 1 preset files:
- `configs/presets/structured_synthetic.json`
- `configs/presets/semi_structured_narrow.json`
- `configs/presets/mixed_general.json`
