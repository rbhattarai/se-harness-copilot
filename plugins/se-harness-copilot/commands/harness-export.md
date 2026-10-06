---
description: Export the agent roster and enforcement hooks to this repo's .github/ for the Copilot coding agent on github.com, with an honest capability report.
argument-hint: <agents|hooks|all>
---

# /harness-export — repo-level Copilot export

The `se-harness-copilot` plugin already gives Copilot CLI the agents, skills and commands. This
command vendors them **into the repo** so the surfaces that don't load plugins (the Copilot
coding agent on github.com, teammates without the plugin) get them too. `$ARGUMENTS` selects
`agents`, `hooks`, or `all` (default).

## Step 1 — Instructions layer (verify, don't convert)
Confirm AGENTS.md exists with the generated block (run `/harness-init` first if not). Copilot
reads AGENTS.md (root + nested) natively — nothing to convert.

## Step 2 — Agent roster
```
bash tools/harness/export-agents.sh copilot .
```
Writes `.github/agents/<name>.md` agent profiles (name/description frontmatter, body verbatim,
tool restrictions carried as body guidance). Org/enterprise-wide distribution: move the
profiles to the org's `.github-private` repo.

## Step 3 — Hooks
Copilot lifecycle hooks (`.github/hooks/*.json` —
[reference](https://docs.github.com/en/copilot/reference/hooks-reference)) deny with JSON
`permissionDecision` output; **exit 2 does not block**, other non-zero exits fail-closed. Export
via the bundled adapter — never wire the gate scripts in directly:
```
mkdir -p tools/harness .github/hooks
cp tools/harness/{copilot-hook-adapter.sh,gate-check.sh,org-validate.sh,memory-log-commit.sh,contract-check.sh} tools/harness/
cp ../se-harness-copilot/templates/copilot-hooks.json .github/hooks/se-harness.json
```
Tell the user to verify the gate actually denies (payload field names differ between the coding
agent and CLI surfaces) and that hooks do NOT run in VS Code Chat.

## Step 4 — MCP layer
Point the user at this project's `.mcp.json` / Copilot's MCP configuration for each surface.
Do not duplicate server configs — reference, don't fork.

## Step 5 — Honest capability report (always end with this)
| Surface | Carries over? |
|---|---|
| AGENTS.md instructions | ✅ native on every Copilot surface |
| Agent roster | ✅ `.github/agents/` profiles — no tool-scoping parity |
| HITL gates (hooks) | ✅ Copilot CLI + coding agent via adapter (Step 3) · ❌ VS Code Chat — AGENTS.md workflow text + CI are the enforcement there |
| Skills (context-injector, wiki-*, grill) | ✅ Copilot CLI plugin · ⚠ elsewhere conventions survive as instructions, automation doesn't |
| MCP servers | ✅ via each surface's MCP config |
| `.harness/` artifacts (profile, REQs, memory) | ✅ plain files — any surface can read them |
