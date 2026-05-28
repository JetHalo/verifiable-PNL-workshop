---
name: lookup-zkverify
description: Look up zkVerify / zkVerifyJS / Kurier facts in the knowledgebase. Always query first before generating code, to avoid hallucinated APIs.
---

# lookup-zkverify · Knowledgebase query skill

Any question that touches **the zkVerify protocol / zkVerifyJS SDK / Kurier API / proof systems / aggregation / attestation** must go through this skill first. Do not answer from model memory alone.

## Workflow

1. **Read `knowledgebase/INDEX.yaml` first** — it gives the directory, the three-tier layout, and the freshness header.
2. Query in priority order:
   - **Priority 1**: `knowledgebase/*.yaml` (operational · protocol-level facts)
   - **Priority 2**: `knowledgebase/cases/<project>/*.yaml` (project-level case — current project is verifytrade)
   - **Priority 3**: `knowledgebase/handbook/example.*.yaml` (generic examples)
3. The KB has a `freshness.operational_last_marked_stale` field → if API info from the yaml looks wrong, **use WebFetch to pull the matching page from docs.zkverify.io** instead of trusting the local yaml.
4. Fact not in the yaml → **say "not in the knowledgebase" rather than guess.**

## Topic map (quick lookup)

| Task | Read this yaml |
|---|---|
| Submit a proof via zkVerifyJS | `zkverifyjs.sdk.yaml` + `zkverifyjs.non_aggregation.yaml` |
| Pick a proof system (Groth16 / Risc0 / SP1 / ...) | `proof.systems.yaml` |
| Understand aggregation / Merkle aggregation | `proof.aggregation.yaml` |
| Submit directly via Kurier | `kurier.api.yaml` + `kurier.direct.yaml` |
| Generate proofs in the browser | `browser.proving.yaml` |
| Verify an attestation on-chain | `base.contract.verification.yaml` |
| Debugging / something doesn't work | `troubleshooting.yaml` |
| Reproduce the full pipeline locally | `runbook.local.yaml` |
| See concrete call examples | `example.*.yaml` |

## Invariants (apply every time)

Read `knowledgebase/zkverify.invariants.yaml` — these are the zkVerify protocol's hard constraints. Generated code must never violate them.

## Version Lock Mandate (always check)

Before generating or modifying any code that touches zkverifyjs / nargo / bb / bb.js / Node / Kurier APIs, **you must consult** `knowledgebase/version.alignment.yaml`:

- Read `current_latest` for the target versions
- Read `project_anchors.<project>` to see whether a low version is pinned for this project
- Use the `verify_commands` section to actually run `--version` and compare
- Mismatch → stop and follow the `mismatch_prompt_template` (ASK_USER)

Skipping this step = violating Rule ④ of the Version Lock Mandate in CLAUDE.md.

## ⚠️ Current KB staleness warning

The operational tier was last aligned with the official docs on **2026-04-23** and is currently marked stale. Since then `zkverifyjs` has moved from 2.3.0 to **3.1.0** (with one MAJOR), and the proof systems list has drifted as well.

**Trigger condition:** if you find the yaml's API signature / field name / version number disagrees with what you just fetched from code or npm — **do not force-fit the yaml.** Use WebFetch to pull docs.zkverify.io and verify on the spot, and tell the user which yaml needs a refresh.
