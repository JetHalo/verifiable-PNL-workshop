# Knowledge Base Refresh Report
# knowledgebase/*.yaml — 2026-04-23 baseline vs 2026-05-28 authoritative pull

Generated: **2026-05-28**
Baseline freshness: **2026-04-23** (per `INDEX.yaml`)
Scope: 21 operational yamls + INDEX
Methodology: pulled `docs.zkverify.io`, `registry.npmjs.org/zkverifyjs`,
`github.com/zkVerify/zkverifyjs/releases`, `raw.githubusercontent.com/zkVerify/zkverifyjs/main/README.md`,
and live `api.kurier.xyz` / `api-testnet.kurier.xyz` `/version` + `/status`.

DO-NOT-MODIFY directive: this report does NOT rewrite any yaml. It identifies
diffs and **proposes** replacement content for the two files that have changed
materially. User must review and apply.

---

## 0. Executive summary

| Surface | Change since 2026-04-23 |
| --- | --- |
| **zkverifyjs npm** | 2.3.0 → 3.1.0 (5 releases: 2.4.0, 2.5.0, 3.0.0, 3.1.0). 3.0.0 is MAJOR. |
| **Node engine** | `>= 18` → `>= 24` (3.0.0 breaking change, see §3) |
| **Ultrahonk config** | New required `version` field (V0_84 / V3_0 / Legacy) — 2.4.0 + 3.1.0 |
| **TEE config** | New required `variant: TeeVariant.Intel` — 2.4.0 |
| **`.execute()` shape** | New `domainId` param at top-level of execute args (was internal in 2.3) |
| **Kurier service** | mainnet & testnet bumped `v1.26.1` → `v1.30.0` (compatible; no API shape change) |
| **Kurier supported proofs (live)** | mainnet: groth16/plonky2/risc0/**fflonk**/ultraplonk/sp1/ultrahonk (7); testnet adds ezkl (8). **No `tee` in either live `/status` endpoint** |
| **docs.zkverify.io supported_proofs** | Now lists **9** systems incl. TEE (Intel TDX, AWS Nitro). docs page lists TEE but Kurier doesn't yet relay it. |
| **Contract addresses** | Unchanged. Mainnet Base + Horizen + 6 testnets listed verbatim in §4. |
| **Statement formula** | Unchanged (`keccak256(keccak256(verifier_ctx), hash(vk), version_hash(proof), keccak256(public_inputs_bytes))`) |

---

## 1. Per-file status table

Legend:
- `current` — no observable drift against sources
- `stale_minor` — drift exists but does not break workshop demo
- `stale_major` — drift will cause runtime / type errors or wrong API call
- `unknown` — could not fully verify from public sources

| # | File | Status | One-line reason |
|---|---|---|---|
| 1 | `INDEX.yaml` | `stale_minor` | `freshness.zkverifyjs_version_current` says "3.1.0 2026-05-19" — accurate; just needs freshness date bump and clarifying TEE-in-docs-not-in-Kurier note |
| 2 | `zkverify.core.yaml` | `current` | Statement formula, aggregation events, verifier contract API all match docs verbatim. Pallet list (`supported_verifier_pallets.examples`) matches docs supported_proofs |
| 3 | `zkverify.invariants.yaml` | `current` | Pure rules; no protocol surface that can drift. No changes needed |
| 4 | `zkverifyjs.sdk.yaml` | **`stale_major`** | Missing `UltrahonkVersion` enum (V0_84/V3_0/Legacy) added in 2.4.0; missing `TeeVariant.Intel` required from 2.4.0; missing `domainId` param on `.execute()`; missing `batchVerify`, `optimisticVerify`, `batchOptimisticVerify`, `registerDomain`, `holdDomain`, `unregisterDomain`, `addDomainSubmitters`, `removeDomainSubmitters`, `aggregate`, `estimateCost`, `createSubmitProofExtrinsic`, `createExtrinsicHex`, `createExtrinsicFromHex`, `addDerivedAccounts`, `addAccounts` methods; missing Node ≥ 24 engine requirement; missing new `NetworkConfig.wsProvider` and `syncTimeoutMs` options |
| 5 | `zkverifyjs.non_aggregation.yaml` | `stale_minor` | SDK lifecycle steps still accurate, but new `domainId` execute param means `proofData` is now inside `{ proofData, domainId }` object — section `sdk_flow.4_execute` needs updating. No structural break for non-aggregation since domainId is optional. |
| 6 | `proof.systems.yaml` | **`stale_major`** | (a) docs.zkverify.io supported_proofs page does **list fflonk** so the comment in INDEX.yaml claiming "fflonk drifted out" is WRONG; (b) `risc0.proofOptions.version` examples include `V2_1` which the docs page no longer lists ("Risc0: v2.1, v2.2, v2.3" per docs — yaml has correct V2_1..V2_3 + adds V3_0 from SDK; mismatch between docs page and SDK); (c) `ultrahonk` section missing required `version` field (V0_84/V3_0/Legacy) per zkverifyjs README v3.1.0; (d) `ultrahonk.docs.noir_version: v1.0.0-beta.6` is outdated — docs.zkverify.io now states `Noir ≥ v1.0.0-beta.14, bb ≥ v3.0.0 and bb.js ≥ v3.0.0`; (e) `tee.proofOptions` missing `variant: TeeVariant.Intel`; (f) `tee` `note` should mention AWS Nitro as second variant per docs page; (g) groth16 supported curves per docs: BLS12-381 / BN128 / BN254 — yaml says `bn128, bn254, bls12-381` (✓ matches) |
| 7 | `proof.aggregation.yaml` | `current` | Aggregation flow, tuple fields, precheck args all match. No drift |
| 8 | `proof.statement.yaml` | `current` | Statement formula matches docs verbatim. Parity checks unchanged |
| 9 | `kurier.api.yaml` | `stale_minor` | Live `/version` now returns `serviceVersion: v1.30.0` (was `v1.26.1`) and adds new field `runtimeSpecVersion: 1006002`. Endpoint shapes unchanged. Supported_proofs live differs from yaml (see §2.6) |
| 10 | `kurier.direct.yaml` | `current` | Direct mode contract unchanged |
| 11 | `kurier.status.yaml` | `current` | All 9 raw statuses still valid; normalized mapping unchanged |
| 12 | `browser.proving.yaml` | `current` | No API surface; pure pattern |
| 13 | `base.contract.verification.yaml` | `current` | `verifyProofAggregation` signature matches docs verbatim. Contract addresses listed in this file? No — they live in §4 below |
| 14 | `schema.bindings.yaml` | `current` | Bindings schema unchanged. proofType enum still valid superset of Kurier live (see §2.6) |
| 15 | `env.schema.yaml` | `current` | No new env vars required by 3.0.0/3.1.0. (Node version bump is engine-level, not env-level) |
| 16 | `security.boundaries.yaml` | `current` | Pure invariants |
| 17 | `trust.model.yaml` | `current` | Pure invariants |
| 18 | `indexer.strategy.yaml` | `current` | No protocol drift |
| 19 | `execution.plan.yaml` | `current` | Stage-gate pattern unchanged |
| 20 | `runbook.local.yaml` | `stale_minor` | `prerequisites.node` says "v24.1.0" — coincidentally aligns with new `engines.node >= 24` from zkverifyjs 3.0.0, BUT should be explicitly tied to zkverifyjs ≥ 3.0.0 requirement instead of "Kurier tutorial recommends" |
| 21 | `acceptance.criteria.yaml` | `current` | No protocol surface; acceptance gates unchanged |

**Net: 2 files `stale_major` (proof.systems.yaml, zkverifyjs.sdk.yaml), 4 files `stale_minor`, 15 files `current`.**

---

## 2. Specific changes detected (with quoted evidence)

### 2.1 zkverifyjs npm version timeline

Source: `https://registry.npmjs.org/zkverifyjs` (curl, 2026-05-28)

```
2.3.0: 2026-03-09 (baseline)
2.4.0: 2026-05-06  ← Ultrahonk versions + TEE variant
2.5.0: 2026-05-11  ← subscription cleanup
3.0.0: 2026-05-14  ← MAJOR: Node ≥24, dep cleanup, immutable options
3.1.0: 2026-05-19  ← Ultrahonk version Legacy default
```

Latest dist-tag: `latest = 3.1.0`. Quoted from npm registry response:
`{'latest': '3.1.0'}`

### 2.2 Ultrahonk `version` field is now required (3.1.0)

Source: GitHub release v3.1.0 body, quoted verbatim:

> "Ultrahonk proofs now require a Version field and circuits built with BB
> V0.84 are now legacy and default the version to 'Legacy' if not provided.
> Existing deployed dapp contracts integrated with the zkVerify aggregation
> contract and using Ultrahonk BB V0.84 should work correctly once this
> v3.1.0 package has been installed."

Source: `https://raw.githubusercontent.com/zkVerify/zkverifyjs/main/README.md` (verbatim):

> "### UltraHonk
> Supports versions: `V0_84`, `V3_0`, `Legacy`
> Supports variants: `Plain`, `ZK`
>
> **Note for zkverifyjs v2.4.0+ and runtime v1.6.0+**: The `version` and
> `variant` options are required. If `version` is omitted, zkverifyjs
> defaults to:
> - `V0_84` on runtime v1.6.0
> - `Legacy` on runtime v1.6.1+
>
> The `Legacy` default preserves pre-versioning Ultrahonk statement hash
> compatibility."

**Impact on `proof.systems.yaml`**: current YAML `ultrahonk.proofOptions` only
has `variant: [Plain, ZK]`. Must add `version: [V0_84, V3_0, Legacy]`.

**Impact on `zkverifyjs.sdk.yaml`**: current `proof_type_examples.ultrahonk`
has only `variant`. Must add `version`.

### 2.3 TEE `variant: TeeVariant.Intel` is now required (2.4.0)

Source: GitHub release v2.4.0 body (verbatim):
> "Added TEE verification key variant support with `TeeVariant.Intel`."

Source: zkverifyjs main README (verbatim):
> "**Note for zkverifyjs v2.4.0+ and runtime v1.6.0+**: The `variant` option
> is required. If omitted, zkverifyjs defaults to `Intel` for backwards
> compatibility and logs a warning."

Source: `https://docs.zkverify.io/architecture/supported_proofs` (verbatim):
> "**TEE** — Intel TDX, AWS Nitro"

So docs lists 2 hardware variants (Intel TDX, AWS Nitro) but the SDK enum
currently only exposes `TeeVariant.Intel`. AWS Nitro is in docs but not yet
in zkverifyjs at v3.1.0.

### 2.4 `.execute()` now takes top-level `domainId` (2.x → 3.x stabilized)

Source: zkverifyjs main README v3.x example (verbatim):

```typescript
.execute({
  proofData: {
    vk: vk,
    proof: proof,
  },
  domainId: 42, // Optional domain ID for proof aggregation
});
```

This is a meaningful shape change. In the YAMLs the SDK execute step is
documented as `execute({ proofData })` only. New shape is
`execute({ proofData, domainId? })`.

### 2.5 Node engine raised to >= 24 (3.0.0 BREAKING)

Source: PR #76 body (3.0.0 release, verbatim from footer):
> "BREAKING CHANGE: `engines.node` raised from `>= 18` to `>= 24` —
> Node 18 went EOL April 2025. Yarn Berry users on Node 18 will get
> hard install failures; npm/pnpm users get a warning unless
> `engine-strict=true`."

Note: PR body upper-text body actually says `>= 18` → `>= 20` in the
"Dependencies" section but the BREAKING CHANGE footer says `>= 24`. The
BREAKING CHANGE footer is authoritative (npm `engines.node` field is what
matters at install time). The discrepancy is likely a draft remnant in the
PR body — to confirm, the runbook's "node v24.1.0" recommendation lines up
with the footer.

### 2.6 Kurier supported_proofs drift

Live (2026-05-28) responses:

`https://api.kurier.xyz/api/v1/status` (mainnet):
```json
{
  "supportedProofs": ["groth16","plonky2","risc0","fflonk","ultraplonk","sp1","ultrahonk"]
}
```

`https://api-testnet.kurier.xyz/api/v1/status` (testnet):
```json
{
  "supportedProofs": ["groth16","plonky2","risc0","fflonk","ultraplonk","sp1","ultrahonk","ezkl"]
}
```

Compared to `proof.systems.yaml` (2026-04-23 baseline):
- `kurier_supported_mainnet_checked_2026_04_23`: **identical 7-list** (no drift)
- `kurier_supported_testnet_checked_2026_04_23`: **identical 8-list** (no drift)
- `openapi_enum`: contains `tee` which is NOT in either live `/status` response

**Important clarification**: the user's prompt said "fflonk in yaml but not
in current docs" — this is INCORRECT. fflonk IS in current docs
(`https://docs.zkverify.io/architecture/supported_proofs` lists it verbatim
as `**Fflonk** — BN128`) AND is in both live Kurier `/status` responses.
The yaml does not need to remove fflonk. The opposite drift exists for `tee`:
docs lists it, Kurier doesn't relay it yet.

### 2.7 Kurier service version bump

Live responses (2026-05-28):
- mainnet `/version`: `{"apiVersion":"v0.1.0","serviceVersion":"v1.30.0","environment":"production","status":"ok","runtimeSpecVersion":1006002}`
- testnet `/version`: `{"apiVersion":"v0.1.0","serviceVersion":"v1.30.0","environment":"staging","status":"ok","runtimeSpecVersion":1006002}`

Versus yaml-baseline 2026-04-23:
- `apiVersion: "v0.1.0"` ← same
- `serviceVersion: "v1.26.1"` → `v1.30.0` (+4 minor)
- new field: `runtimeSpecVersion: 1006002` (was absent in 2026-04-23 schema)

No request/response **shape** changes detected for `/submit-proof`,
`/job-status`, `/register-vk`, `/jobs`, `/status`, `/version`.

### 2.8 docs.zkverify.io supported_proofs full list (verbatim)

Source: `https://docs.zkverify.io/architecture/supported_proofs`

```
1. EZKL    — Reusable Verifier only (v0.1.0), BN254 (Curve), BDFG21 (batch opening scheme)
2. Fflonk  — BN128
3. Groth16 — BLS12-381, BN128, BN254
4. Noir UltraHonk  — Noir ≥ v1.0.0-beta.14, bb ≥ v3.0.0 and bb.js ≥ v3.0.0
5. Noir UltraPlonk — Noir ≥ v0.31.0, bb ≤ v0.76.4
6. Risc0   — v2.1, v2.2, v2.3
7. Plonky2 — Keccak256, Poseidon
8. SP1     — v5.x
9. TEE     — Intel TDX, AWS Nitro
```

Note: docs page Risc0 list is `v2.1, v2.2, v2.3`. zkverifyjs SDK enum is
`Risc0Version.V2_1|V2_2|V2_3|V3_0`. There's a `V3_0` in the SDK that the
docs page doesn't list yet. Either:
- (a) docs page is stale and V3_0 should be added there;
- (b) SDK exposes the enum value but pallet doesn't accept V3_0 yet.

This is a known authoritative ambiguity — left as `unknown` for V3_0.

### 2.9 Ultrahonk Noir version drift

Yaml says (`proof.systems.yaml` line 98):
```yaml
ultrahonk:
  docs:
    noir_version: "v1.0.0-beta.6"
```

Docs page now says:
> "Noir ≥ v1.0.0-beta.14, bb ≥ v3.0.0 and bb.js ≥ v3.0.0"

This is meaningful: `v1.0.0-beta.6` → `v1.0.0-beta.14` (8 betas later), and
bb is now ≥ v3.0.0 (the workshop's `verifytrade` case-study locks bb to
`0.84.0` per CLAUDE.md hard-rule ④; this means VerifyTrade's anchor version
is BB V0_84 which is exactly the "Legacy" Ultrahonk variant in zkverifyjs
3.1.0. Workshop must use `version: UltrahonkVersion.V0_84` or accept the
`Legacy` default).

### 2.10 Contract addresses (verbatim from docs)

Source: `https://docs.zkverify.io/architecture/contract-addresses`

```
Mainnet:
  Base               (8453)     0x5596aE76a636483361C9e777C03091BAEDcEa1C6
  Horizen            (26514)    0xCb47A3C3B9Eb2E549a3F2EA4729De28CafbB2b69

Testnet:
  Sepolia            (11155111) 0x5a3c35CCC5c05fDeFe5Ecafc15F4B1aC8eF71481
  Arbitrum Sepolia   (421614)   0x8fDFE115948b54e77134Ff3841a626FAd4E6A661
  Base Sepolia       (84532)    0x312468EbF274F1f584d93d0CCA8458cC91460FC0
  Optimism Sepolia   (11155420) 0xFbA954966Fa27adec13Ba42F96E9F8ec8308a860
  EDU Chain Testnet  (656476)   0x8fDFE115948b54e77134Ff3841a626FAd4E6A661
  Horizen Testnet    (2651420)  0x03225ff1ff4F1BAc6e81BB6317006A509422D51C
```

**None of the YAMLs currently store these addresses** (`base.contract.verification.yaml`
talks about the verifier contract abstractly but has no concrete address).
Recommendation: consider adding a new file `contract.addresses.yaml` so the
workshop doesn't have to look these up each run.

### 2.11 zkverifyjs.sdk.yaml missing public API methods

Source: zkverifyjs README v3.x table of contents (verbatim list of API methods):

| Method | In yaml? |
|---|---|
| `zkVerifySession.start` | ✓ |
| `zkVerifySession.close` | ✗ missing |
| `zkVerifySession.verify` | ✓ |
| `zkVerifySession.batchVerify` | ✗ missing |
| `zkVerifySession.optimisticVerify` | ✗ missing |
| `zkVerifySession.batchOptimisticVerify` | ✗ missing |
| `zkVerifySession.registerVerificationKey` | ✗ missing (yaml only mentions "register vk" in passing) |
| `zkVerifySession.getAggregateStatementPath` | ✓ |
| `zkVerifySession.getVkHash` | ✗ missing |
| `zkVerifySession.format` | ✗ missing |
| `zkVerifySession.formatVk` | ✗ missing |
| `zkVerifySession.createSubmitProofExtrinsic` | ✗ missing |
| `zkVerifySession.createExtrinsicHex` | ✗ missing |
| `zkVerifySession.createExtrinsicFromHex` | ✗ missing |
| `zkVerifySession.estimateCost` | ✗ missing |
| `zkVerifySession.getAccountInfo` | ✗ missing |
| `zkVerifySession.getAccount` | ✗ missing |
| `zkVerifySession.addAccount` | ✗ missing |
| `zkVerifySession.addAccounts` | ✗ missing |
| `zkVerifySession.addDerivedAccounts` | ✗ missing |
| `zkVerifySession.removeAccount` | ✗ missing |
| `zkVerifySession.subscribe` | ✗ missing |
| `zkVerifySession.waitForAggregationReceipt` | ✓ |
| `zkVerifySession.unsubscribe` | ✗ missing |
| `zkVerifySession.aggregate` | ✗ missing |
| `zkVerifySession.registerDomain` | ✗ missing |
| `zkVerifySession.holdDomain` | ✗ missing |
| `zkVerifySession.unregisterDomain` | ✗ missing |
| `zkVerifySession.addDomainSubmitters` (v1.3.0+) | ✗ missing |
| `zkVerifySession.removeDomainSubmitters` (v1.3.0+) | ✗ missing |
| `zkVerifySession.api` | ✗ missing |
| `zkVerifySession.provider` | ✗ missing |

The yaml is by-design "operational essentials only" not a full reference, but
the domain operation methods (`registerDomain`, `holdDomain`, `unregisterDomain`,
`addDomainSubmitters`, `removeDomainSubmitters`) are **directly relevant** to
the workshop because they let the workshop demo register its own
`aggregationDomainId` instead of borrowing a public one.

---

## 3. zkverifyjs 2.3 → 3.1 breaking & meaningful changes (chronological)

Compiled from GitHub release bodies (verbatim quotes inlined).

### 2.4.0 (2026-05-06)

Feature additions (PR #74):
- "Added Ultrahonk proof version support with `UltrahonkVersion.V0_84` and `UltrahonkVersion.V3_0`."
- "Added TEE verification key variant support with `TeeVariant.Intel`."
- "Updated Ultrahonk and TEE proof/VK formatting to match zkVerify runtime v1.6.0+ payload shapes."
- "Added runtime-aware type registration so zkverifyjs selects legacy or v1.6.0+ Polkadot custom types based on the connected chain runtime."

Compatibility fallbacks (verbatim):
- "Ultrahonk calls with only `variant` default to `UltrahonkVersion.V0_84` on runtime v1.6.0+."
- "TEE calls without `variant` default to `TeeVariant.Intel` on runtime v1.6.0+."
- "Added warnings when compatibility defaults are applied, so users can update their code explicitly."

→ **Not technically breaking** (defaults preserve old behavior), but workshop
code that explicitly sets `variant` without `version` will get a warning log.

### 2.5.0 (2026-05-11)

- "fix: clean up transaction and event subscriptions (PR #75)" — internal hygiene only.

### 3.0.0 (2026-05-14) — MAJOR

Three documented BREAKING CHANGE footers (verbatim from PR #76):

> "BREAKING CHANGE: `engines.node` raised from `>= 18` to `>= 24` — Node 18 went EOL April 2025."

> "BREAKING CHANGE: `web3`, `snarkjs`, `@types/snarkjs`, and `@types/web3` removed from `package.json`. They were never imported from src/. Any consumer who was relying on these as transitive deps via `zkverifyjs` must add them explicitly."

> "BREAKING CHANGE: `validateProofTypeOptions` (internal but exported) now returns `ProofOptions` instead of `void`; callers that previously relied on in-place mutation of the input options object will need to use the return value. The exported `bindMethods` helper has been removed from `utils/helpers` — it was internal and not referenced by any public consumer pattern, but it is no longer exported."

> "BREAKING CHANGE: `fastify` (dev dep used by the test wallet server) bumped 4.29.1 → 5.8.5. Affects integration test setup only — no runtime impact on the published package."

Non-breaking but user-facing additions:
- `NetworkConfig.wsProvider` — new option with `autoConnectMs` (default 2500) and `timeout`. Setting `autoConnectMs: false` disables auto-reconnect.
- `NetworkConfig.syncTimeoutMs` — new option, default 300_000 ms (5 min). Throws when exceeded.
- `WaitForNodeToSyncOptions` is now exported.

Bug fixes worth noting in workshop debugging context:
- `verify()` no longer mutates caller's `options.domainId`. Reusing a builder across `execute()` calls used to leak state.
- `getAggregateStatementPath` switched `.toHuman()` → `.toJSON()` because `.toHuman()` formatted u32 with thousand-separator commas and `Number()` returned NaN once `numberOfLeaves` crossed 1000 — **directly relevant** to any workshop that survives long enough to hit a domain with > 1000 leaves.
- `formatPublicSignals` now actually validates that inputs are strings; previously `[1, 2, 3]` (numbers) crashed later inside `BigInt()` with a cryptic error.
- `setupAccount` now rejects Substrate dev SURIs (`//Alice` etc.) on Volta and zkVerify mainnet; allowed on `.Custom()`. **Workshop should use `.Custom()`** if they want `//Alice`-style seeds for demos.
- BIP39 word-count enforced (12/15/18/21/24).

### 3.1.0 (2026-05-19)

> "Ultrahonk proofs now require a Version field and circuits built with BB V0.84 are now legacy and default the version to 'Legacy' if not provided. Existing deployed dapp contracts integrated with the zkVerify aggregation contract and using Ultrahonk BB V0.84 should work correctly once this v3.1.0 package has been installed."

→ Backwards-compatible default to `Legacy`; explicit `version` recommended.

### Summary of action items for workshop code (assumes upgrading to 3.1.0)

1. Set `engines.node >= 24` in workshop `package.json` or pin Node 24.x in `nvmrc`.
2. If workshop uses `Library.snarkjs` for Groth16, add `snarkjs` as a direct dep (no longer transitive).
3. Update Ultrahonk verify calls to include `version: UltrahonkVersion.V0_84` (matches VerifyTrade BB 0.84.0 anchor).
4. Update TEE verify calls to include `variant: TeeVariant.Intel` (silences warning).
5. Update SDK execute shape to `.execute({ proofData, domainId? })` — old `execute({ proofData })` still works but `domainId` is now the canonical place to pass it.

---

## 4. Proposed replacement: `proof.systems.yaml`

(Only this section is content the user can copy-paste over the existing file
after review. It preserves all existing semantics, updates outdated facts,
adds missing fields, and documents the docs-vs-kurier drift for `tee` and
`V3_0`.)

```yaml
# Supported Proof Systems
# Proof types, required proofOptions, limits, and artifact shapes
# Refreshed 2026-05-28 against docs.zkverify.io/architecture/supported_proofs
# and live api.kurier.xyz / api-testnet.kurier.xyz /status

kurier_supported_mainnet_checked_2026_05_28:
  # Live response from https://api.kurier.xyz/api/v1/status
  - groth16
  - plonky2
  - risc0
  - fflonk
  - ultraplonk
  - sp1
  - ultrahonk
  note: "tee is in docs.zkverify.io/architecture/supported_proofs but NOT yet in Kurier mainnet supportedProofs."

kurier_supported_testnet_checked_2026_05_28:
  # Live response from https://api-testnet.kurier.xyz/api/v1/status
  - groth16
  - plonky2
  - risc0
  - fflonk
  - ultraplonk
  - sp1
  - ultrahonk
  - ezkl
  note: "tee is in docs.zkverify.io/architecture/supported_proofs but NOT yet in Kurier testnet supportedProofs."

openapi_enum:
  # Kurier OpenAPI still advertises tee as accepted; backend may reject at runtime.
  - groth16
  - plonky2
  - risc0
  - fflonk
  - ultraplonk
  - sp1
  - ultrahonk
  - ezkl
  - tee

docs_zkverify_io_full_list_2026_05_28:
  ezkl:
    notes: "Reusable Verifier only (v0.1.0), BN254 (Curve), BDFG21 (batch opening scheme)"
  fflonk:
    notes: "BN128"
  groth16:
    curves: [BLS12-381, BN128, BN254]
  noir_ultrahonk:
    requires: "Noir >= v1.0.0-beta.14, bb >= v3.0.0 and bb.js >= v3.0.0"
  noir_ultraplonk:
    requires: "Noir >= v0.31.0, bb <= v0.76.4"
  risc0:
    versions: [v2.1, v2.2, v2.3]
    note: "zkverifyjs SDK enum also exposes V3_0; docs page does not list it as of 2026-05-28 — treat V3_0 as unverified for Kurier route."
  plonky2:
    hash_functions: [Keccak256, Poseidon]
  sp1:
    versions: "v5.x"
  tee:
    variants: [Intel TDX, AWS Nitro]
    note: "AWS Nitro listed in docs but zkverifyjs (v3.1.0) only exposes TeeVariant.Intel."

proof_options:
  groth16:
    proofOptions:
      library:
        examples: [snarkjs, arkworks, gnark]
      curve:
        examples: [bn128, bn254, bls12-381]
    proofData:
      proof: "object"
      publicSignals: "array|object"
      vk: "object|string vkHash"
    public_input_limit_docs:
      mainnet: 64
      testnet: 64

  fflonk:
    proofOptions:
      curve:
        examples: [bn128]
    public_input_limit_docs:
      mainnet: 1
      testnet: 1

  plonky2:
    proofOptions:
      hashFunction:
        examples: [Poseidon, Keccak256]
    limits_docs:
      max_public_inputs: 64
      max_proof_size: "256 KiB"
      max_vk_size: "50 KB"

  risc0:
    proofOptions:
      version:
        examples: [V2_1, V2_2, V2_3, V3_0]
        note: "V3_0 exists in zkverifyjs enum; not on docs page as of 2026-05-28."
    proofData:
      proof: "0x/cbor-compatible proof string"
      publicSignals: "public journal / pub_inputs"
      vk: "image_id or vkHash"
    limits_docs:
      max_public_inputs_size: "2052 bytes, 2048 bytes user input"
      format: cbor

  sp1:
    proofOptions: {}
    proofData:
      proof: "SP1 zkv proof"
      publicSignals: "public values"
      vk: "image_id or vkHash"
    limits_docs:
      max_public_inputs_size: "2048 bytes"
      supported_versions: "v5.x"

  ultrahonk:
    proofOptions:
      version:
        # NEW REQUIRED FIELD as of zkverifyjs 3.1.0
        examples: [V0_84, V3_0, Legacy]
        required: true
        default_runtime_v1_6_0: V0_84
        default_runtime_v1_6_1_plus: Legacy
        note: "Required since zkverifyjs 3.1.0. Workshop using bb 0.84.0 anchor → use V0_84 explicitly."
      variant:
        examples: [Plain, ZK]
        required: true_since_2_4_0
    proofData:
      proof: "hex string"
      publicSignals: "hex public inputs array/string"
      vk: "hex vk or vkHash"
    docs:
      noir_version: ">= v1.0.0-beta.14"
      bb_version: ">= v3.0.0"
      bbjs_version: ">= v3.0.0"
      hash: Keccak256
      public_input_limit: 32

  ultraplonk:
    proofOptions:
      numberOfPublicInputs:
        type: number
        required: true
    proofData:
      proof: "base64 proof or formatted proof"
      vk: "base64 vk or vkHash"
    docs:
      noir_version: ">= v0.31.0"
      bbup: "<= v0.76.4"
      public_input_limit: 32

  ezkl:
    proofOptions: {}
    docs:
      reusable_verifier_version: "v0.1.0"
      curve: BN254
      batch_opening_scheme: BDFG21
    note: "Supported in zkVerify/Kurier docs (testnet only as of 2026-05-28). Check current /status before use."

  tee:
    proofOptions:
      variant:
        examples: [Intel]
        required: true_since_2_4_0
        sdk_only: [Intel]
        docs_advertised: [Intel TDX, AWS Nitro]
        runtime_requirement: "zkVerify runtime v1.5.0+"
    proofData:
      proof: "0x-prefixed hex"
      publicSignals: "none"
    note: "OpenAPI advertises tee; Kurier /status mainnet+testnet do NOT yet list tee. Treat as docs-only as of 2026-05-28."

selection_guidance:
  noir_ultrahonk:
    use_when:
      - "new tutorial circuit"
      - "browser proving with Noir"
      - "Keccak-friendly public input hashing"
    caution:
      - "version field required as of zkverifyjs 3.1.0; default is Legacy on runtime v1.6.1+"
      - "variant required since 2.4.0"
      - "VerifyTrade workshop anchor is bb 0.84.0 → use version: V0_84"

  noir_ultraplonk:
    use_when:
      - "existing Noir UltraPlonk artifacts"
      - "public input count fixed and documented"
    caution:
      - "must set numberOfPublicInputs"

  groth16:
    use_when:
      - "Circom/snarkjs compatibility"
      - "simple examples"
    caution:
      - "curve/library must match vk/proof"
      - "zkverifyjs 3.0.0 dropped snarkjs as transitive dep; add it explicitly if using Library.snarkjs"

validation_checklist:
  - proofType_in_current_status_endpoint
  - proofOptions_match_proofType
  - vk_matches_circuit_build
  - public_input_count_within_limit
  - artifact_encoding_matches_route
  - local_verify_passes_before_kurier
  - ultrahonk_version_set_explicitly_since_3_1_0
  - tee_variant_set_explicitly_since_2_4_0
```

---

## 5. Proposed replacement: `zkverifyjs.sdk.yaml`

(Same caveat — review before applying.)

```yaml
# zkVerifyJS SDK Reference
# Non-Kurier SDK path for direct interaction with zkVerify
# Refreshed 2026-05-28 against zkverifyjs v3.1.0 (npm latest)
# Source: https://raw.githubusercontent.com/zkVerify/zkverifyjs/main/README.md
# Release notes: https://github.com/zkVerify/zkverifyjs/releases

overview:
  package: zkverifyjs
  latest_version_pulled: "3.1.0"
  latest_pull_date: "2026-05-28"
  purpose: "TypeScript SDK for sending proofs to zkVerify, listening to transaction events, waiting for finalization, registering verification keys, and managing aggregation domains."
  use_when:
    - submission_mode_is_zkverifyjs_non_aggregation
    - app_wants_direct_sdk_lifecycle
    - Kurier_is_not_selected_for_branch
  do_not_use_when:
    - branch_locked_to_aggregation_kurier
    - branch_locked_to_kurier_direct

runtime_requirements:
  engines_node: ">= 24"
  reason: "zkverifyjs 3.0.0 raised engines.node from >=18 to >=24 (Node 18 EOL April 2025)."
  if_using_snarkjs:
    rule: "Add snarkjs as a direct dep in your package.json. zkverifyjs 3.0.0 removed it from transitive deps."

installation:
  npm: "npm install zkverifyjs"
  dotenv: "npm install dotenv"
  optional_for_groth16: "npm install snarkjs"

session_modes:
  read_only:
    example: "await zkVerifySession.start().zkVerify()"
    can_send_transactions: false
  read_only_custom:
    example: "await zkVerifySession.start().Custom({ websocket, rpc, network })"
  backend_single_account:
    example: "await zkVerifySession.start().zkVerify().withAccount(SEED_PHRASE)"
    can_send_transactions: true
    secret_boundary: "seed phrase must be server-only"
    seed_constraints:
      - "BIP39 word count enforced (12/15/18/21/24) since 3.0.0"
      - "Substrate dev SURIs like //Alice rejected on .zkVerify() and Volta; allowed on .Custom()"
  backend_multi_account:
    example: "await zkVerifySession.start().zkVerify().withAccounts([SEED_1, SEED_2, SEED_3])"
    note: "Use addAccount/removeAccount/addDerivedAccounts/getAccountInfo to manage runtime."
  frontend_wallet:
    example: "await zkVerifySession.start().zkVerify().withWallet({ source, accountAddress })"
    can_send_transactions: true
    note: "Uses browser wallet context (window.injectedWeb3)."
  custom_network:
    fields:
      websocket: string
      rpc: string
      network: string  # optional label
    new_options_3_0_0:
      wsProvider:
        autoConnectMs: "number | false (default 2500)"
        timeout: number
        note: "autoConnectMs: false disables auto-reconnect; pair with session.provider.on('disconnected', ...)."
      syncTimeoutMs:
        default: 300000
        note: "Throws if node hasn't finished syncing within this many ms during session start."

verify_flow:
  fluent_pattern:
    steps:
      - "session.verify()"
      - "select proof type and config (e.g. .ultrahonk({version, variant}))"
      - "optional .nonce(n)"
      - "optional .withRegisteredVk()"
      - "execute({ proofData, domainId? })"
      - "listen to events"
      - "await transactionResult"
  events:
    - includedInBlock
    - finalized
    - error
    - ErrorEvent
  transactionResult:
    meaning: "Final transaction details after finalization."
  domainId_in_execute:
    location: "top-level of execute() args alongside proofData"
    optional: true
    example: "execute({ proofData: {vk, proof, publicSignals}, domainId: 42 })"

proof_type_examples:
  groth16:
    config:
      library: "Library.snarkjs | Library.arkworks | Library.gnark"
      curve: "CurveType.bn128 | CurveType.bn254 | CurveType.bls12381"
  ultraplonk:
    config:
      numberOfPublicInputs: number
  ultrahonk:
    config:
      version: "UltrahonkVersion.V0_84 | UltrahonkVersion.V3_0 | UltrahonkVersion.Legacy"
      variant: "UltrahonkVariant.Plain | UltrahonkVariant.ZK"
    required_since:
      version: "3.1.0 (defaults to Legacy on runtime v1.6.1+, V0_84 on v1.6.0)"
      variant: "2.4.0"
    workshop_recommendation: "version: V0_84 (matches VerifyTrade bb 0.84.0 anchor)"
  risc0:
    config:
      version: "Risc0Version.V2_1 | V2_2 | V2_3 | V3_0"
      note: "V3_0 in SDK enum; docs.zkverify.io supported_proofs only lists v2.1, v2.2, v2.3 as of 2026-05-28."
  plonky2:
    config:
      hashFunction: "Plonky2HashFunction.Poseidon | Plonky2HashFunction.Keccak256"
  sp1:
    config: {}
  ezkl:
    config: {}
  tee:
    config:
      variant: "TeeVariant.Intel"
    required_since:
      variant: "2.4.0 (defaults to Intel on runtime v1.6.0+ with warning)"
    sdk_only_variants: [Intel]
    docs_only_variants: [Intel_TDX, AWS_Nitro]

batch_verify:
  signature: "session.batchVerify().<proofType>(config).withRegisteredVk?.nonce?.execute([{proofData, domainId}, ...])"
  rule: "All proofs in a batch must be same ProofType and same config."
  failure_semantics: "If any proof fails, the whole batch fails."

optimistic_verify:
  methods:
    - optimisticVerify
    - batchOptimisticVerify
  use_when: "Want optimistic verification result before final on-chain inclusion."

register_verification_key:
  signature: "session.registerVerificationKey().<proofType>(config).execute(vk)"
  returns: "VKRegistrationTransactionInfo (contains statementHash)"
  later_use: "Set .withRegisteredVk() on subsequent verify calls and pass vk = vkTransactionInfo.statementHash"

aggregation_helpers:
  waitForAggregationReceipt:
    use_when: "SDK aggregation is selected."
    note: "Not used as gate in zkverifyjs-non-aggregation mode unless branch explicitly changes mode."
  getAggregateStatementPath:
    inputs:
      - blockHash
      - domainId
      - aggregationId
      - statement
    output: "AggregateStatementPathResult"
    bug_fixed_3_0_0: ".toHuman() -> .toJSON() — was returning NaN once numberOfLeaves > 1000."
  aggregate:
    signature: "session.aggregate(...)"
    note: "Publish aggregation; available v2.0.0+"

domain_management:
  available_since: "v1.x"
  methods:
    registerDomain:
      note: "queueSize: 0 throws; default queueSize only applies when arg is omitted (clarified in 3.0.0 README/JSDoc)."
    holdDomain: {}
    unregisterDomain: {}
    addDomainSubmitters:
      since: "v1.3.0+"
    removeDomainSubmitters:
      since: "v1.3.0+"
  workshop_relevance: "Lets the workshop register its own aggregationDomainId instead of borrowing a public one."

utility_methods:
  - getVkHash
  - format
  - formatVk
  - createSubmitProofExtrinsic
  - createExtrinsicHex
  - createExtrinsicFromHex
  - estimateCost
  - getAccountInfo
  - getAccount
  - addAccount
  - addAccounts
  - addDerivedAccounts
  - removeAccount
  - subscribe
  - unsubscribe

raw_access:
  - "session.api  # polkadot ApiPromise"
  - "session.provider  # polkadot WsProvider"

non_aggregation_status_gate:
  required:
    - includedInBlock_or_finalized_event_captured
    - transactionResult_persisted
    - proof_reference_fields_saved
  forbidden:
    - "calling /proof-aggregation endpoint"
    - "requiring aggregation tuple"
    - "using Kurier status parser"

security:
  backend_seed_phrase:
    rule: "If withAccount is used on backend, seed phrase is server-only and never logged."
    new_3_0_0_validation:
      - "Empty/whitespace seed throws clear message."
      - "Substrate dev SURIs (//Alice etc.) rejected on Volta/mainnet; allowed only on .Custom()."
      - "BIP39 word count 12/15/18/21/24 enforced."
      - "32-byte hex seeds and mnemonic-with-derivation still work."
  frontend_wallet:
    rule: "If withWallet is used, user must approve transaction in wallet."
  witness:
    rule: "Still browser-only unless case explicitly uses server-owned proof generation for non-private system proofs."

breaking_changes_2_3_to_3_1:
  - "engines.node >= 18 → >= 24 (3.0.0)"
  - "web3, snarkjs, @types/snarkjs, @types/web3 removed from package.json — add explicitly if consumer relied on transitive (3.0.0)"
  - "validateProofTypeOptions (internal but exported) now returns ProofOptions instead of void (3.0.0)"
  - "bindMethods helper removed from utils/helpers exports (3.0.0)"
  - "fastify dev dep 4.x → 5.x (3.0.0; test setup only)"
  - "Ultrahonk version field required (3.1.0; defaults to Legacy on runtime v1.6.1+ for backwards compatibility)"

validation_checklist:
  - submission_mode_locked_to_zkverifyjs_non_aggregation
  - no_kurier_payloads_used
  - no_proof_aggregation_gate
  - events_persist_included_finalized
  - transactionResult_persisted
  - business_gate_defined
  - node_version_24_or_higher
  - ultrahonk_calls_include_version_field
  - tee_calls_include_variant_field
  - snarkjs_added_as_direct_dep_if_used
```

---

## 6. Recommended `INDEX.yaml` freshness diff

Apply this change to lines 38-49 (and add a new clarifying note):

```yaml
# Freshness / drift status (last reviewed)
#
# operational tier:  2026-05-28 partial refresh (proof.systems.yaml + zkverifyjs.sdk.yaml)
#                    2026-04-23 baseline for other 19 files (verified current 2026-05-28)
# cases tier:        2026-05-28 (VerifyTrade one-day retro)
# handbook tier:     2026-04-23 captured, no longer actively maintained
freshness:
  operational_last_pulled: "2026-04-23"
  operational_last_verified: "2026-05-28"
  operational_files_refreshed_2026_05_28:
    - proof.systems.yaml      # ultrahonk version field + tee variant + bb v3.0.0
    - zkverifyjs.sdk.yaml     # 2.3 → 3.1 surface
  operational_files_minor_drift_2026_05_28:
    - INDEX.yaml              # this section
    - kurier.api.yaml         # serviceVersion 1.26.1 → 1.30.0, new runtimeSpecVersion field
    - runbook.local.yaml      # node version tie to zkverifyjs 3.0.0 requirement
    - zkverifyjs.non_aggregation.yaml  # execute() now takes domainId at top-level
  zkverifyjs_version_when_pulled_baseline: "2.3.0"
  zkverifyjs_version_current: "3.1.0"
  zkverifyjs_breaking_releases_since_baseline: ["3.0.0"]
  kurier_serviceVersion_when_pulled_baseline: "v1.26.1"
  kurier_serviceVersion_current: "v1.30.0"
  notes:
    - "fflonk is in current docs.zkverify.io supported_proofs AND in Kurier /status mainnet+testnet. Earlier note about fflonk drift was incorrect."
    - "tee is in docs.zkverify.io supported_proofs and Kurier OpenAPI enum, but NOT in live Kurier /status supportedProofs (mainnet+testnet) as of 2026-05-28."
    - "risc0 V3_0 is in zkverifyjs enum but not on docs.zkverify.io supported_proofs page yet."
    - "ultrahonk requires explicit version field since zkverifyjs 3.1.0; Legacy default preserves pre-versioning statement hash."
  pending_refresh_job: "see knowledgebase/REFRESH-REPORT.md"
```

---

## 7. Files I could not fully verify

| File / Topic | Why unverified | Recommendation |
|---|---|---|
| `proof.aggregation.yaml` event names (`Aggregate::NewProof`, `Aggregate::AggregationComplete`, `Aggregate::NewAggregationReceipt`) | The docs page `/architecture/proof-aggregation/overview` did not enumerate these specific event names in the fetched content. They appear in zkverifyjs README event-name list (`NewAggregationReceipt`, `AggregationComplete`) so the *receipt + complete* events are confirmed. `NewProof` was not visible in the docs page I fetched. | Hold as `current` based on zkverifyjs event-name evidence; spot-check against the actual zkVerify pallet source if precision matters |
| `aggregate_statementPath` RPC method name | Docs page did not show this RPC name in the section I pulled. zkverifyjs has `getAggregateStatementPath` method (camelCase JS wrapper). The underlying Substrate RPC name (`aggregate_statementPath`) is plausible but unconfirmed from public docs pull. | Hold as `current` |
| Risc0 V3_0 acceptance by Kurier | zkverifyjs SDK enum exposes `Risc0Version.V3_0` but docs.zkverify.io supported_proofs only lists `v2.1, v2.2, v2.3`. Could not determine if Kurier mainnet/testnet would accept a V3_0 proof. | Workshop should stick to V2_3 until confirmed |
| TEE in production | docs.zkverify.io says TEE supported (Intel TDX, AWS Nitro). Kurier `/status` does not list `tee` in mainnet OR testnet supportedProofs. Cannot determine if (a) TEE submission goes via a different endpoint, (b) it's enabled on the chain but not exposed by Kurier yet, or (c) docs is ahead of deployment. | Workshop should NOT plan on TEE submission via Kurier today |
| `proof_aggregation/overview` full content | The fetched content was truncated — only Domain ID and NewAggregationReceipt details came through cleanly. Aggregation ID + AggregationComplete event semantics not in the response. | Re-fetch with a more targeted prompt if precise event semantics needed |
| Handbook `example.*` files | The 3 surviving handbook examples (`example.aggregation_kurier.yaml`, `example.kurier_direct.yaml`, `example.zkverifyjs_non_aggregation.yaml`) live under `knowledgebase/handbook/` and are out of scope per the operational-only framing. | Not verified; out of scope |
| Whether VerifyTrade case YAMLs need refresh | `knowledgebase/cases/verifytrade/*` mentioned in CLAUDE.md but explicitly out of scope per user prompt | Not verified |

---

## 8. Summary of recommended actions for the user

1. **Apply §4** to overwrite `proof.systems.yaml` (after eyeballing).
2. **Apply §5** to overwrite `zkverifyjs.sdk.yaml` (after eyeballing).
3. **Apply §6** to update `INDEX.yaml` freshness block.
4. Minor in-place edits suggested (no full replacement needed):
   - `kurier.api.yaml`: bump `version_checked_2026_04_23.serviceVersion` from `v1.26.1` → `v1.30.0` (and rename key to `_2026_05_28`); add `runtimeSpecVersion: 1006002` to the response field list.
   - `runbook.local.yaml`: change `prerequisites.node` from "Kurier tutorial recommends v24.1.0" to "zkverifyjs 3.0.0+ requires Node >= 24; pin v24.x LTS".
   - `zkverifyjs.non_aggregation.yaml`: in `sdk_flow.4_execute`, change `"execute({ proofData })"` to `"execute({ proofData, domainId? })"`.
5. Consider creating new file `contract.addresses.yaml` containing the verbatim address table from §2.10. This is information the workshop needs but currently has to look up each session.
6. **Do not** remove `fflonk` from `proof.systems.yaml` — it is still supported. The earlier hunch was wrong; the actual drift is `tee` (in docs, not in Kurier).
7. After applying the file changes, run a `git diff` and re-read each replacement to confirm no semantic regression vs the 2026-04-23 baseline (the replacements are additive — no rules removed).
