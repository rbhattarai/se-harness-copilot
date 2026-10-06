# se-harness-copilot

**An AI-agentic SDLC harness for GitHub Copilot that you can bootstrap around any software
project — new or existing, any stack, from a single repo to a multi-repo product. AI agents
do the work; hooks make sure they can't ship without you.**

[![license](https://img.shields.io/github/license/rohanbhattaraidev-beep/se-harness-copilot?label=license&color=97ca00)](./LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/rohanbhattaraidev-beep/se-harness-copilot/ci.yml?branch=main&label=CI)](https://github.com/rohanbhattaraidev-beep/se-harness-copilot/actions/workflows/ci.yml)
[![Copilot CLI](https://img.shields.io/badge/Copilot_CLI-se--harness--copilot-8957e5?logo=githubcopilot&logoColor=white)](./docs/setup-guide-copilot.md)
[![agents](https://img.shields.io/badge/SDLC_agents-12-6f42c1)](./plugins/se-harness-copilot/agents)
[![HITL gates](https://img.shields.io/badge/HITL_gates-3_hook--enforced-blue)](./plugins/se-harness-copilot/hooks.json)
[![platforms](https://img.shields.io/badge/macOS_%7C_Linux_%7C_Windows-supported-555)](./docs)
[![privacy](https://img.shields.io/badge/telemetry-none-success)](./PRIVACY.md)

AI coding agents are good at writing code and bad at process discipline. se-harness-copilot
wraps a full software-engineering lifecycle around GitHub Copilot: it learns your project
(scan + interview), builds a memory of your code and domain, staffs it with 12 specialized
agents, and runs each goal through requirement → stories → implementation → tests → PR →
deploy — pausing at **three human-approval gates that are enforced by hooks, not prompts**.
The agent literally cannot open the PR, push, or deploy until *you* flip `status: approved`
(the `preToolUse` hook returns a `permissionDecision` deny).

The same goal loop scales from a single repo up to a whole product: single repo, mono-repo,
modulith, multi-repo, and hybrid topologies all go through `harness-goal` the same way. Only
when a change's impact spans **2 or more** repos/components does the harness create an
inspectable `workspace-plan.md`, hand it to a `workspace-orchestrator` agent, and require a
combined integration check before the usual gates will let anything ship.

## What you get

- **Bootstrap, not boilerplate** — `harness-init` scans existing repos first (stack +
  org-convention detection, evidence-based, you confirm) and interviews you only for what it
  can't detect. Output: `AGENTS.md` inside idempotent generated-block markers (your hand
  edits survive re-runs), a committed `.harness/` profile, and a gitignored `.env.harness`.
- **A goal loop with real gates** — `harness-goal "Add CSV export"` grills you until the
  requirement is unambiguous, writes `.harness/requirements/REQ-001.md`, then drives stories →
  design → parallel implementation in isolated worktrees → unit/integration/e2e tests → PR →
  deploy. Three gates (requirement, PR evidence, deploy) are blocked by the hook until you
  approve.
- **A 12-agent SDLC roster** — architect, story-writer, backend/frontend implementers,
  db-engineer, unit + integration testers, e2e planner/generator/healer, release-manager, and
  a workspace-orchestrator for multi-component requirements.
- **3-tier memory** — committed project profile, append-only daily/topic logs with typed
  causal links, and a provenance-tracked domain wiki (ingest/query/lint skills).
- **Multi-repo aware** — declare products in `workspace.yaml` with a contracts registry;
  `contract-check.sh` blocks pushes that change a provided contract and names the consumer
  repos that would break. See
  [`docs/workspace-orchestration-plan.md`](./docs/workspace-orchestration-plan.md).
- **Drift-aware sync** — `harness-sync` detects drift on four axes (profile, recommendations,
  templates, memory health), shows the diff first, and refreshes only generated blocks.
- **Repo-level export** — `harness-export` vendors agents and hooks into `.github/` for the
  Copilot coding agent on github.com.
- **No telemetry, ever** — see [PRIVACY.md](./PRIVACY.md).

## Install

```bash
copilot plugin marketplace add rohanbhattaraidev-beep/se-harness-copilot
copilot plugin install se-harness-copilot@se-harness-copilot
```

**Plugin installs restricted in your org?** The [setup guide](./docs/setup-guide-copilot.md)
(§1.2–1.3) covers internal GitHub Enterprise import and offline zip → local-path
marketplace, plus a no-plugin prompt-driven fallback.

## Quickstart (5 minutes)

In your project run `copilot harness-init`. Existing repos get scanned first; you're
interviewed only for what can't be detected. Then `copilot harness-bootstrap` for opt-in
companion tooling, and your first goal:

```
copilot harness-goal "Add CSV export to the reports page"
```

It writes `.harness/requirements/REQ-001.md` and the gate hook blocks PR/push/deploy until
**you** flip `status: approved`.

**Multi-repo product** — clone all repos side-by-side and add a `workspace.yaml` (from
[`templates/workspace.yaml`](./templates/workspace.yaml)), or run `harness-init` from an empty
workspace folder with a `repos.txt` listing the repos — it'll offer to clone them (opt-in,
shows the plan, never overwrites). Then run `harness-init` again inside each code repo.

A companion demo repo, [demo-loan-app](https://github.com/rbhattarai/demo-loan-app), is a
two-app loan product with a ready-made `workspace.yaml`; walkthrough in
[`docs/demo/README.md`](./docs/demo/README.md).

### Commands

| Command | What it does |
|---|---|
| `harness-init` | Intake interview (+ scan for existing repos) → generates all per-project artifacts |
| `harness-scan` | Brownfield detection: evidence collector → confirm → merge into profile |
| `harness-bootstrap` | Recommends companion plugins/CLIs/MCP servers from your profile; opt-in install + lockfile |
| `harness-goal` | The goal loop: supervisor over the agent roster, 3 hook-enforced approval gates |
| `harness-sync` | Four-axis drift detection → diff-first report → confirmed refresh of generated blocks |
| `harness-export` | Vendor agents + hooks into `.github/` for the coding agent |

## Documentation

- **[GitHub Copilot setup guide](./docs/setup-guide-copilot.md)** — CLI plugin, coding agent,
  VS Code, enterprise rollout, worked examples, extending and publishing
- **[Surface matrix](./docs/interop-matrix.md)** — component × Copilot surface support, plus
  verified schema notes in [`docs/copilot/`](./docs/copilot)
- **[Demo walkthroughs](./docs/demo/README.md)**
- **[Workspace-orchestration plan](./docs/workspace-orchestration-plan.md)**
- [Historical design notes](./docs/history) from when the project also targeted Claude Code

## Repo layout

```
.github/plugin/marketplace.json      # this repo IS a Copilot plugin marketplace
plugins/se-harness-copilot/          # the plugin (source of truth)
  plugin.json  hooks.json
  agents/                            # 12-agent SDLC roster (*.agent.md)
  skills/                            # harness skills + each harness-* command as a skill
  commands/                          # the six harness-* commands
  scripts/                           # gate-check, org-validate, memory-log, contract-check,
                                     # copilot-hook-adapter, workspace-*, render-block, ...
registry/recommendations.json        # profile → plugin mappings (recommender data)
templates/                           # profile/env/requirement/AGENTS/mcp/workspace/hooks + memory seeds
docs/                                # setup guide, surface matrix, platform notes, demo guide
tests/run-tests.sh                   # test suite run in CI
```

## Contributing

Edit `plugins/se-harness-copilot/` directly and run `bash tests/run-tests.sh`. See
[CONTRIBUTING.md](./CONTRIBUTING.md). Verify manifests against the
[Copilot plugin docs](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference)
before releasing — the schemas evolve quickly.
