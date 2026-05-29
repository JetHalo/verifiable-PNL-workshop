# Workshop · PnL × zkVerify Agent

A ZK-TLS PnL demo project built on the Claude Agent SDK. One prompt generates a complete VerifyTrade-style starter: Noir circuit / Rust prover / Solidity contracts / TypeScript scripts / Next.js frontend / TLSNotary plugin / Railway notary deploy package / docs.

## Environment

Required before you start:

| Item | Version | Check |
|---|---|---|
| Python | 3.11+ | `python3 --version` |
| Node.js | 18+ (for verification of generated components) | `node --version` |
| Git | 2.x+ | `git --version` |
| OS | macOS / Linux / WSL | — |
| **Anthropic API Key** | balance ≥ $20 | [console.anthropic.com](https://console.anthropic.com) |

Optional (deeper generation / verification):

| Tool | Used for |
|---|---|
| `nargo` 1.0.0-beta.6 | Compiles the generated Noir circuit |
| `bb` 0.84.0 (via `bbup`) | Runs circuit prove / verify |
| Rust + cargo | Builds the generated prover CLI |
| Foundry (`forge`) | Runs Solidity tests |
| pnpm | Installs frontend + scripts deps |

Full install + troubleshooting in [SETUP.md](./SETUP.md).

## Quick start

```bash
# 1. Install Python deps
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure API key
cp .env.example .env
# Edit .env, set ANTHROPIC_API_KEY

# 3. Generate
python pnl_agent.py "<paste the prompt below>"
```

## Generation prompt

Paste this into the command above and the agent will generate a complete VerifyTrade-style project from scratch:

```
Build me a "verifiable trading leaderboard" web app.

What users can do:
- Place a few trades on Binance Futures Testnet, then use my Chrome extension
  to "notarize" the trade history of the current session into a ZK-TLS
  attestation (TLSNotary).
- Use a Noir UltraHonk circuit to prove "my realizedProfit over this window
  exceeds threshold X" - taking the realizedProfit field from the Binance
  response as a private input, never revealing individual trades.
- Submit the proof to zkVerify (Volta testnet) and wait for finalize to get
  back an aggregationId.
- The frontend immediately writes this submission (identity / tradeCount /
  volume / pnl / aggregationId / blockHash / txHash) into state.json. The
  current round's leaderboard updates, sorted by PnL descending.
- The site is publicly accessible; anyone can view the leaderboard.

The leaderboard data lives **in a JSON file on the frontend server**, **not on
any chain**. zkVerify submission + receiving the aggregationId is the end of
the on-chain path; no Solidity contract / Base / any EVM chain consumes the
attestation. state.json is the source of truth.

Please generate all 8 components:
- circuit/        Noir circuit
- prover/         Rust CLI (runs MPC-TLS or Proxy mode, assembles proof, shells
                  out to bb)
- contracts/      Solidity Competition contract + Foundry test.
                  Note: this is a "ready-made reference implementation for a
                  future on-chain version", **not part of the live demo path**.
                  forge test must still pass, but the frontend does not call it.
- scripts/        TypeScript ops scripts (zkverifyjs submit / mock data / e2e
                  test)
- frontend/       Next.js 14 dApp (home / submit / rounds / leaderboard /
                  admin). Persistence uses a JSON file (lib/storage.ts +
                  data/state.json); no separate DB; no contract calls — after
                  submitting the proof to zkVerify and getting an
                  aggregationId, call appendSubmission() to write state.json.
- plugin/         TLSNotary Chrome extension (config.json declares the Binance
                  bapi endpoint)
- notary-server/  Railway one-click deploy package (Dockerfile + railway.toml
                  + key-gen script)
- docs/           README + architecture diagram + dev guide

Key pitfalls to avoid (CLAUDE.md and knowledgebase have the full list; the
most-forgotten ones are):
- Don't recompute PnL inside the circuit. Trust the realizedProfit from the
  attestation.
- Proof generation must be browser-only. The seed phrase must be server-only.
- Lock versions to the current_latest section of
  knowledgebase/version.alignment.yaml. Run verify_commands before generating
  code; on a mismatch, stop and ask me.
- The TLSNotary verifier must be deployed to region asia-southeast1 (Binance
  enforces geo restrictions).
- Writes to state.json must go through the mutex + atomic-rename path in
  lib/storage.ts; do not let two concurrent POSTs call fs.writeFile directly.

Done when:
- Every component's own must_pass passes (nargo test / forge test / tsc
  --noEmit / etc.).
- Finally, scripts/e2e-mock-test.sh prints "E2E MOCK PIPELINE PASSED" on its
  last line.
```

Paste the whole block in one shot; the agent will run for 10–30 minutes and then all 8 components should be in place.

## Iteration and modification

The first run rarely lands at 100% satisfaction. This entry point keeps `continue_conversation=True` by default — follow-up commands automatically resume the latest session, and the agent remembers what it generated.

### Modify a component

```bash
python pnl_agent.py "Modify circuit/src/main.nr: change the threshold formula to sum(positive_trades) - sum(negative_trades) > x"
```

### Add a feature

```bash
python pnl_agent.py "Add a /history page in frontend that lists all past submissions for a given wallet"
```

### Fix a bug

```bash
# If you saw a test failure during generation, tell the agent directly:
python pnl_agent.py "Earlier, forge test failed: testClaim reverted with 'NULLIFIER_USED'. Fix it."
```

### Start over

```bash
python pnl_agent.py --new "Regenerate, this time use Groth16 instead of UltraHonk"
```

### Inspect changes / roll back

```bash
git status                    # files the agent added / modified
git diff                      # detailed diff
git add . && git commit -m "iter 1"    # happy: lock it in
git reset --hard HEAD~1       # unhappy: roll back to previous commit
```

### Interrupt and resume

`Ctrl+C` while running. Next `python pnl_agent.py "..."` will resume from where it stopped.

### Force a fresh conversation

```bash
python pnl_agent.py --new "..."
```

`--new` discards the recent session memory; the agent starts fresh.

### Debug the run

Save the full event stream for later review:

```bash
python pnl_agent.py "..." 2>&1 | tee runs/$(date +%H%M%S).log
```

Inspect `runs/HHMMSS.log` after the run to see every step the agent took, every tool call, and where it failed.

## Directory layout

```
workshop/
├── pnl_agent.py              # Entry script
├── CLAUDE.md                 # Project doctrine for the agent
├── requirements.txt
├── .env.example
├── .mcp.json                 # Context7 MCP config
│
├── .claude/skills/           # 3 skills the agent invokes
│   ├── lookup-zkverify/
│   ├── build-pnl-circuit/
│   └── wire-zkverify-submission/
│
└── knowledgebase/            # Local knowledge base
    ├── INDEX.yaml            # Directory + freshness header
    ├── *.yaml                # 23 protocol / SDK / API references
    ├── cases/verifytrade/    # Project case + debug history + deliverable spec
    └── handbook/             # Generic examples
```

## How the 5 Harness subsystems map here

| Subsystem | Location |
|---|---|
| Instructions | `CLAUDE.md` (loaded by the SDK at startup) |
| State | `knowledgebase/` + automatic context compaction |
| Verification | `post_tool_use` hook in `pnl_agent.py` |
| Scope | `allowed_tools` / `can_use_tool` / `permission_mode` in `pnl_agent.py` |
| Lifecycle | `hooks` dict in `pnl_agent.py` (binds to the SDK's 7 lifecycle hook points) |

Environment setup and common issues are in [SETUP.md](./SETUP.md).
