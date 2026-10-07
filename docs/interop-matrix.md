# se-harness-copilot surface matrix: GitHub Copilot (2026-07-16)

How each framework component ships on each Copilot surface. Details: `docs/copilot/platform-notes.md`.

| Component | Copilot CLI | Coding agent (github.com) | VS Code Chat |
|---|---|---|---|
| Marketplace | `.github/plugin/marketplace.json` — `copilot plugin marketplace add owner/repo` | n/a | n/a |
| Plugin | `plugins/se-harness-copilot` (`plugin.json` at root) | not loaded — use repo-level files | not loaded — use repo-level files |
| Commands / goal loop | plugin `commands/` **and** each command as a skill (`skills/harness-*/SKILL.md`, invoked `copilot harness-goal …`); script paths use `tools/harness/` | `.github/prompts/*.prompt.md` | `.github/prompts/*.prompt.md` |
| Agents (12-role roster) | plugin `agents/*.agent.md` (tool scoping as body guidance) | `.github/agents/*.md` via `export-agents.sh copilot` | same |
| Skills (8 harness + 9 command-derived) | `skills/<name>/SKILL.md` | — | — |
| Workspace orchestration (`workspace-plan.md`, `workspace-orchestrator` agent) | ✅ full FS access; sibling repo checked first with `[ -d <sibling-path> ]` | ❌ ephemeral single-repo sandbox — goes straight to the manual per-repo handoff | ⚠️ only if the sibling folder is in the open multi-root workspace; otherwise handoff |
| Hooks: gate-check, contract-check (blocking) | bundled `hooks.json` (plugin-root-relative paths) via `copilot-hook-adapter.sh` (exit 2 → deny JSON) | repo-level `.github/hooks/se-harness.json` via the adapter | repo-level hooks (VS Code honors exit 2 and deny JSON) |
| Hooks: org-validate, memory-log (feedback) | adapter `post` mode (never fails closed) | same | same |
| Hooks: inject-context | `userPromptSubmitted` exists — context-injection effect still **unverified**; not wired yet | same | `UserPromptSubmit` — unverified |
| MCP (github, atlassian, code-graph) | plugin `.mcp.json` / enterprise-managed | repo MCP config | `.vscode/mcp.json` |
| Instructions | `AGENTS.md` native; optional thin `.github/copilot-instructions.md` pointer | same | same |
| `.harness/` artifacts (profile, REQs, memory, lock) | plain files | plain files | plain files |
| Enterprise distribution | enterprise-managed plugins (auto-install, forced hooks/MCP) | `.github-private` agent profiles | — |

**Design rule:** the durable behavior lives once — commands, agents, skills, scripts, templates
in the plugin — and surface adapters stay thin (`copilot-hook-adapter.sh`, `export-agents.sh`).
If supporting a surface requires editing workflow *content*, the content is in the wrong place.

**Not yet wired:** the context-injection hook (see matrix row) and skill auto-activation parity
across surfaces (observe in practice).
