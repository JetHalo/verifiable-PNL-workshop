# zkVerify Knowledge Base

This directory is a machine-readable zkVerify / Kurier knowledge base split apart in `/knowledge` style.

Entry file:

- `INDEX.yaml`

Recommended read order:

1. `INDEX.yaml`
2. `zkverify.invariants.yaml`
3. Load the relevant YAML according to the task router

Key rules:

- Witness / proof generation happens in the browser.
- The server only relays proofs and polls status.
- The Kurier API key lives on the server only.
- Each branch picks exactly one submission mode.
- In aggregation mode you MUST check `statement == leaf` and `verifyProofAggregation(...) == true`.

The original long-form documentation lives at:

- `../doc/`

