"""PnL x zkVerify Agent — Claude Agent SDK entry point.

Usage:
    python pnl_agent.py "your prompt"         # pass on command line
    python pnl_agent.py                        # interactive input
    PROMPT="..." python pnl_agent.py           # pass via environment variable

Conversation continuity (default):
    The SDK's continue_conversation=True automatically picks up the most recent
    session in the current directory. The agent remembers earlier turns; you
    do not have to manage session IDs.

    python pnl_agent.py "First, do the circuit"     # new session
    python pnl_agent.py "Now add scripts"            # auto-resumes the previous
    python pnl_agent.py --new "Restart from scratch" # force a fresh session

Environment:
    Requires ANTHROPIC_API_KEY (in .env or as an environment variable).
"""
import asyncio
import os
import sys
from claude_agent_sdk import query, ClaudeAgentOptions


# --- (3) + (5) Verification + Lifecycle -------------------------------
# After every Edit on a .circom file, run the circuit tests automatically.
# Failures are fed back to the agent so it can iterate.
async def post_tool_use(event):
    if event.tool_name == "Edit" and event.file_path.endswith(".circom"):
        # In the real project this runs `npm run circuit:test`.
        # Stubbed here; the workshop repo will wire the real command in.
        return {"observation": "[stub] circuit test would run here"}
    return None


# --- (4) Scope --------------------------------------------------------
# Intercept dangerous bash commands (rm / curl / wget) so the agent cannot
# accidentally delete files or pull from the network.
async def can_use_tool(name, params):
    if name == "Bash":
        cmd = params.get("command", "")
        for danger in ("rm ", "curl ", "wget ", "git push"):
            if danger in cmd:
                return False
    return True


DEFAULT_PROMPT = """Based on this repo's CLAUDE.md and knowledgebase/cases/verifytrade/workshop-deliverable.yaml,
generate a complete VerifyTrade-style ZK-TLS PnL project from scratch, with 8 components:
  circuit / prover / contracts / scripts / frontend / plugin / notary-server / docs

Generation guidelines:
1. Read knowledgebase/INDEX.yaml first to understand the knowledge base layout
2. Strictly follow the project doctrine in CLAUDE.md and the version alignment mandate
3. Satisfy every component's key_invariants in workshop-deliverable.yaml
4. After generation, run each component's must_pass commands and scripts/e2e-mock-test.sh;
   the last line must print "E2E MOCK PIPELINE PASSED" before you are done.

Get to work. workshop-deliverable.yaml defines the acceptance boundaries; you choose the
concrete file structure."""


def use_continue_conversation() -> bool:
    """--new forces a new session (default: continue the most recent one)."""
    if "--new" in sys.argv:
        sys.argv.remove("--new")
        return False
    return True


def get_prompt() -> str:
    """Priority: CLI arg > PROMPT env var > interactive input > DEFAULT_PROMPT."""
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:])
    if os.environ.get("PROMPT"):
        return os.environ["PROMPT"]
    if sys.stdin.isatty():
        print("Enter your prompt (end with two blank lines, or just Enter for the default):\n> ", end="", flush=True)
        lines = []
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line == "" and lines:
                break
            if line == "" and not lines:
                return DEFAULT_PROMPT
            lines.append(line)
        return "\n".join(lines) or DEFAULT_PROMPT
    return DEFAULT_PROMPT


async def main():
    prompt = get_prompt()
    cont = use_continue_conversation()

    print(f"\n--- {'resuming most recent session' if cont else 'starting a new session'} ---", flush=True)
    print(f"--- Prompt ---\n{prompt}\n--- Start ---\n", flush=True)

    options = ClaudeAgentOptions(
        # (4) Scope — three-layer permissions
        allowed_tools=[
            # Local files / commands
            "Read", "Edit", "Bash", "Glob", "Grep",
            # Online docs fallback — when the knowledge base is silent or stale, the agent
            # can pull live pages from the official sources
            "WebFetch",
            # Context7 MCP — structured up-to-date docs for popular libraries
            # (Noir / Circom / zkVerify SDK and many more)
            "mcp__context7__resolve-library-id",
            "mcp__context7__get-library-docs",
        ],
        permission_mode="default",
        can_use_tool=can_use_tool,
        # (3) + (5) Verification + Lifecycle — hook
        hooks={"PostToolUse": post_tool_use},
        # External MCP server: Context7 feeds the latest library docs to the agent
        mcp_servers={
            "context7": {
                "command": "npx",
                "args": ["-y", "@upstash/context7-mcp"],
            },
        },
        # Conversation continuity: SDK finds the most recent session in cwd and resumes it
        continue_conversation=cont,
    )

    async for message in query(prompt=prompt, options=options):
        # (2) State — real-time event stream
        print(message)


if __name__ == "__main__":
    asyncio.run(main())
