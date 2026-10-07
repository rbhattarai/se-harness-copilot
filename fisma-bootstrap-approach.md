# FISMA — se-harness bootstrap approach (personal working notes)

> **Not committed.** This file is untracked in this repo on purpose — it's your own
> notes for rolling se-harness out on the FISMA project. Email it to yourself and
> delete it from the working copy whenever you're done; nothing here has been (or
> will be) `git add`ed.

Written against `se-harness` as of commit `dc5bf87` (main), which just added Graphify as
a third structural-memory candidate. Framework docs this is distilled from:
`docs/setup-guide-copilot.md` (your org is GitHub Copilot, not Claude Code — that guide is
the canonical one for you), `templates/workspace.yaml`, `templates/profile.yaml`,
`registry/recommendations.json`, and `plugins/se-harness/commands/harness-goal.md`.

---

## 1. What se-harness actually gives you here

- **Per-repo memory + conventions**: `/harness-init` (or `/harness-scan` on an existing repo)
  reads each repo, detects stack (dotnet/C#, Angular/TypeScript, MSSQL), interviews you for
  what it can't detect (org conventions, internal libraries), and writes `AGENTS.md` +
  `.harness/profile.yaml` + `.harness/memory/` into that repo. Copilot (CLI, VS Code Chat,
  and the cloud coding agent) reads `AGENTS.md` natively.
- **A workspace manifest** (`workspace.yaml`) that ties your repos together: shared org
  context, and a **contract registry** — when `fisma-backend-core` changes an API that
  `fisma-frontend` or `fisma-backend-integration` consumes, `contract-check.sh`
  deterministically flags it and blocks the push until you've dealt with it.
- **The goal loop** (`/harness-goal "<your feature>"`): grills you for requirement/acceptance
  criteria if you didn't give them, writes an approval-gated `REQ-NNN.md`, drives
  story → design → implementation → tests → PR → deploy, with **3 human approval gates**
  enforced by hooks (not just prompts) — the agent literally cannot push/PR/deploy an
  unapproved requirement.
- **Three memory tiers**, all plain files under `.harness/`, committed with your code:
  1. **Structural** — a rebuildable code-graph (impacted files/callers/blast radius). Still
     an open "bake-off" in this framework between CodeGraph, codebase-memory-mcp, and (as of
     today) **Graphify** — see §5.
  2. **Session** — append-only daily logs + `MEMORY.md`, with typed causal links
     (`[[REQ-042]] solves [[dealer-mapping-duplicate-key-bug]]`).
  3. **Domain wiki** — synthesized, provenance-tracked pages under `.harness/memory/wiki/`,
     built by ingesting Jira/Confluence/etc. (`wiki-ingest` skill).

**What it is not (be honest with your team about this)**: there is currently **no single
command that spans multiple repos and writes code in all of them for one feature**. The
"workspace-level goal loop over a federated service graph" is explicitly on this framework's
v2 roadmap, not implemented yet. `/harness-goal` runs **per repo**. `workspace.yaml`'s
contract registry gives you deterministic *impact detection* across repos (it'll tell you
"changing this contract breaks `fisma-frontend`"), not automatic cross-repo implementation.
§7 below shows exactly how you thread one feature across `fisma-frontend` /
`fisma-backend-integration` / `fisma-backend-core` today, by hand, with the harness doing the
per-repo heavy lifting and the contract registry catching what you'd otherwise miss.

---

## 2. Your repo topology, mapped to the framework's model

This is a **multi-repo product** in se-harness terms (`workspace.topology: multi-repo`,
`layout: layered`). Map your repos to roles:

| Your repo | Stack (for `profile.yaml`/`workspace.yaml`) | Role |
|---|---|---|
| `fisma-frontend` | `angular`, `typescript` | UI |
| `fisma-common-ui` | `typescript` (internal component/shared UI library) | shared UI lib, consumed by frontend |
| `fisma-backend-core` | `dotnet`, `csharp`, `mssql` | domain models, controllers, business logic |
| `fisma-backend-integration` | `dotnet`, `csharp` | vendor integrations (InvestorTools Perform, ICE, etc.) |
| `fisma-config` | (none / per-env `.prop`-style files) | environment config |
| `fisma-database` | `mssql` | schema/migrations |
| *(any others you have — `fisma-...`)* | fill in | |

This is close enough to the framework's own worked example (`acme-loan-platform`:
`frontend` / `backend-core` / `backend-integration` / `common` / `ui` / `config` /
`database-config`, Angular + .NET Core + MSSQL) that you can follow
`docs/setup-guide-copilot.md` Parts 2–8 almost line-for-line, substituting your repo names.
That's what the rest of this doc does.

---

## 3. Install the framework (once, for you — or once for the org)

Your org uses **GitHub Copilot**, so this is the Copilot CLI plugin path
(`docs/setup-guide-copilot.md` Part 1), not Claude Code.

**If your machine can reach public GitHub and plugin installs aren't restricted:**
```bash
copilot plugin marketplace add rbhattarai/se-harness
copilot plugin install se-harness-copilot@se-harness
```

**More likely, given a financial-firm environment — get it imported internally first**
(don't hand-copy an unreviewed zip into firm infra):
1. Ask platform/security to import `rbhattarai/se-harness` into GitHub Enterprise as an
   internal repo (e.g. `yourorg/se-harness`) via "Import repository" — it contains no company
   data, it's small, they can read all of it in a few minutes.
2. Then:
   ```bash
   copilot plugin marketplace add yourorg/se-harness
   copilot plugin install se-harness-copilot@se-harness
   ```
3. Everything below references this internal copy from now on.

If plugin installs are blocked entirely, Part 1.3 of the setup guide covers the offline-zip /
local-path fallback — the repo-level artifacts (`AGENTS.md`, `.github/agents/`,
`.github/prompts/`, vendored `tools/harness/` scripts) work even without the CLI plugin
installed, driven as plain prompts.

Verify: `copilot plugin list` shows `se-harness-copilot`.

---

## 4. Lay out the FISMA workspace (side-by-side clones)

Side-by-side, one folder, the harness beside your repos — the workspace manifest and
contract-check assume sibling checkouts:

```bash
mkdir fisma-workspace && cd fisma-workspace
git clone <internal-git-url>/fisma-frontend.git
git clone <internal-git-url>/fisma-common-ui.git
git clone <internal-git-url>/fisma-backend-core.git
git clone <internal-git-url>/fisma-backend-integration.git
git clone <internal-git-url>/fisma-config.git
git clone <internal-git-url>/fisma-database.git
# ...any other fisma-* repos
git clone <internal-git-url>/se-harness.git      # the internal framework copy
```

Create `fisma-workspace/workspace.yaml` from `se-harness/templates/workspace.yaml`:

```yaml
workspace:
  name: fisma
  topology: multi-repo
  layout: layered

  shared:
    org:
      internal_libraries:
        - { name: "fisma-common-ui", registry: "internal-npm", purpose: "shared Angular UI components" }
        - { name: "Fisma.Common", registry: "internal-nuget", purpose: ".NET shared utilities (if you have one)" }
      conventions_url: "<Confluence page with FISMA coding guidelines, if any>"
    mcp: [github, atlassian]
    jira_project: "FISMA"          # your real Jira project key

  units:
    - { name: fisma-frontend,             repo: <url>/fisma-frontend.git,             stack: [angular, typescript] }
    - { name: fisma-common-ui,            repo: <url>/fisma-common-ui.git,            stack: [typescript] }
    - { name: fisma-backend-core,         repo: <url>/fisma-backend-core.git,         stack: [dotnet, csharp, mssql] }
    - { name: fisma-backend-integration,  repo: <url>/fisma-backend-integration.git,  stack: [dotnet, csharp] }
    - { name: fisma-config,               repo: <url>/fisma-config.git,               stack: [] }
    - { name: fisma-database,             repo: <url>/fisma-database.git,             stack: [mssql] }

  run:
    compose: ""

contracts:                          # exact shape matters — contract-check.sh reads it literally
  - name: core-api
    file: docs/api/core-openapi.yaml           # inside fisma-backend-core
    provider: fisma-backend-core
    consumers: [fisma-frontend]
  - name: perform-ice-feed-schema
    file: schemas/dealer-feed.json             # inside fisma-backend-integration
    provider: fisma-backend-integration
    consumers: [fisma-backend-core]
```

Fill `contracts:` with whatever's actually written down (OpenAPI spec for
`fisma-backend-core`'s API, the schema/contract for what
`fisma-backend-integration` hands back from Investortools Perform/ICE). If nothing's
written down yet — that's itself worth flagging; start with the one or two interfaces that
break most often between teams.

Commit `workspace.yaml` to a small internal meta-repo (e.g. `fisma-harness-meta`) once you're
happy with it, so the rest of the team gets it by cloning. Until then it can just live
uncommitted in `fisma-workspace/`.

---

## 5. Pick a structural-memory engine (and be deliberate about it)

This framework hasn't picked a default yet (its own "A7 bake-off," now three-way as of
today's `Graphify` addition — see `brainstorm.md` B7/B12/B13 if you want the reasoning).
For FISMA, given your stack:

| Candidate | Fit for FISMA | Notes |
|---|---|---|
| **Graphify** (`Graphify-Labs/graphify`) | Probably the easiest first pick | CLI + `/graphify` skill (not a bare MCP server), works across ~40 languages incl. C#/.NET and TypeScript, local tree-sitter AST (nothing leaves the machine for code). `uv tool install graphifyy` then `graphify install --project` inside each repo. Optional `graphify claude install --strict`-style hook exists for Claude Code only — on Copilot you get the always-on guidance via `AGENTS.md`/instruction files instead (see the framework's per-platform table). Also the only one of the three with **built-in PDF/Office/video ingestion** (`graphifyy[pdf]`, `[office]`, `[video]` extras) — useful for §6's NAS gap. |
| `codebase-memory-mcp` (`DeusData/codebase-memory-mcp`) | Strong if you want a **team-shared committed graph artifact** | 158-language tree-sitter + "hybrid LSP," MCP server, ADR tracking, HTTP/gRPC/GraphQL route linking (useful for tracing `fisma-frontend` → `fisma-backend-core` → `fisma-backend-integration` calls). Configured via `.mcp.json`. |
| `CodeGraph` | Two unrelated projects share this name (`codegraph-ai/CodeGraph` vs `colbymchenry/codegraph`) | Confirm which one before installing anything; disambiguate by repo URL, not the name "CodeGraph." |

**Recommendation for a first pass**: install Graphify in `fisma-backend-core` first (your
densest C#/MSSQL logic), run `/graphify .`, look at `graph.html` and `GRAPH_REPORT.md`, and
decide from there whether you want the team-shared-artifact properties of
`codebase-memory-mcp` instead/as well. Don't over-invest in the bake-off — this tier is
rebuildable by design, so switching later costs nothing you've committed.

---

## 6. Wire up your actual memory sources

Map what you listed to what the framework already knows how to ingest, and what's still a
gap:

| Source | Status in se-harness today | What to do |
|---|---|---|
| **Jira** (Epics/Stories/Bugs) | ✅ First-class, via Atlassian MCP | Set `ATLASSIAN_BASE_URL` / `ATLASSIAN_EMAIL` / `ATLASSIAN_API_TOKEN` in each repo's `.env.harness` (gitignored, never commit). `story-writer` agent creates/links stories at goal-loop step 4; `wiki-ingest` can pull existing Epics/PRDs into the domain wiki. |
| **Zephyr/XRay test cases** | ✅ First-class, via Atlassian MCP | Same story-writer agent — one test case per acceptance criterion, keys recorded in the `REQ-NNN.md` frontmatter. |
| **Confluence** | ✅ First-class, via Atlassian MCP | Set `sources.confluence_spaces` in `.harness/profile.yaml`; `wiki-ingest` synthesizes pages from it (never copies raw content — provenance-linked distillation). |
| **GitHub (multiple repos, PRs)** | ✅ First-class, via GitHub MCP | `GITHUB_PERSONAL_ACCESS_TOKEN` in `.env.harness`. Commits/PRs are auto-logged to the daily memory by a post-commit hook — you don't have to do this by hand. |
| **SharePoint** | ⚠️ Anticipated but **not bundled** | `profile.yaml` already has a `sources.sharepoint_sites` field and `.env.harness` already has `SHAREPOINT_CLIENT_ID`/`SHAREPOINT_CLIENT_SECRET` placeholders — but se-harness doesn't ship a SharePoint MCP server. You (or your firm's platform team) need to stand up/point at one (e.g. a Graph-API-based SharePoint MCP) and register it in `.mcp.json` / `.vscode/mcp.json`. Until then, `wiki-ingest` treats a SharePoint doc the same as any "local document" you paste/attach. |
| **NAS documents** | ❌ Explicitly deferred in v1 (`profile.yaml`'s `sources.deferred: [nas_documents]`) | The `wiki-ingest` skill will politely decline these today. Practical workaround: point **Graphify** at the NAS share directly — `uv tool install "graphifyy[pdf]" "graphifyy[office]"` then `/graphify \\nas\path\to\docs` (or the mapped drive letter) builds a local graph over those files with zero se-harness changes needed. Feed its `GRAPH_REPORT.md` highlights into `wiki-ingest` as a manually-attached source afterward if you want it in the domain wiki proper. |
| **Recorded videos (NAS)** | ❌ Explicitly deferred in v1 (needs transcription/OCR infra — same field) | Same workaround, one step further: `uv tool install "graphifyy[video]"` (pulls in faster-whisper) then `/graphify <path-to-recordings>` transcribes and indexes them. This is the one place Graphify genuinely fills a hole se-harness admits it doesn't cover yet. |

Practical order: get Jira + GitHub wired first (cheap, first-class, immediate payoff for the
goal loop), Confluence next, then decide whether SharePoint/NAS/video is worth the extra
setup for your team versus just describing that domain knowledge to the agent directly when
it grills you.

---

## 7. Bootstrap each FISMA repo

Do **one repo first** — recommend `fisma-backend-core` (it's the hub) — verify it fully
(§8), then repeat for the rest. This follows `docs/setup-guide-copilot.md` Part 4.

For each of `fisma-frontend`, `fisma-common-ui`, `fisma-backend-core`,
`fisma-backend-integration` (the real code repos):

```bash
cd fisma-backend-core        # one repo at a time
```

In VS Code Copilot Chat (agent mode) or Copilot CLI, run the intake. As a prompt (adjust the
relative path to wherever you cloned `se-harness`):

> Read `../se-harness/plugins/se-harness/commands/harness-init.md` and execute its steps
> against this repository as an **existing project**. Also read
> `../se-harness/plugins/se-harness/commands/harness-scan.md` and
> `../se-harness/plugins/se-harness/skills/stack-detector/SKILL.md`, run
> `bash ../se-harness/plugins/se-harness/scripts/scan-evidence.sh` in the terminal, and use
> its output as the detection evidence. Interview me for anything you can't detect —
> especially FISMA-specific organization context (internal NuGet/npm libraries like
> `fisma-common-ui`, banned/preferred libraries, MSSQL conventions, coding conventions).
> Write the artifacts exactly as the command specifies. For AGENTS.md and CLAUDE.md, render
> the inner block to a temp file and splice it with
> `bash ../se-harness/plugins/se-harness/scripts/render-block.sh <target> <temp-file>` —
> never edit those files directly.

Or, if you installed the CLI plugin (§3), just run `copilot harness-init` in the repo — same
result.

**Verify what got written** in `fisma-backend-core`:
- `.harness/profile.yaml` — stack should read `dotnet`, `csharp`, `mssql`; `org:` section
  filled with your internal libraries/conventions
- `.env.harness` — created from the example; fill secrets locally, **never commit**
- `.harness/memory/` — `MEMORY.md`, `SCRATCHPAD.md`, `daily/`, `wiki/`
- `.harness/org-rules.txt` — one line per "use X, never Y" answer you gave
- `AGENTS.md` (+ `CLAUDE.md`) — with `SEAA:GENERATED` markers

Then repeat for `fisma-backend-integration` (mention InvestorTools Perform/ICE as vendor
integrations when it asks about org context — that's exactly the kind of thing the intake
interview is for), `fisma-frontend`, and `fisma-common-ui`.

**Lighter treatment** for `fisma-config` and `fisma-database` (per Part 4.6 of the setup
guide — no full `.harness/` needed):
- `fisma-config`: a short hand-written `AGENTS.md` explaining your `.prop`/env-file naming
  scheme and which env is which.
- `fisma-database`: a hand-written `AGENTS.md` describing your MSSQL object/migration layout
  and change process. Optionally add a minimal `.harness/profile.yaml` with `stack: [mssql]`
  if you want it inside the workspace tooling proper.

**Also do, per real code repo** (Part 4.2–4.7 of the setup guide):
- The Copilot CLI plugin already gives every CLI session the agent roster + skills + commands
  + hooks (from §3's install).
- For the coding agent on github.com and VS Code Chat, export repo-level agent profiles and
  prompt files:
  ```bash
  bash ../se-harness/plugins/se-harness/scripts/export-agents.sh copilot .
  mkdir -p .github/prompts
  cp ../se-harness/plugins/se-harness-copilot/commands/harness-goal.md .github/prompts/harness-goal.prompt.md
  ```
- A thin `.github/copilot-instructions.md` pointing at `AGENTS.md`.
- MCP config (`.vscode/mcp.json`) for Atlassian + GitHub, per §6.
- The enforcement hooks (repo-level, for the coding agent + VS Code):
  ```bash
  mkdir -p tools/harness
  cp ../se-harness/plugins/se-harness/scripts/{copilot-hook-adapter.sh,gate-check.sh,org-validate.sh,memory-log-commit.sh,contract-check.sh} tools/harness/
  mkdir -p .github/hooks
  cp ../se-harness/templates/copilot-hooks.json .github/hooks/se-harness.json
  ```
  **Verify this before trusting it** — ask Copilot to open a PR while the REQ is still
  `draft`; it must be denied.

Commit everything except `.env.harness` through your normal PR process, per repo.

---

## 8. Verify the bootstrap (per repo, ~10 min)

1. VS Code → Copilot Chat: *"What internal libraries must this project prefer, and what's
   banned?"* — answer must come from `AGENTS.md`'s org section, not a generic answer.
2. *"What's the workflow for implementing a new requirement here?"* — expect the goal-loop
   summary (REQ → approval → story → implement → tests → PR gates).
3. `bash ../se-harness/plugins/se-harness/scripts/scan-evidence.sh | head -40` — confirms it
   sees your `.csproj`/`package.json`/internal registry scopes.
4. Assign a trivial GitHub issue to the Copilot coding agent in that repo; confirm the PR
   description reflects `AGENTS.md` conventions.

---

## 9. Worked example — "Dealer Mapping" end to end

This is the concrete answer to your question. Read §1's honesty note first: **this runs
per-repo today**, threaded together by you + the shared REQ/story ID + the contract registry
— not one command that silently writes code in three repos.

### 9.1 Where you start it
Start in whichever repo owns the primary logic — for "Dealer Mapping," that's most likely
`fisma-backend-core` (it owns the domain model). Open it in VS Code Copilot Chat (agent mode)
or `copilot` CLI, and run:

```
/harness-goal "Add Dealer Mapping functionality"
```

(or `copilot harness-goal "Add Dealer Mapping functionality"` in the CLI.)

### 9.2 What happens (per `plugins/se-harness/commands/harness-goal.md`)
1. **Grill** — since you gave it almost nothing, it interrogates until the requirement is
   falsifiable: what "dealer mapping" means concretely (mapping dealer codes/IDs across
   Investortools Perform and ICE to your internal dealer records?), explicit scope
   exclusions, testable acceptance criteria, failure behavior (what happens on an unmapped
   dealer code?), and checks for conflicts with prior decisions via `wiki-query` + org
   conventions. It batches its questions rather than trickling them one at a time.
2. **Deep-dive memory** — queries the structural-memory engine you picked (§5) for
   impacted files/callers in `fisma-backend-core`, checks `workspace.yaml`'s
   `contracts:` for anything Dealer Mapping would touch (e.g. if it changes the
   `perform-ice-feed-schema` contract, it already knows `fisma-backend-core` is a
   consumer), queries the domain wiki for related PRDs/decisions, and checks recent daily
   logs for prior attempts.
3. **Gate 1** — writes `.harness/requirements/REQ-NNN.md` with everything above, **stops**,
   and shows it to you. Nothing proceeds until you flip `status: approved` yourself.
4. **Story + test cases** — `story-writer` creates the Jira story + Zephyr/XRay test cases
   (one per acceptance criterion) via Atlassian MCP; story/test-case keys land in the REQ.
   **This is your thread across repos**: note the story key (e.g. `FISMA-1234`).
5. **Design + implement** — `architect` writes `design.md` (component/data model changes,
   API changes, one ADR per new decision), you resolve its open questions, then it's broken
   into tasks and implemented in isolated git worktrees *within this repo* — model/controller
   code for dealer mapping, in `fisma-backend-core`, tagged with the REQ id.
6. **Tests, then gate 2 (PR)**, then **local verify**, then **gate 3 (deploy)** — same as any
   other goal, per `harness-goal.md` steps 6–9.

### 9.3 The frontend and integration pieces
Because implementation in step 5 is scoped to the repo you started in, do the UI
(`fisma-frontend`) and vendor integration (`fisma-backend-integration`) pieces as their **own**
`/harness-goal` runs, in their own repos, **once the core design is settled** (so the
frontend/integration requirements can reference the same design decisions instead of
guessing):

```bash
# in fisma-backend-integration
/harness-goal "Integrate dealer mapping data from Investortools Perform and ICE for REQ-NNN"

# in fisma-frontend
/harness-goal "Build the Dealer Mapping UI for REQ-NNN"
```

Reference the original REQ/story key (`FISMA-1234`) when it grills you in each repo — that's
what threads the three REQs together as one feature in Jira and in your daily memory logs.
Before pushing from `fisma-backend-integration` or `fisma-backend-core`, run
`bash ../se-harness/plugins/se-harness/scripts/contract-check.sh --` (CI re-checks it anyway)
— if the vendor feed schema or core API changed, it names exactly which sibling repo's
consumer code might now be broken, so you don't find out from a runtime error later.

### 9.4 What to expect vs. what not to expect
- **Expect**: per-repo requirement grilling, approval gates, story/test-case creation, design
  docs, implementation in isolated worktrees, contract-impact warnings across repos, PR/deploy
  gates — all real, all hook-enforced.
- **Don't expect** (yet): typing one goal once and having the harness silently open three
  coordinated PRs across `fisma-frontend`/`fisma-backend-integration`/`fisma-backend-core`
  without you re-invoking it in each repo. That federated, workspace-level goal loop is
  explicitly future work in this framework (see README "Status" / `brainstorm.md` A7).

---

## 10. Enforcement you should also keep at the GitHub/org layer

Hooks constrain the *agent*, not humans, and don't run in VS Code Chat. Keep the GitHub-native
layer too (`docs/setup-guide-copilot.md` Part 6): branch protection requiring PR review
(CODEOWNERS on `fisma-database`/`fisma-config` especially), required green status checks, a
PR template that requires linking an `approved` `REQ-NNN.md`, and CI jobs that re-run
`org-validate.sh` / `contract-check.sh` against the diff so hand-written PRs get the same
checks agent PRs do.

---

## 11. Rollout order (suggested)

1. Get the plugin installed internally (§3) — one-time, coordinate with platform/security.
2. Bootstrap `fisma-backend-core` alone; verify (§8); live with it for a few days.
3. Wire Jira + GitHub MCP (§6) — cheapest payoff.
4. Bootstrap `fisma-backend-integration`, `fisma-frontend`, `fisma-common-ui`; light-touch
   `fisma-config`/`fisma-database`.
5. Write `workspace.yaml` with real contracts (§4) once you know which 1–2 interfaces
   actually break most often between teams — don't try to model everything on day one.
6. Pick a structural-memory engine (§5) — Graphify is the lowest-friction first try.
7. Confluence, then SharePoint/NAS/video only if the team actually needs them ingested rather
   than just described to the agent by hand (§6).
8. Run your first real goal end-to-end on a small, low-risk requirement before trying
   something as cross-cutting as Dealer Mapping — you want to have seen the three gates fire
   at least once on something forgettable.
