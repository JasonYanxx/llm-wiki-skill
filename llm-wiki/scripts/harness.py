#!/usr/bin/env python3
"""
harness.py — Maintenance harness for a Chinese-first Research Workbench.

Usage:
    python3 harness.py preflight <workbench-root>
    python3 harness.py postflight <workbench-root>
    python3 harness.py health <workbench-root>
"""

from __future__ import annotations

import json
import re
import sys
from contextlib import redirect_stdout
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Any

from lint_wiki import lint as lint_workbench

FOCUS_KEYS = [
    "Primary active project",
    "Current blocker",
    "Primary repo jump point",
    "Immediate next push",
]
PLACEHOLDER_VALUES = {"", "tbd", "todo", "unknown", "n/a", "none", "待补", "未填写"}
LOG_FILENAME_RE = re.compile(r"^\d{8}\.md$")
REPO_REF_RE = re.compile(r"^repo:([^/]+)/")


def main(argv: list[str]) -> int:
    if len(argv) != 3 or argv[1] not in {"preflight", "postflight", "health"}:
        print(__doc__)
        return 1

    command = argv[1]
    root = Path(argv[2]).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(f"workbench root does not exist: {root}")
        return 1

    if command == "preflight":
        return run_preflight(root)
    if command == "postflight":
        return run_postflight(root)
    return run_health(root)


def run_preflight(root: Path) -> int:
    ops = build_ops_state(root)
    write_ops(root, ops)

    print("Research Workbench harness — preflight\n")
    print(f"工作台: {root}")
    print(f"状态: {ops['maintenance_mode']}")
    if ops["current_focus_ok"]:
        print("Current Focus: 已就绪")
    else:
        print("Current Focus: 未就绪")
        for item in ops["missing_inputs"]:
            print(f"  - 缺少 {item}")

    render_delta_block(ops)
    render_repo_bridge_block(ops)
    print(f"Open audits: {ops['open_audit_count']}")
    print("\n已写入 `compiled/_meta/ops.json`。")
    if ops["maintenance_mode"] == "blocked":
        print("建议先填写 `indexes/Home.md -> Current Focus`，再开始 compile / promote。")
        return 1
    print("可以进入 ingest / compile / review 流程。")
    return 0


def run_health(root: Path) -> int:
    ops_path = root / "compiled/_meta/ops.json"
    ops, issues = load_ops(ops_path)
    if ops is None:
        ops = build_ops_state(root)
        ops["maintenance_mode"] = "blocked"
        ops["missing_inputs"] = sorted(set(ops["missing_inputs"] + ["compiled/_meta/ops.json missing"]))
        issues = issues or ["compiled/_meta/ops.json missing"]

    print("Research Workbench harness — health\n")
    print(f"工作台: {root}")
    print(f"状态: {ops['maintenance_mode']}")
    print(f"Current Focus 就绪: {'yes' if ops['current_focus_ok'] else 'no'}")
    print(f"上次成功闭环: {ops.get('last_successful_loop_at') or '(none)'}")
    print(f"最近 lint: {ops.get('last_lint_status', 'unknown')}")
    if issues:
        print("\nops.json 问题:")
        for item in issues:
            print(f"  - {item}")
    if ops.get("missing_inputs"):
        print("\n缺失输入:")
        for item in ops["missing_inputs"]:
            print(f"  - {item}")
    render_delta_block(ops)
    render_repo_bridge_block(ops)
    print(f"Open audits: {ops['open_audit_count']}")
    return 0 if ops["maintenance_mode"] == "ready" else 1


def run_postflight(root: Path) -> int:
    ops_path = root / "compiled/_meta/ops.json"
    ops, issues = load_ops(ops_path)
    if ops is None:
        print("postflight 无法执行：缺少 `compiled/_meta/ops.json`，请先运行 preflight。")
        for item in issues:
            print(f"  - {item}")
        return 1

    print("Research Workbench harness — postflight\n")
    print("正在运行 lint...\n")
    lint_buffer = StringIO()
    with redirect_stdout(lint_buffer):
        lint_exit = lint_workbench(str(root))
    lint_output = lint_buffer.getvalue().rstrip()
    if lint_output:
        print(lint_output)
        print()

    preflight_at = parse_timestamp(str(ops.get("generated_at", "")))
    if preflight_at is None:
        issues.append("ops.generated_at missing or invalid; run preflight again")

    preflight_delta = ops.get("delta", {}) if isinstance(ops, dict) else {}
    preflight_raw_paths = list(preflight_delta.get("raw_paths", [])) if isinstance(preflight_delta, dict) else []
    preflight_promote_candidates = (
        list(preflight_delta.get("promote_candidates", []))
        if isinstance(preflight_delta, dict)
        else []
    )
    preflight_open_audits = int(ops.get("open_audit_count", 0)) if isinstance(ops, dict) else 0
    had_backlog = bool(preflight_raw_paths or preflight_promote_candidates or preflight_open_audits)

    log_touched = was_log_touched_since(root, preflight_at)
    registry_touched = was_file_touched_since(root / "compiled/_meta/registry.json", preflight_at)
    review_touched = was_file_touched_since(root / "compiled/review/Review.md", preflight_at)
    followthrough_paths = collect_followthrough_paths(root, preflight_at)
    followthrough_ok = (not had_backlog) or bool(followthrough_paths)

    ops = build_ops_state(root, existing_ops=ops)
    ops["last_lint_status"] = "pass" if lint_exit == 0 else "fail"
    if lint_exit == 0 and preflight_at is not None and log_touched and followthrough_ok:
        ops["last_successful_loop_at"] = datetime.now().isoformat()
    write_ops(root, ops)

    print("postflight 检查:")
    print(f"- log 已追加: {'yes' if log_touched else 'no'}")
    print(f"- registry 已更新: {'yes' if registry_touched else 'no'}")
    print(f"- review 已更新: {'yes' if review_touched else 'no'}")
    print(f"- 有效跟进输出: {'yes' if followthrough_paths else 'no'}")
    print(f"- lint 结果: {ops['last_lint_status']}")
    if followthrough_paths:
        for rel in followthrough_paths[:10]:
            print(f"  - {rel}")

    failure_reasons: list[str] = []
    if lint_exit != 0:
        failure_reasons.append("lint failed")
    if not log_touched:
        failure_reasons.append("log not updated after preflight")
    if ops["maintenance_mode"] != "ready":
        failure_reasons.append("workbench still blocked")
    if had_backlog and not followthrough_paths:
        failure_reasons.append(
            "backlog still has no compiled/index/review/query/audit follow-through after preflight"
        )

    if failure_reasons:
        print("\n本轮尚未构成成功闭环:")
        for item in failure_reasons:
            print(f"  - {item}")
        return 1

    print("\n本轮维护闭环已确认，`ops.json` 已更新。")
    return 0


def build_ops_state(root: Path, existing_ops: dict[str, Any] | None = None) -> dict[str, Any]:
    now_iso = datetime.now().isoformat()
    existing = existing_ops or load_ops(root / "compiled/_meta/ops.json")[0] or {}

    missing_inputs: list[str] = []
    workbench_path = root / "WORKBENCH.md"
    home_path = root / "indexes/Home.md"
    registry_path = root / "compiled/_meta/registry.json"

    if not workbench_path.exists():
        missing_inputs.append("WORKBENCH.md missing")
    if not home_path.exists():
        missing_inputs.append("indexes/Home.md missing")
        focus_fields = {}
    else:
        focus_fields = parse_current_focus(home_path.read_text(encoding="utf-8"))
        for key in FOCUS_KEYS:
            value = focus_fields.get(key, "").strip()
            if not value or value.lower() in PLACEHOLDER_VALUES:
                missing_inputs.append(f"Current Focus / {key}")

    registry, _ = load_json(registry_path)
    delta_since = parse_timestamp(existing.get("last_successful_loop_at")) if isinstance(existing, dict) else None
    raw_delta = collect_recent_raw_paths(root, delta_since)
    promote_candidates = collect_promote_candidates(root, delta_since)
    pending_repo_bridge = collect_pending_repo_bridge(root, registry)
    open_audit_count = count_open_audits(root)

    return {
        "generated_at": now_iso,
        "current_focus_ok": not any(item.startswith("Current Focus /") for item in missing_inputs),
        "missing_inputs": missing_inputs,
        "maintenance_mode": "ready" if not missing_inputs else "blocked",
        "delta": {
            "raw_paths": raw_delta,
            "promote_candidates": promote_candidates,
        },
        "open_audit_count": open_audit_count,
        "pending_repo_bridge": pending_repo_bridge,
        "last_successful_loop_at": existing.get("last_successful_loop_at") if isinstance(existing, dict) else None,
        "last_lint_status": existing.get("last_lint_status", "unknown") if isinstance(existing, dict) else "unknown",
    }


def render_delta_block(ops: dict[str, Any]) -> None:
    delta = ops.get("delta", {})
    raw_paths = list(delta.get("raw_paths", [])) if isinstance(delta, dict) else []
    promote_candidates = list(delta.get("promote_candidates", [])) if isinstance(delta, dict) else []
    print("\nRaw delta:")
    if raw_paths:
        for rel in raw_paths[:10]:
            print(f"  - {rel}")
    else:
        print("  - 无新的 raw 增量")
    print("\nPromote candidates:")
    if promote_candidates:
        for rel in promote_candidates[:10]:
            print(f"  - {rel}")
    else:
        print("  - 暂无候选")


def render_repo_bridge_block(ops: dict[str, Any]) -> None:
    pending = ops.get("pending_repo_bridge", [])
    print("\nPending repo bridge:")
    if pending:
        for slug in pending:
            print(f"  - {slug}")
    else:
        print("  - 无待确认 repo root")


def parse_current_focus(text: str) -> dict[str, str]:
    lines = text.splitlines()
    in_section = False
    section_lines: list[str] = []
    for line in lines:
        if re.match(r"^##\s+", line):
            if in_section:
                break
            if line.strip() == "## Current Focus":
                in_section = True
            continue
        if in_section:
            section_lines.append(line)

    fields: dict[str, str] = {}
    for line in section_lines:
        match = re.match(r"^\s*-\s*([^:]+):\s*(.*)\s*$", line)
        if not match:
            continue
        key = match.group(1).strip()
        value = match.group(2).strip()
        fields[key] = value
    return fields


def collect_recent_raw_paths(root: Path, since: datetime | None) -> list[str]:
    raw_root = root / "raw"
    if not raw_root.exists():
        return []
    candidates = []
    for path in raw_root.rglob("*"):
        if not path.is_file() or path.name.startswith(".") or path.name == ".gitkeep":
            continue
        stat = path.stat()
        modified = datetime.fromtimestamp(stat.st_mtime)
        if since is None or modified > since:
            candidates.append((modified, path.relative_to(root).as_posix()))
    candidates.sort(reverse=True)
    return [rel for _mtime, rel in candidates[:12]]


def collect_promote_candidates(root: Path, since: datetime | None) -> list[str]:
    query_root = root / "outputs/queries"
    if not query_root.exists():
        return []
    candidates = []
    for path in query_root.glob("*.md"):
        name = path.name.lower()
        if "promote" not in name and "candidate" not in name:
            continue
        modified = datetime.fromtimestamp(path.stat().st_mtime)
        if since is None or modified > since:
            candidates.append((modified, path.relative_to(root).as_posix()))
    candidates.sort(reverse=True)
    return [rel for _mtime, rel in candidates[:10]]


def collect_pending_repo_bridge(root: Path, registry: dict[str, Any] | None) -> list[str]:
    pending: set[str] = set()
    repo_roots = {}
    if isinstance(registry, dict):
        meta = registry.get("meta", {})
        if isinstance(meta, dict) and isinstance(meta.get("repo_roots"), dict):
            repo_roots = meta["repo_roots"]

    objects = registry.get("objects", []) if isinstance(registry, dict) else []
    for obj in objects:
        if not isinstance(obj, dict):
            continue
        source_refs = obj.get("source_refs", [])
        if isinstance(source_refs, list):
            for ref in source_refs:
                if not isinstance(ref, str):
                    continue
                match = REPO_REF_RE.match(ref)
                if match and match.group(1) not in repo_roots:
                    pending.add(match.group(1))

        object_path = obj.get("path")
        if not isinstance(object_path, str) or obj.get("type") != "project":
            continue
        path = root / object_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        repo_slug_match = re.search(r"^repo_slug:\s*(.+?)\s*$", text, re.MULTILINE)
        if repo_slug_match:
            slug = repo_slug_match.group(1).strip().strip("'\"")
            if slug and slug not in repo_roots:
                pending.add(slug)
    return sorted(pending)


def count_open_audits(root: Path) -> int:
    audit_root = root / "audit"
    if not audit_root.exists():
        return 0
    count = 0
    for path in audit_root.rglob("*.md"):
        if "resolved" in path.parts or path.name.startswith("."):
            continue
        count += 1
    return count


def load_json(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    if not path.exists():
        return None, [f"{path.relative_to(path.parent.parent.parent) if path.is_absolute() else path} missing"]
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        return None, [f"{path} is not valid JSON: {err}"]
    if not isinstance(parsed, dict):
        return None, [f"{path} must contain a JSON object"]
    return parsed, []


def load_ops(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    ops, issues = load_json(path)
    if ops is None:
        return None, issues

    required = {
        "generated_at",
        "current_focus_ok",
        "missing_inputs",
        "maintenance_mode",
        "delta",
        "open_audit_count",
        "pending_repo_bridge",
        "last_successful_loop_at",
        "last_lint_status",
    }
    missing = required - set(ops.keys())
    if missing:
        issues.append(f"ops.json missing keys: {', '.join(sorted(missing))}")
    if not isinstance(ops.get("missing_inputs"), list):
        issues.append("ops.json `missing_inputs` must be a list")
    if not isinstance(ops.get("delta"), dict):
        issues.append("ops.json `delta` must be an object")
    if not isinstance(ops.get("pending_repo_bridge"), list):
        issues.append("ops.json `pending_repo_bridge` must be a list")
    return ops, issues


def write_ops(root: Path, ops: dict[str, Any]) -> None:
    path = root / "compiled/_meta/ops.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ops, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.strip())
    except ValueError:
        return None


def was_log_touched_since(root: Path, since: datetime | None) -> bool:
    log_root = root / "log"
    if since is None or not log_root.exists():
        return False
    for path in sorted(log_root.glob("*.md")):
        if not LOG_FILENAME_RE.match(path.name):
            continue
        modified = datetime.fromtimestamp(path.stat().st_mtime)
        if modified >= since:
            return True
    return False


def was_file_touched_since(path: Path, since: datetime | None) -> bool:
    if since is None or not path.exists():
        return False
    return datetime.fromtimestamp(path.stat().st_mtime) >= since


def collect_followthrough_paths(root: Path, since: datetime | None) -> list[str]:
    if since is None:
        return []

    touched: list[str] = []
    candidate_roots = [
        root / "compiled",
        root / "indexes",
        root / "outputs" / "queries",
        root / "audit",
    ]

    for base in candidate_roots:
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            if path.name.startswith(".") or path.name == ".gitkeep":
                continue
            rel = path.relative_to(root).as_posix()
            if rel == "compiled/_meta/ops.json":
                continue
            if datetime.fromtimestamp(path.stat().st_mtime) >= since:
                touched.append(rel)
    return touched


if __name__ == "__main__":
    sys.exit(main(sys.argv))
