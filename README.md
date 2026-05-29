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
Based on this repo's CLAUDE.md and knowledgebase/cases/verifytrade/workshop-deliverable.yaml,
generate a complete ZK-TLS PnL verification project from scratch, with 8 components:
circuit / prover / contracts / scripts / frontend / plugin / notary-server / docs.

Goal: Use TLSNotary to capture the realizedProfit field from Binance bapi,
use a Noir UltraHonk circuit to assert PnL > threshold, submit via zkverifyjs
to zkVerify Volta to obtain an aggregationId, have a Solidity contract on Base
consume the attestation and maintain a leaderboard, coordinate the flow in a
Next.js frontend, and persist data via a JSON file store
(frontend/lib/storage.ts + frontend/data/state.json) instead of a separate DB.

Version selection:
- Default to the latest versions in the current_latest section of
  knowledgebase/version.alignment.yaml (Rule ①).
- If you want to strictly reproduce the original VerifyTrade demo, use
  project_anchors.verifytrade instead.
- Either way, run the verify_commands and stop + ASK_USER on any mismatch
  (skipping this violates Rule ④ of the Version Lock Mandate in CLAUDE.md).
- For components not listed in version.alignment.yaml, look them up via the
  Context7 MCP or fetch the official release page.

Strictly follow:
- The version alignment mandate, 7 hard rules, and failure-loop constraint in CLAUDE.md
- The key_invariants and must_pass for every component in
  knowledgebase/cases/verifytrade/workshop-deliverable.yaml

Once finished, run each component's must_pass commands plus
scripts/e2e-mock-test.sh; it must print "E2E MOCK PIPELINE PASSED" on the last
line before the deliverable is considered complete.
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
