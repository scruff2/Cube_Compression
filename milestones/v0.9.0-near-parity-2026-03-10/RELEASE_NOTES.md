# Near-Parity Milestone Release Notes

Tag: `v0.9.0-near-parity-2026-03-10`
Source commit: `04d96bc`
Date: 2026-03-10

## Summary

This milestone locks a reproducible near-parity snapshot against `zlib`.

## Key Results

- structured_synthetic: cube best real `304` bits vs zlib `1904` bits
- semi_structured_narrow: cube best real `57,800` bits vs zlib `57,920` bits
- mixed_general: cube best real `31,792` bits vs zlib `31,800` bits

## Validation

- `pytest -q` passed (`31 passed`)

## Included Artifacts

See `MANIFEST.json` and `SHA256SUMS.txt`.
