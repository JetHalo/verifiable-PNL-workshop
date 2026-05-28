---
name: wire-zkverify-submission
description: Submit a generated proof through zkVerifyJS to the zkVerify testnet and obtain an aggregationId.
---

# wire-zkverify-submission · zkVerify submission skill

## Mandatory prerequisites

Before invoking this skill, you **must** call [[lookup-zkverify]] and read:
- `knowledgebase/zkverifyjs.sdk.yaml` (real SDK API signatures)
- `knowledgebase/zkverifyjs.non_aggregation.yaml` (the simplest submission mode)
- `knowledgebase/cases/verifytrade/verifytrade.debug-retro.yaml` (pitfalls encountered on this pipeline)

**Do not write zkVerifyJS calls from memory.** The model has limited exposure to this SDK and tends to hallucinate.

## Workflow

1. Write a wrapper module at `app/lib/zkverify.ts` exposing:
   - `submitProof(proof, publicInputs)` — submit and wait for an aggregationId
   - `pollAggregation(txHash)` — poll until the aggregationId is available
2. Call that wrapper from `app/api/submit/route.ts`.
3. Run an end-to-end fixture proof (from generation to aggregationId).

---

## ⚠️ Four known on-chain verify pitfalls (from the VerifyTrade retro)

Source: the `zkverify_*` entries in `knowledgebase/cases/verifytrade/verifytrade.debug-retro.yaml`.
**Hitting any one of these makes native verify return false.** Generated code must avoid all four.

### ① proof must be a 0x-prefixed hex string, not a Buffer

```ts
// ❌ Wrong: passing a Buffer directly
submitProof(proofBuffer, publicSignals)

// ✅ Right: convert to 0x hex
const proofHex = '0x' + Buffer.from(proofBuffer).toString('hex')
submitProof(proofHex, publicSignals)
```

### ② Every entry in publicSignals must have a 0x prefix

```ts
// ❌ Wrong: missing 0x
const publicSignals = [account_id, pnl_value, time_range]

// ✅ Right: prefix each
const ensureHex = (s: string) => s.startsWith('0x') ? s : '0x' + s
const publicSignals = [account_id, pnl_value, time_range].map(ensureHex)
```

### ③ Every publicSignal must be padded to 32 bytes

```ts
// ❌ Wrong: short value not padded
'0xabc'   // length 5

// ✅ Right: padStart(64, '0') then prefix
const pad = (hex: string) => '0x' + hex.replace(/^0x/, '').padStart(64, '0')
const publicSignals = raw.map(pad)
```

### ④ UltrahonkVersion must match the bb version

```ts
import { UltrahonkVersion, Variant } from 'zkverifyjs'

// ✅ This project (bb 0.84.0) uses:
const config = {
  version: UltrahonkVersion.V0_84,
  variant: Variant.Plain,
}
```

bb 0.72.x uses V0_72; bb 0.56.x uses V0_56. **Mismatched version → on-chain panic.**

---

## ⚠️ zkverifyjs v3+ API rename — don't use attestationId

```ts
// ❌ Wrong: old API
const id = await tx.attestationId   // undefined!

// ✅ Right: v3+ new name
const id = await tx.aggregationId
```

---

## Verification gates (run automatically in PostToolUse)

- TypeScript must pass `tsc --noEmit`
- A fixture submission must run end-to-end and yield a readable aggregationId before we call it done
- Any try/catch must log the error to the console — no silent swallowing

## Minimum reference: a complete submission

See the `chain` section of `knowledgebase/cases/verifytrade/verifytrade.architecture.yaml` for the canonical field definitions (the key field definitions are inlined in that yaml).
