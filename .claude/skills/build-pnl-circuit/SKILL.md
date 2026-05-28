---
name: build-pnl-circuit
description: Generate a PnL proof circuit skeleton (Noir/UltraHonk preferred), including input definitions, verification function, and test fixtures.
---

# build-pnl-circuit · PnL circuit generation skill

## ⚠️ Step 0 · Mandatory version alignment check (skipping this guarantees failure)

In the VerifyTrade debugging day, **roughly half the failure time** went into Noir / bb / bb.js version mismatches. The error messages were always indirect signals like "deserialize" / "format marker" / "byte length".

**Before doing anything**, the agent must run these via Bash and paste back the output:

```bash
nargo --version    # must be 1.0.0-beta.6
bb --version       # must be 0.84.0
node -e "console.log(require('@aztec/bb.js/package.json').version)"      # must be 0.84.0
node -e "console.log(require('@noir-lang/noir_js/package.json').version)" # must be 1.0.0-beta.6
```

**If any one is off**, do not generate the circuit. Stop and ASK_USER:
> Current nargo=X / bb=Y, not within the locked version range (locks are in knowledgebase/cases/verifytrade/verifytrade.architecture.yaml).
> Pin the versions first, or accept the current ones (verify may fail)?

The full lock table is in the `version_lock` section of `knowledgebase/cases/verifytrade/verifytrade.architecture.yaml`.

## Workflow

1. **Pick the proof system** — default Noir + UltraHonk (this project is anchored to bb 0.84.0).
   If the user explicitly wants Groth16, invoke [[lookup-zkverify]] and read `proof.systems.yaml` to confirm zkVerify supports it.

2. **PnL data source — locked, do not ask again**
   This project's PnL **uses the `realizedProfit` field directly from the Binance bapi response** (captured by the TLSNotary extension from the user's logged-in binance.com session, then parsed in the browser).
   - Do not ASK_USER "what counts as PnL"
   - Do not write sum(profits) - sum(losses) or final - initial recomputation logic
   - See the `flow` section of `knowledgebase/cases/verifytrade/verifytrade.architecture.yaml`
   - Only fall through to ASK_USER if the user **explicitly** says "I'm not building VerifyTrade, I want a different PnL definition".

3. **Generate the circuit file** at `circuits/pnl.nr` (Noir), containing:
   - public inputs: account_id, claimed_pnl, time_range, attestation_hash
   - private inputs: realizedProfit_from_attestation, binding_fields (chainId, userAddr, timestamp, anti-replay)
   - verification logic: assert that the private realizedProfit equals claimed_pnl, and Poseidon-commit the binding fields
   - **Do not** recompute PnL in the circuit — trust the Binance value signed under the TLSN attestation.

4. **bb compile must carry the right flags** (Noir path):
   ```bash
   nargo compile                       # produces ACIR
   bb write_vk --oracle_hash keccak    # vk hash must match the on-chain algorithm
   bb prove --oracle_hash keccak       # same
   ```
   **Missing `--oracle_hash keccak` → vk hash disagrees with zkVerify Volta → verify returns false.**

5. **Generate fixtures** at `circuits/fixtures/sample_trades.json`

6. **Run the tests**: `npm run circuit:test`. Fix on failure.

## Invariants

- Never emit a private input as a public output
- Always assert a range check (overflow guard)
- Always include component-level comments in .nr / .circom explaining what each constraint guards against
- **Generated bb.js calls must pass `{ keccak: true }` explicitly** — otherwise the oracle hash at prove time disagrees with the vk hash.

## Failure patterns (from the debug retro)

| Error message | Real root cause | Fix |
|---|---|---|
| `invalid format marker` | nargo / noir_js versions mismatched | Pin to the same minor |
| `unexpected byte length` | bb / bb.js versions mismatched | Pin both to 0.84.0 |
| `vk hash mismatch` | Forgot `--oracle_hash keccak` | Add the flag at compile time |
| Verify returns false on-chain but format looks right | UltrahonkVersion selected wrong | V0_84 + Variant.Plain |

Full cross-reference: the `noir_*` / `bb_*` / `keccak_*` entries in `knowledgebase/cases/verifytrade/verifytrade.debug-retro.yaml`.
