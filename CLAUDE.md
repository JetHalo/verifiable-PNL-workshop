# Mushanghai Workshop · PnL × zkVerify Agent

A starter workshop project built on the Claude Agent SDK. The goal: let the agent
generate a small app that produces a PnL proof and submits it to zkVerify
(reference implementation: VerifyTrade).

---

## Project doctrine (Instructions subsystem)

### Knowledge source — three-tier structure, queried in priority order

The knowledgebase is split into three tiers; query them **from highest to lowest priority**:

1. **`knowledgebase/*.yaml` — OPERATIONAL** (protocol-level facts)
   - Current spec / schema / API shapes for zkVerify / zkVerifyJS / proof systems / Kurier
   - This tier is the "current standard", aligned with the architecture/overview docs on docs.zkverify.io
   - All code generation must take this as the source of truth
2. **`knowledgebase/cases/<project>/` — project-level case study**
   - Current case: `cases/verifytrade/` (VerifyTrade debug retrospective + architecture + version lock)
   - When the task is on the same stack, reuse the pitfalls captured here
3. **`knowledgebase/handbook/example.*.yaml` — generic examples**
   - Only consult when the operational + cases tiers can't resolve your question
   - Not a main entry; may drift from the current SDK

**Entry point:** Always read `knowledgebase/INDEX.yaml` first — it explains the three tiers' coverage and freshness state.

**Do not generate zkVerifyJS / TLSNotary / Noir / bb API calls from model memory** — grep / read the relevant yaml first.

### Code conventions

- Python entry: `pnl_agent.py` (single file, easy to read)
- Custom skills go under `.claude/skills/<skill-name>/SKILL.md`
- Generated circuit code → `circuits/`
- Generated contract code → `contracts/`
- Generated frontend code → `app/`

### Prohibited actions

- Never read or write `.env`
- Never run `rm` / `curl` / `wget` or any destructive or network bash commands
- Never run `git push` directly — push requires a human-in-the-loop confirmation

### Verification gates

- After any edit to a `.circom` or `.nr` file, automatically run the corresponding circuit test (PostToolUse hook)
- After any edit to a zkVerifyJS call, the file must import successfully without type errors

### Task scope + Definition of Done

The current workshop task: **a participant enters a single prompt → the agent generates a complete VerifyTrade-style starter project from scratch**.

**All 8 components are in scope, nothing is "out of band":**
1. circuit (Noir circuit)
2. prover (Rust CLI)
3. contracts (Solidity + Foundry)
4. scripts (TypeScript ops)
5. frontend (Next.js 14)
6. plugin (TLSNotary Chrome extension)
7. notary-server (Railway deploy package: Dockerfile + railway.toml + config)
8. docs (architecture + dev guide)

**The precise "done" definition** lives in `knowledgebase/cases/verifytrade/workshop-deliverable.yaml`, which contains:
- Each component's intent + key_invariants (hard constraints) + must_pass (verification commands)
- Acceptance conditions (how the agent declares done)
- Cross-references (concrete constraints live in skills + other yamls; not duplicated here)

**Must read before generation:** `workshop-deliverable.yaml` is this project's "acceptance contract". You may not start generating code without reading it first.

**Note:** `workshop-deliverable.yaml` only defines **boundaries** (what each component must do, what invariants it must satisfy, what commands must pass). It does **not** prescribe an exact file list. The agent decides the concrete file structure, as long as each component passes its must_pass and satisfies its key_invariants.

**Out of scope:** real trading, KYC, matching engine logic. That's it.

---

## Seven hard rules distilled from a day of VerifyTrade debugging

These 7 rules are **lessons paid for in blood** during the day that took the demo from broken to working.
The agent **must** follow them in any related decision; no skipping allowed.

### ① Don't assume upstream APIs are stable (alpha / pre-1.0 software)

PSE removed the entire `notary-server` directory from the repo at alpha.13, with no deprecation, no migration guide.
**Countermeasure:** for any alpha / pre-1.0 software, `git diff workspace members` before every upgrade.

### ② Don't try to force MPC across cloud edge proxies

MPC over Railway / Fly / Cloudflare edges almost always deadlocks (Nagle / buffering).
**Countermeasure:** for any ZK-TLS project, get **Proxy mode** working first; reserve MPC mode for self-hosted colocation.

### ③ Reverse-engineer assuming "the user does nothing extra"

The whole premise of ZK-TLS is "the user is already logged in". Any scheme that requires the user to configure extra things (API key / HMAC signature / self-managed wallet) targets a user group that already understands ZK and doesn't need ZK-TLS.
**Countermeasure:** before writing a plugin, capture real traffic in the browser Network tab and reverse-engineer the actual cookie-auth endpoints.

### ④ Treat version alignment as a "vertical stack" problem

Noir + bb is a **vertical stack**: nargo → ACIR → bb prove/write_vk → bb.js runtime → zkVerify pallet.
A mismatch in any layer fails everything downstream, and the error messages are always indirect signals like "deserialize" / "format marker".
**Countermeasure:** pin an anchor version (this project: `bb 0.84.0`, dictated by what zkVerify Volta supports), and **pin everything else to match it**.
The full version table is in `knowledgebase/version.alignment.yaml`.

### ⑤ Geo restrictions are not a "maybe", they are a certainty

Any financial service (Binance / Coinbase / exchanges) does IP-based geo filtering. A US-based Railway IP calling binance.com (not .US) almost always returns 451.
**Countermeasure:** when deploying a ZK-TLS verifier, **the region must follow the target server's permitted regions**, not the developer's convenience.
Current production: `asia-southeast1` (Singapore).

### ⑥ Routes must be explicit

A `/submit` endpoint that picks the round itself ("I know better than the user") is an anti-pattern. If the user is on `/leaderboard/2` and clicks Submit, they want to submit to Round 2.
**Countermeasure:** any potentially ambiguous page entry must carry an explicit parameter (`?round=N`). No parameter → show a picker UI, never silently fall back.

### ⑦ Tracing logs beat human-readable error messages

The MPC `accept()` deadlock looked invisible under `RUST_LOG=info`. We needed `RUST_LOG=warn,tlsn=trace,mpc_tls=trace` to see it.
**Countermeasure:** any ZK / MPC / crypto-related service should ship with trace logging enabled. Don't add logs and redeploy after a failure.

---

## Version Lock Mandate

The ZK toolchain is a **vertical stack** (nargo → ACIR → bb → bb.js → zkVerifyJS → zkVerify pallet).
A mismatch in any layer fails everything downstream, and error messages are always indirect signals like "deserialize" / "byte length" / "format marker".

**Therefore the agent must execute the following 4 rules without exception in any version-related decision:**

### Rule ①: Default to the latest stable version

For new projects with no legacy constraints, **lock all components to the latest stable**.
The current latest is given by the `current_latest` block in `knowledgebase/version.alignment.yaml`.
Read that yaml before querying — do not assume version numbers from memory.

### Rule ②: Every component must be version-checked explicitly

Before generating or modifying any code, config, Dockerfile, or package.json:

```
For each component involved (nargo / bb / bb.js / noir_js / zkverifyjs / kurier / Node / Python ...)
  Explicitly run `<tool> --version` or `cat package.json` to read the actually installed version
  Compare against the target in knowledgebase/version.alignment.yaml
  Mismatch → stop and ASK_USER immediately. Do not proceed.
```

**Prohibited**: generating imports / API calls / configs from a guess about "what version is probably installed".

### Rule ③: When pinning a low version, the whole vertical stack must drop to match

If the project locks a low version for legacy reasons (e.g. VerifyTrade locks `bb 0.84.0`),
**the rest of the vertical stack must match the anchored version**. Do not silently upgrade other pieces:

- `bb 0.84.0` → pair with `nargo 1.0.0-beta.6` + `bb.js 0.84.0` + `@noir-lang/noir_js 1.0.0-beta.6`
- zkVerifyJS upgraded to 3.x → pair with Node ≥ 24, install snarkjs explicitly (3.0 dropped the transitive dep)
- Ultrahonk running on the anchored bb 0.84.0 → zkverifyjs calls must specify `version: V0_84` explicitly (not let it default to Legacy)

Change the anchor, change the whole stack. **Mixed old + new is not allowed.**

### Rule ④: These checks are **mandatory**, not "recommendations"

The agent must not:
- Skip the version check and jump straight to code generation
- Assume "this version probably still works since it worked last time"
- Ignore a red `--version` error and proceed
- Defer a version mismatch as "not urgent, do something else first"

**Version-check failure = stop immediately + ASK_USER.** This is at the same priority level as the "failure-loop constraint" below.

---

## Failure-loop hard constraint

**If any tool (Edit / Bash / network call) fails twice in a row, stop and ASK_USER. Do not keep guessing.**

Reason: when the agent loops freely, token burn is rapid, and it usually drifts further from the truth on a wrong premise.
The correct action is to report the observed facts and the stuck point to the user, and let a human decide the next step.

---

## Complete debug history

If you encounter what looks like a previously-seen failure, consult:
- `knowledgebase/cases/verifytrade/verifytrade.debug-retro.yaml` — the 12-chapter retrospective distilled into an error → fix table
- `knowledgebase/cases/verifytrade/verifytrade.architecture.yaml` — final architecture + version lock table
