---
name: harness-update
description: Update the se-harness plugin to the newest version (marketplace first, GitHub as fallback), then migrate this project's .harness/ data to match — without losing anything the project changed.
---

# /harness-update — plugin update + project migration

Two different things get out of date, and this command handles both in order:

1. **The plugin** (commands, skills, hooks, scripts) — lives in Copilot CLI's plugin store, is
   replaced wholesale on update, and only takes effect after a **restart**.
2. **This project's harness data** (`.harness/`, the generated block in `AGENTS.md`) — lives in the repo, is *yours*, and must be migrated, never overwritten.

Because of the restart, the command is **re-entrant**: run it, update, restart, run it again.
`--check` in `$ARGUMENTS`: run Steps 0, 1 and the read-only `--dry-run` of Step 3, report what
is out of date and what would happen, and change nothing (Step 1's marketplace refresh only
updates the local catalog clone).

Never use `-y`/`--force`/`--force-blocks` or accept a marketplace-declared command on the
user's behalf — every one of those is an explicit confirmation from them.

## Step 0 — What is installed, what is in the project
- **Running plugin version**: `version` in the `plugin.json` of the plugin that ships this
  command (the one currently loaded).
- **Project stamp** (if `.harness/agentstack.lock` exists): `se_harness` (version that last
  wrote this project) and `schema_version` (absent = 1). At a workspace root (`workspace.yaml` /
  `repos.txt`, no lockfile of its own) the stamp lives in each bootstrapped unit — see Step 5.
- **Install source**: run `copilot plugin list` and find `se-harness-copilot` — note the
  marketplace it came from (or that it was installed from a local path, in which case it is
  updated with `git pull` in that clone, not through a marketplace). Check
  `copilot plugin --help` once for the exact subcommand names in this CLI version rather than
  guessing.

## Step 1 — Find the newest version (marketplace first)
1. Refresh the marketplace catalog (`copilot plugin marketplace update <marketplace>` if this CLI
   has it; otherwise the update in Step 2 refreshes it).
2. Read `version` from the marketplace clone's `plugins/se-harness-copilot/plugin.json` (find
   the clone via `copilot plugin marketplace list` / `copilot plugin list`).
3. **If the marketplace step fails** (offline, auth, marketplace not added, clone broken): fall
   back to GitHub. Fetch with WebFetch
   `https://raw.githubusercontent.com/rbhattarai/se-harness-copilot/main/plugins/se-harness-copilot/plugin.json`
   (the repo is `repository` in this plugin's `plugin.json`; use it if it differs) and read
   `version`. If that fails too, say both sources were unreachable, name each error, and stop —
   do not guess.
4. Compare with the running version (semver). Report one line:
   `installed X · newest Y (via marketplace|github) · project stamp S / schema N`.
   For a major bump, point at the release notes
   (`https://github.com/rbhattarai/se-harness-copilot/releases`) before going on.

(Plugin scripts make no network calls — `PRIVACY.md` — so every lookup above goes through the
`copilot` CLI or WebFetch, here in the command, never inside `scripts/`.)

## Step 2 — Update the plugin (only if newest > running)
With `--check`: skip this step and Step 4; report only.

1. Confirm with the user (AskUserQuestion): update `se-harness-copilot` X → Y (source found in Step 0)?
2. If the newest version was found **only via GitHub** (the marketplace step failed), the
   marketplace clone is stale and the plugin update would see no change. Tell the user to
   repair it first — `copilot plugin marketplace add rbhattarai/se-harness-copilot` (re-adds/refreshes),
   or the marketplace update once connectivity is back — and re-run this command.
   Do not copy files out of a GitHub clone into the plugin cache by hand.
3. Otherwise run `copilot plugin update se-harness-copilot` (or reinstall with
   `copilot plugin install se-harness-copilot@<marketplace>` if this CLI has no update
   subcommand). If it asks for confirmation of anything, show it to the user verbatim and let
   them decide. A local-path install: tell them to `git pull` in that clone instead.
4. Tell the user plainly: **restart Copilot CLI, then run `/harness-update` again** — the new
   commands and scripts load only on restart, and the migration in Step 4 must be run by the
   *new* plugin's `migrate.sh`, which is why this command stops here. Stop.

## Step 3 — Running plugin is current: does this project need migrating?
(No lockfile → the project isn't bootstrapped; nothing to migrate. Say so and stop; suggest
`/harness-init` then `/harness-bootstrap`.)

Run `bash tools/harness/migrate.sh --dry-run`.
- `up to date` and `se_harness` equals the running version → "nothing to do", stop.
- `up to date` but `se_harness` is older → no data migration is needed; skip to Step 5
  (a sync refreshes the generated blocks and stamps the new version).
- Pending migrations → list them with their descriptions, and say what protects the user:
  one backup under `.harness/backup/`, whole-run rollback on any failure, hand-edited generated
  blocks never overwritten silently, user-written files never touched.
- `project schema is newer than this plugin supports` → the plugin is *older* than the project
  (someone upgraded elsewhere). Go back to Step 2.

## Step 4 — Migrate
1. If the working tree has uncommitted harness changes, `migrate.sh` refuses (exit 2). Suggest
   committing or stashing them first. Offer `--allow-dirty` only if the user insists.
2. Confirm, then run `bash tools/harness/migrate.sh`.
3. Exit 0 → report the schema change and the backup path. Exit 3 → a generated block was
   hand-edited: for each `*.seaa.proposed` file show the user a diff against their current
   block and ask keep-mine / take-new. Keep-mine: leave it (the project stays on its old
   block; tell them the migration did not run). Take-new: re-run with `--force-blocks`
   (their edit is saved to `<file>.seaa.bak`). Exit 1 → rolled back; show the error and the
   backup path; do not retry blindly.

## Step 5 — Refresh generated content
Run `/harness-sync` (its Step 0b re-checks the stamps; it sets `se_harness` to the running
version after a clean sync). At a **workspace root**, ask once which bootstrapped units to
update (all / named / suggest), then run Steps 3–5 for each unit in turn and finish with one
table: unit | schema before → after | migrated | block conflicts | skipped.

## Step 6 — Report
Plugin: X → Y (or already current) · migrated: schema A → B (or none) · backup path ·
`.seaa.proposed`/`.seaa.bak` files left for the user to review · next: review the diff and
commit `.harness/` and `AGENTS.md`; add `.harness/backup/` to `.gitignore` (or delete
the backup once satisfied).
