# Format and Robustness Notes (Draft)

## Stream magic and mode metadata

Custom real-mode streams use a header with:
- magic: `CCM2`
- mode id
- original bit length
- token count
- flags (including route-only optimization)

## Corruption behavior

Current behavior:
- wrong magic => explicit `ValueError`
- unsupported mode id => explicit `ValueError`
- truncated/corrupt entropy payload => explicit decode failure

## Safety goals

- fail closed on malformed data
- avoid silent misdecode
- preserve deterministic behavior

## Covered by tests

- `test_decode_rejects_bad_magic`
- `test_decode_rejects_corrupt_entropy_payload`
