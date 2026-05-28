# SETUP

## Requirements

| Item | Version | Check |
|---|---|---|
| Python | 3.11+ | `python3 --version` |
| pip | 24+ | `pip --version` |
| Node.js | 18+ (only needed if you also use Claude Code CLI) | `node --version` |
| OS | macOS / Linux / WSL | — |

Python must be 3.11+. The SDK does not support 3.10 or older. If your system Python is older, use `python3.11 -m venv .venv`.

## Install

```bash
cd workshop

python3 -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows PowerShell

pip install -r requirements.txt

cp .env.example .env
# Edit .env, set ANTHROPIC_API_KEY
```

## Two ways to run

### A. Python SDK entry (`pnl_agent.py`)

```bash
# Pass the prompt on the command line
python pnl_agent.py "Add a PnL proof circuit for ZEN/USDT"

# Or interactively (end with two blank lines)
python pnl_agent.py

# Or from an environment variable
PROMPT="..." python pnl_agent.py
```

Hitting Enter without typing a prompt uses the `DEFAULT_PROMPT` inside `pnl_agent.py` (generates the full VerifyTrade starter).

**Conversation continuity** (on by default): the SDK's `continue_conversation=True` automatically finds the most recent session in the current directory and resumes it — the agent remembers earlier turns. You don't manage session IDs by hand.

```bash
python pnl_agent.py "First, do the circuit part. Make nargo check pass."
python pnl_agent.py "Now add scripts/submit-to-zkverify.ts"   # auto-resumes
python pnl_agent.py "Change the threshold from 10 to 100"      # continues
python pnl_agent.py --new "Restart. This time use Groth16."    # force new session
```

This entry runs the Python code in this project, which wires up `post_tool_use` / `can_use_tool` / `permission_mode` / `mcp_servers`. All hooks and permission logic are explicit and inspectable.

### B. Claude Code CLI (`claude` command)

If you have [Claude Code CLI](https://claude.com/code) installed:

```bash
cd workshop
claude
```

Type your prompt in Claude Code's built-in TUI.

Claude Code reads the same `CLAUDE.md` + `.claude/skills/` + `.mcp.json`, so **project doctrine, knowledge base, skills, and MCP all take effect**. However, the Python hooks defined in `pnl_agent.py` (`post_tool_use` / `can_use_tool`) **do not**. Claude Code has its own hooks mechanism via `.claude/settings.json` (shell commands, different from the SDK's Python callbacks).

| Aspect | Python entry | Claude Code CLI |
|---|---|---|
| Prompt input | CLI arg / stdin / env var | Native TUI |
| CLAUDE.md / skills / MCP | ✅ | ✅ |
| Python hooks (`post_tool_use` etc.) | ✅ | ❌ (uses settings.json instead) |
| Authentication | ANTHROPIC_API_KEY | Also supports `claude login` (subscription auth after Jun 15) |
| Interrupt and steer mid-run | Re-run | TUI supports live steering |

Both routes drive the same project. Pick whichever feels better.

## Authentication

Right now (2026-05-28) the Agent SDK runs on API keys. Get one from the [Anthropic Console](https://console.anthropic.com) (format `sk-ant-...`) and put it in `.env`. It is billed per token and is independent of any Claude.ai subscription.

After 2026-06-15, Anthropic will roll out a subscription-auth path for the Agent SDK (Pro gets a $20/month Agent SDK credit pool, Max gets $200/month). After that lands, you can `claude login` and the SDK will use the subscription. Until then, stick with the API key.

## Verify install

```bash
source .venv/bin/activate

python -c "from claude_agent_sdk import query, ClaudeAgentOptions; print('SDK OK')"
python -m py_compile pnl_agent.py && echo "syntax OK"
ls knowledgebase | wc -l   # should be >= 23
```

All three pass → you can run `python pnl_agent.py`.

## What happens at runtime

```
Press Enter
   ↓
Python loads pnl_agent.py → asyncio.run(main())
   ↓
SDK auto-loads:
   - CLAUDE.md            (project doctrine)
   - .claude/skills/      (registers the 3 skills)
   - .mcp.json            (Context7 MCP)
   ↓
SDK sends prompt + CLAUDE.md + skills to Claude
   ↓
Claude reasons → decides to call a tool → SDK passes it through can_use_tool →
executes the tool → PostToolUse hook runs → result feeds back → Claude continues
   ↓
The async for loop prints every event to your terminal
   ↓
Loop continues until Claude says done (or fails)
   ↓
The working directory has been modified (files added / changed)
```

## Common errors

### Wrong Python version

Symptom: `pip install` reports `claude-agent-sdk requires Python>=3.11`.  
Fix: install Python 3.11+. On macOS: `brew install python@3.11`, then `python3.11 -m venv .venv`.

### API key not picked up

Symptom: 401 / `AuthenticationError` at startup.  
Fix: confirm `.env` actually contains `ANTHROPIC_API_KEY=sk-ant-...`.

⚠️ Note: if `ANTHROPIC_API_KEY` was previously `export`ed in your shell, **the shell value overrides `.env`** — this is dotenv's default behavior (it does not overwrite existing env vars). Workaround: `unset ANTHROPIC_API_KEY`, or open a fresh terminal.

### First call hangs

Symptom: nothing happens for ~10 seconds after `python pnl_agent.py`.  
Cause: SDK is streaming; the first token can take several seconds.  
Fix: wait 10s. Still nothing? Ctrl+C and look at the stack trace.

### Agent re-reads the same file

Symptom: you see the agent calling `Read knowledgebase/INDEX.yaml` multiple times in the same run.  
Cause: context compaction dropped earlier reads.  
Fix: add a directive in CLAUDE.md like "Read INDEX.yaml once and keep its contents in working memory."

### CLAUDE.md edits don't change agent behavior

Cause: the SDK loads CLAUDE.md once per session.  
Fix: exit and re-run (new process = new session = re-load).

### A skill isn't being found

Symptom: agent acts as if the skill doesn't exist.  
Cause: wrong path, or the SKILL.md frontmatter is missing `name:` / `description:`.  
Fix: check that the path is `.claude/skills/<skill-name>/SKILL.md`, and that the frontmatter has both required fields.

### Tokens burn fast

Symptom: a few runs and your balance is gone.  
Cause: the agent is looping on a wrong assumption.  
Fix: CLAUDE.md already has a hard rule ("if the same tool fails twice, stop and ASK_USER") — check that it is still in effect and hasn't been edited away.

## Modify and extend

| Goal | Where to edit |
|---|---|
| Change the agent's doctrine | `CLAUDE.md` |
| Add a skill | `.claude/skills/<new-name>/SKILL.md` |
| Change the default prompt | `os.environ.get("PROMPT", ...)` in `pnl_agent.py` |
| Add a verification hook | `post_tool_use` in `pnl_agent.py` |
| Block a class of commands | `can_use_tool` in `pnl_agent.py` |
| Switch model | `ClaudeAgentOptions(model="claude-opus-4-...")` |
| Add an MCP server | `ClaudeAgentOptions(mcp_servers={...})` or `.mcp.json` |
