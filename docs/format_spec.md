# Format and Robustness Notes (Draft)

## Stream magic and mode metadata

Custom real-mode streams use a header with:
- magic: `CCM2`
- mode id
- original bit length
- token count
- flags:
  - `FLAG_ROUTE_ONLY` (`1`)
  - `FLAG_LITERAL_ZLIB` (`2`)
  - `FLAG_FRAMED_PAYLOAD` (`4`)
  - `FLAG_TOKEN_ZLIB` (`8`)

## Framed payloads (fixed/local/entropy modes)

For non-legacy real modes, payloads are framed as:

- `uint32 token_payload_len`
- `uint32 literal_blob_len`
- `token_payload` bytes
- optional `literal_blob`

If `FLAG_TOKEN_ZLIB` is set, `token_payload` bytes are zlib-compressed and must be decompressed before token parsing.

`literal_blob` (when present):
- `uint32 literal_bit_length`
- `zlib`-compressed literal bit bytes

Literal bits are consumed in token order using per-token literal lengths.

## Corruption behavior

Current behavior:
- wrong magic => explicit `ValueError`
- unsupported mode id => explicit `ValueError`
- truncated/corrupt entropy payload => explicit decode failure
- corrupt framed/literal payload sizes or zlib data => explicit decode failure
- invalid token-zlib flag/data combinations => explicit decode failure

## Safety goals

- fail closed on malformed data
- avoid silent misdecode
- preserve deterministic behavior

## Covered by tests

- `test_decode_rejects_bad_magic`
- `test_decode_rejects_corrupt_entropy_payload`
- `test_decode_rejects_corrupt_literal_payload`
- `test_decode_rejects_invalid_token_zlib_flag`
