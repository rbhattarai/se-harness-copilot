# Contributing

Thanks for your interest in improving the SE Harness! Contributions of all kinds are
welcome — bug reports, new agents/skills, docs fixes, and support for additional
stacks or ecosystems. This project is MIT-licensed; by contributing you agree your
contributions are licensed under the same terms.

## Repo layout — read this first

| Path | Role |
|---|---|
| `plugins/se-harness-copilot/` | **Source of truth.** The Copilot plugin: agents, skills, commands, hooks, scripts. |
| `.github/plugin/marketplace.json` | Marketplace manifest (Copilot's canonical location). Edit directly. |
| `templates/` | Files the harness copies into user projects (`AGENTS.md.tmpl`, `workspace.yaml`, hooks, memory seeds). |
| `registry/recommendations.json` | Stack-detection to companion-tooling recommendations used by `harness-bootstrap`. |
| `docs/` | Setup guide, surface matrix, and platform notes. |

## Development workflow

1. **Fork and branch.** Create a topic branch off `main`.
2. **Make your change** in `plugins/se-harness-copilot/` (or docs/templates/registry).
   Each `harness-*` command exists twice: `commands/<name>.md` and
   `skills/<name>/SKILL.md` (Copilot registers commands as skills). Keep the bodies identical.
3. **Test:** `bash tests/run-tests.sh`.
4. **Try it locally** without publishing:

   ```bash
   copilot plugin install ./plugins/se-harness-copilot
   ```

   Then exercise what you changed in a scratch project. Components are cached, so uninstall
   and reinstall to pick up edits.
5. **Open a pull request** against `main`. Describe what you changed and how you tested it.
   Keep PRs focused: one logical change per PR.

## Versioning and releases

**Do not bump versions in a contribution PR** — maintainers handle releases.
Versions are pinned, so users only receive updates when the version string changes.
A release bumps two places in lockstep (semver):

- `plugins/se-harness-copilot/plugin.json` -> `version`
- `.github/plugin/marketplace.json` -> `metadata.version`

followed by a `vX.Y.Z` tag and a GitHub release.

## Conventions

- **Agents** (`agents/<name>.agent.md`): YAML frontmatter with `name` and `description` on
  single lines. Tool scoping is carried as body guidance.
- **Skills** (`skills/<name>/SKILL.md`): `name` + `description` frontmatter.
- **Commands** (`commands/*.md`): reference scripts as `tools/harness/<script>.sh` (vendored
  into the managed repo) and templates/registry via `../se-harness-copilot/`. Don't hardcode
  absolute paths.
- **Scripts** (`plugins/se-harness-copilot/scripts/*.sh`): POSIX-leaning bash, `set -eu`,
  no network calls. The plugin must keep working fully offline — see
  [PRIVACY.md](./PRIVACY.md); a change that adds telemetry or remote calls will not
  be accepted without a privacy-policy update and very good reason.
- Line endings: files are committed with LF; a CRLF-converting editor on Windows is
  fine (git handles it), but don't commit mass line-ending churn.

## Reporting bugs and proposing features

Open a [GitHub issue](https://github.com/rohanbhattaraidev-beep/se-harness-copilot/issues)
with reproduction steps (for bugs: OS, Copilot CLI version, and the
command or hook involved). For larger features — new agents,
changes to the goal-loop gates — please open an issue to discuss before investing in
a PR.

## Questions

Open an issue, or reach the maintainer at rohan.bhattarai.dev@gmail.com.
