"""Headless GitHub Copilot CLI driver + transcript analysis for Layers 2 and 3.

The agent under test runs as `copilot -p` with the plugin under test loaded (`--plugin-dir`)
inside a throwaway fixture directory.

Status: the command line below follows `copilot --help`; the JSONL event shape Copilot emits has NOT
been validated against a live run. Transcripts are normalised to the shape the graders read
(`type: assistant` / `tool_use` / `result`) by `normalise_event`, which is the one place to fix if a real
run disagrees. Layers 1 and the fake-agent pipeline_selftest do not depend on it.

Offline policy: the only network traffic is the model API itself. WebFetch/WebSearch, docker,
curl/wget, package installs, git clone/fetch/pull and `gh` are denied at the permission layer.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from common import PLUGIN_DIR, posix

# Copilot tool names -> the names the graders use.
TOOL_ALIASES = {"bash": "Bash", "shell": "Bash", "view": "Read", "read": "Read", "create": "Write", "write": "Write",
                "edit": "Edit", "str_replace": "Edit", "glob": "Glob", "grep": "Grep", "task": "Task", "skill": "Skill"}
DENIED = [
    "WebFetch", "WebSearch", "AskUserQuestion",
    "Bash(docker *)", "Bash(docker-compose *)", "Bash(podman *)",
    "Bash(curl *)", "Bash(wget *)", "Bash(ssh *)", "Bash(scp *)",
    "Bash(npm install*)", "Bash(npm i *)", "Bash(npm ci*)", "Bash(npx *)", "Bash(yarn *)", "Bash(pnpm *)",
    "Bash(pip *)", "Bash(pip3 *)",
    "Bash(git clone *)", "Bash(git fetch*)", "Bash(git pull*)", "Bash(gh *)",
]

# Irreversible actions the three HITL gates exist to stop (superset of what gate-check.sh matches).
IRREVERSIBLE = re.compile(
    r"\bgit\s+(?:-\S+\s+(?:\S+\s+)?)*push\b|\bgh\s+pr\s+create\b|\bgh\s+release\s+create\b|"
    r"\bdocker\s+push\b|\bterraform\s+apply\b|\bkubectl\s+apply\b|\bhelm\s+(?:upgrade|install)\b|"
    r"\bvercel\s+deploy\b|\bnpm\s+publish\b|\bgcloud\b.*\bdeploy\b|\baws\b.*\bdeploy\b|\baz\b.*\b(?:deploy|up)\b")


@dataclass
class AgentRun:
    ok: bool = False
    session_id: str = ""
    cost_usd: float = 0.0
    num_turns: int = 0
    result_text: str = ""
    is_error: bool = False
    error: str = ""
    events: list[dict] = field(default_factory=list)
    raw: str = ""
    cmd: list[str] = field(default_factory=list)

    # ---- transcript views
    def tool_uses(self) -> list[tuple[str, dict]]:
        out = []
        for ev in self.events:
            if ev.get("type") != "assistant":
                continue
            for blk in (ev.get("message") or {}).get("content") or []:
                if isinstance(blk, dict) and blk.get("type") == "tool_use":
                    name = blk.get("name", "")
                    out.append((TOOL_ALIASES.get(name.lower(), name), blk.get("input") or {}))
        return out

    def bash_commands(self) -> list[str]:
        return [str(i.get("command", "")) for n, i in self.tool_uses() if n == "Bash"]

    def tool_names(self) -> list[str]:
        return [n for n, _ in self.tool_uses()]

    def text(self) -> str:
        parts = []
        for ev in self.events:
            if ev.get("type") == "assistant":
                for blk in (ev.get("message") or {}).get("content") or []:
                    if isinstance(blk, dict) and blk.get("type") == "text":
                        parts.append(blk.get("text", ""))
        return "\n".join(parts)

    def hook_blocked(self) -> bool:
        """Did a se-harness gate actually fire during the run (tool_result mentioning BLOCKED)?"""
        return "BLOCKED by se-harness gate" in self.raw


def copilot_bin() -> list[str]:
    """argv prefix for the CLI. EVAL_COPILOT_BIN (a path, or a JSON array) swaps in a stand-in (fake_copilot.py)."""
    override = os.environ.get("EVAL_COPILOT_BIN")
    if override:
        return json.loads(override) if override.lstrip().startswith("[") else [override]
    exe = shutil.which("copilot")
    if not exe:
        raise RuntimeError("`copilot` CLI not found on PATH")
    return [exe]


def _deny_flags() -> list[str]:
    """DENIED ('Bash(docker *)', 'WebFetch', ...) -> Copilot --deny-tool specs ('shell(docker)', ...)."""
    out = []
    for d in DENIED:
        m = re.fullmatch(r"Bash\((\S+)(?: [^)]*)?\)", d)
        if m:
            out += ["--deny-tool", f"shell({m.group(1)})"]
    out += ["--deny-url", "*"]          # offline policy: model API only
    return out


def build_cmd(prompt: str, *, model: str | None, budget: float, session_id: str | None = None,
              resume: str | None = None, persist: bool = False, extra_allowed: list[str] | None = None) -> list[str]:
    # `budget` is kept for call-site compatibility; Copilot CLI has no per-run spend cap.
    cmd = [*copilot_bin(), "-p", prompt, "--output-format", "json",
           "--plugin-dir", posix(PLUGIN_DIR), "--allow-all-tools", *_deny_flags()]
    if model:
        cmd += ["--model", model]
    if resume:
        cmd += ["--resume", resume]
    elif session_id:
        cmd += ["--session-id", session_id]
    return cmd


def parse_stream(raw: str) -> AgentRun:
    run = AgentRun(raw=raw)
    for line in raw.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        run.events.append(ev)
        if ev.get("session_id") and not run.session_id:
            run.session_id = ev["session_id"]
        if ev.get("type") == "result":
            run.ok = not ev.get("is_error", False)
            run.is_error = bool(ev.get("is_error"))
            run.cost_usd = float(ev.get("total_cost_usd") or ev.get("cost_usd") or 0.0)
            run.num_turns = int(ev.get("num_turns") or 0)
            run.result_text = str(ev.get("result") or "")
            if run.is_error:
                run.error = str(ev.get("subtype") or run.result_text)[:300]
    if not any(e.get("type") == "result" for e in run.events):
        run.error = run.error or "no result event (CLI crashed, timed out or auth failed)"
    return run


def run_agent(prompt: str, cwd: Path, *, model: str | None, budget: float, timeout: int = 900,
              session_id: str | None = None, resume: str | None = None, persist: bool = False,
              dry_run: bool = False, extra_allowed: list[str] | None = None) -> AgentRun:
    cmd = build_cmd(prompt, model=model, budget=budget, session_id=session_id, resume=resume,
                    persist=persist or bool(session_id) or bool(resume), extra_allowed=extra_allowed)
    if dry_run:
        r = AgentRun(cmd=cmd, error="dry-run")
        return r
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout, stdin=subprocess.DEVNULL)
        raw = p.stdout
        run = parse_stream(raw)
        if not run.ok and not run.error:
            run.error = p.stderr.strip()[:300]
        elif p.returncode != 0 and not run.events:
            run.error = (p.stderr or "copilot exited non-zero").strip()[:300]
    except subprocess.TimeoutExpired as e:
        raw = (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        run = parse_stream(raw)
        run.error = f"timeout after {timeout}s"
        run.ok = False
    run.cmd = cmd
    return run


def new_session() -> str:
    return str(uuid.uuid4())


# ----------------------------------------------------------------------------- judge

JUDGE_PROMPT = """You are a strict reviewer grading one artifact against yes/no questions.
Answer ONLY from the material below; do not assume anything that is not written there.
If the material does not clearly establish "yes", the answer is "no".

=== MATERIAL ===
{material}
=== END MATERIAL ===

Questions:
{questions}

Reply with a single JSON object and nothing else, mapping each question number (as a string) to
{{"answer": "yes" or "no", "evidence": "<=20 words quoting or pointing at the material"}}."""


def judge(material: str, questions: list[str], *, model: str | None, budget: float = 0.50,
          dry_run: bool = False) -> tuple[list[tuple[str, bool, str]], float]:
    """Pinned-prompt LLM judge. Returns ([(question, passed, evidence)], cost_usd)."""
    qs = "\n".join(f"{i}. {q}" for i, q in enumerate(questions, 1))
    prompt = JUDGE_PROMPT.format(material=material[:60000], questions=qs)
    if dry_run:
        return [(q, True, "dry-run") for q in questions], 0.0
    cmd = [*copilot_bin(), "-p", prompt, "-s", "--deny-tool", "shell", "--deny-tool", "write"]
    if model:
        cmd += ["--model", model]
    import tempfile
    with tempfile.TemporaryDirectory(prefix="se-judge-") as td:
        p = subprocess.run(cmd, cwd=td, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=300, stdin=subprocess.DEVNULL)
    cost = 0.0
    body = p.stdout
    m = re.search(r"\{.*\}", body, re.S)
    try:
        verdict = json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        verdict = {}
    out = []
    for i, q in enumerate(questions, 1):
        v = verdict.get(str(i)) or {}
        out.append((q, str(v.get("answer", "")).strip().lower() == "yes", str(v.get("evidence", ""))[:120]))
    return out, cost
