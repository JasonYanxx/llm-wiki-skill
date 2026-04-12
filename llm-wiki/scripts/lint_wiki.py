#!/usr/bin/env python3
"""
lint_wiki.py — Structural + harness-readiness health check for a Research Workbench.

Usage:
    python3 lint_wiki.py <workbench-root>

Checks:
  1. Canonical root shape (`WORKBENCH.md`, `compiled/`, `indexes/`, registry)
  2. Registry validity and registry/page drift
  3. `ops.json` plus `Current Focus` readiness
  4. Missing or incomplete generated index coverage
  5. Chinese-first profile and local noise policy
  6. Missing provenance sections on compiled pages
  7. Disconnected compiled objects
  8. Stale compiled pages whose source refs changed
  9. Unresolved wikilinks in compiled/index pages
  10. log/ shape
  11. audit/ shape and audit target validity

Exit codes:
  0 — no issues found
  1 — issues found
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path


WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
LOG_FILENAME_RE = re.compile(r"^(\d{4})(\d{2})(\d{2})\.md$")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)

REGISTRY_REQUIRED_FIELDS = {
    "id",
    "type",
    "path",
    "title",
    "status",
    "summary",
    "updated_at",
    "source_count",
    "audit_open_count",
    "source_refs",
    "related_object_ids",
}
VALID_TYPES = {"project", "idea", "knowledge", "people", "review"}
OPS_REQUIRED_FIELDS = {
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
VALID_MAINTENANCE_MODES = {"blocked", "ready"}
VALID_LINT_STATUSES = {"unknown", "pass", "fail"}
INDEX_BY_TYPE = {
    "project": "indexes/Projects.md",
    "idea": "indexes/Ideas.md",
    "knowledge": "indexes/Knowledge.md",
    "people": "indexes/People.md",
    "review": "indexes/Review.md",
}
HOME_REQUIRED_HEADINGS = [
    "Current Focus",
    "Projects",
    "Ideas",
    "Review",
    "People",
    "Recent Changes",
]
CURRENT_FOCUS_KEYS = [
    "Primary active project",
    "Current blocker",
    "Primary repo jump point",
    "Immediate next push",
]
CHINESE_PROFILE_TARGETS = [
    "WORKBENCH.md",
    "indexes/Home.md",
    "indexes/Projects.md",
    "indexes/Ideas.md",
    "indexes/Knowledge.md",
    "indexes/People.md",
    "indexes/Review.md",
    "compiled/review/Review.md",
]
CJK_RE = re.compile(r"[\u3400-\u9fff]")

AUDIT_REQUIRED_FIELDS = {
    "id",
    "target",
    "target_lines",
    "anchor_before",
    "anchor_text",
    "anchor_after",
    "severity",
    "author",
    "source",
    "created",
    "status",
}
VALID_SEVERITIES = {"info", "suggest", "warn", "error"}
VALID_STATUSES = {"open", "resolved"}
VALID_SOURCES = {"obsidian-plugin", "web-viewer", "manual"}


def collect_root_markdown_files(root: Path) -> list[Path]:
    return sorted(
        path for path in root.glob("*.md")
        if path.is_file() and not path.name.startswith(".")
    )


def collect_markdown_files(root: Path, rel_dir: str) -> list[Path]:
    base = root / rel_dir
    if not base.exists():
        return []
    return sorted(
        p for p in base.rglob("*.md")
        if not any(part.startswith(".") for part in p.relative_to(root).parts)
    )


def build_page_lookup(root: Path) -> dict[str, Path]:
    pages: dict[str, Path] = {}
    for path in collect_root_markdown_files(root):
        rel = path.relative_to(root).as_posix()
        no_ext = path.relative_to(root).with_suffix("").as_posix()
        stem = path.stem
        pages.setdefault(rel, path)
        pages.setdefault(no_ext, path)
        pages.setdefault(stem, path)
        pages.setdefault(stem.lower(), path)

    for rel_dir in ("compiled", "indexes", "raw", "outputs", "wiki"):
        base = root / rel_dir
        if not base.exists():
            continue
        for path in base.rglob("*.md"):
            rel = path.relative_to(root).as_posix()
            no_ext = path.relative_to(root).with_suffix("").as_posix()
            stem = path.stem

            pages.setdefault(rel, path)
            pages.setdefault(no_ext, path)
            pages.setdefault(stem, path)
            pages.setdefault(stem.lower(), path)

            base_rel = path.relative_to(base).with_suffix("").as_posix()
            pages.setdefault(base_rel, path)
            pages.setdefault(base_rel.lower(), path)

            if path.name == "index.md":
                parent_rel = path.parent.relative_to(root).as_posix()
                pages.setdefault(parent_rel, path)
                parent_under_base = path.parent.relative_to(base).as_posix()
                pages.setdefault(parent_under_base, path)
                parent_name = path.parent.name
                pages.setdefault(parent_name, path)
                pages.setdefault(parent_name.lower(), path)
    return pages


def extract_wikilinks(text: str) -> list[str]:
    return [match.strip() for match in WIKILINK_RE.findall(text)]


def parse_frontmatter(text: str) -> dict | None:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None
    body = match.group(1)
    result: dict = {}
    for line in body.split("\n"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, rest = line.partition(":")
        key = key.strip()
        val = rest.strip()
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            if not inner:
                result[key] = []
            else:
                result[key] = [p.strip().strip('"').strip("'") for p in inner.split(",") if p.strip()]
        elif val.startswith('"') and val.endswith('"'):
            result[key] = val[1:-1].replace("\\n", "\n").replace('\\"', '"')
        elif val.startswith("'") and val.endswith("'"):
            result[key] = val[1:-1]
        else:
            result[key] = val
    return result


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

    result: dict[str, str] = {}
    for line in section_lines:
        match = re.match(r"^\s*-\s*([^:]+):\s*(.*)\s*$", line)
        if not match:
            continue
        result[match.group(1).strip()] = match.group(2).strip()
    return result


def load_registry(path: Path) -> tuple[dict | None, list[str]]:
    issues: list[str] = []
    if not path.exists():
        return None, [f"{path} is missing"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        return None, [f"{path} is not valid JSON: {err}"]

    if not isinstance(data, dict):
        return None, [f"{path} must contain a top-level object"]
    if "meta" not in data or not isinstance(data["meta"], dict):
        issues.append("registry missing top-level `meta` object")
    if "objects" not in data or not isinstance(data["objects"], list):
        issues.append("registry missing top-level `objects` array")
        return data, issues
    repo_roots = data["meta"].get("repo_roots") if isinstance(data.get("meta"), dict) else None
    if repo_roots is not None and not isinstance(repo_roots, dict):
        issues.append("registry.meta.repo_roots must be an object when present")
    elif isinstance(repo_roots, dict):
        for slug, repo_root in repo_roots.items():
            if not isinstance(slug, str) or not slug:
                issues.append("registry.meta.repo_roots contains a non-string or empty slug")
            if not isinstance(repo_root, str) or not repo_root.strip():
                issues.append(f"registry.meta.repo_roots[{slug!r}] must be a non-empty string path")

    for index, obj in enumerate(data["objects"]):
        prefix = f"registry.objects[{index}]"
        if not isinstance(obj, dict):
            issues.append(f"{prefix} must be an object")
            continue
        missing = REGISTRY_REQUIRED_FIELDS - set(obj.keys())
        if missing:
            issues.append(f"{prefix} missing fields: {', '.join(sorted(missing))}")
        obj_type = obj.get("type")
        if obj_type not in VALID_TYPES:
            issues.append(f"{prefix} has invalid type `{obj_type}`")
        if not isinstance(obj.get("source_refs", []), list):
            issues.append(f"{prefix}.source_refs must be an array")
        if not isinstance(obj.get("related_object_ids", []), list):
            issues.append(f"{prefix}.related_object_ids must be an array")
    return data, issues


def load_ops(path: Path) -> tuple[dict | None, list[str]]:
    issues: list[str] = []
    if not path.exists():
        return None, [f"{path} is missing"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        return None, [f"{path} is not valid JSON: {err}"]

    if not isinstance(data, dict):
        return None, [f"{path} must contain a top-level object"]

    missing = OPS_REQUIRED_FIELDS - set(data.keys())
    if missing:
        issues.append(f"ops.json missing fields: {', '.join(sorted(missing))}")

    if data.get("maintenance_mode") not in VALID_MAINTENANCE_MODES:
        issues.append(f"ops.json has invalid maintenance_mode `{data.get('maintenance_mode')}`")
    if data.get("last_lint_status") not in VALID_LINT_STATUSES:
        issues.append(f"ops.json has invalid last_lint_status `{data.get('last_lint_status')}`")
    if not isinstance(data.get("missing_inputs"), list):
        issues.append("ops.json `missing_inputs` must be a list")
    if not isinstance(data.get("pending_repo_bridge"), list):
        issues.append("ops.json `pending_repo_bridge` must be a list")
    if not isinstance(data.get("delta"), dict):
        issues.append("ops.json `delta` must be an object")
    else:
        delta = data["delta"]
        if not isinstance(delta.get("raw_paths"), list):
            issues.append("ops.json `delta.raw_paths` must be a list")
        if not isinstance(delta.get("promote_candidates"), list):
            issues.append("ops.json `delta.promote_candidates` must be a list")
    return data, issues


def resolve_vault_ref(root: Path, ref: str) -> Path | None:
    if not ref.startswith("vault:"):
        return None
    rel = ref[len("vault:"):].lstrip("/")
    full = root / rel
    if full.is_dir():
        index = full / "index.md"
        return index if index.exists() else None
    return full if full.exists() else None


def resolve_repo_ref(root: Path, ref: str, repo_roots: dict[str, str]) -> tuple[Path | None, str | None]:
    if not ref.startswith("repo:"):
        return None, None

    rel = ref[len("repo:"):]
    slug, sep, inner_path = rel.partition("/")
    if not sep or not slug or not inner_path:
        return None, f"invalid repo source ref `{ref}` (expected `repo:<project-slug>/<path>`)"

    repo_root_raw = repo_roots.get(slug)
    if not isinstance(repo_root_raw, str) or not repo_root_raw.strip():
        return None, f"repo source ref `{ref}` cannot be resolved because `{slug}` is missing from registry.meta.repo_roots"

    repo_root = Path(repo_root_raw).expanduser()
    if not repo_root.is_absolute():
        repo_root = root / repo_root
    repo_root = repo_root.resolve()
    target = (repo_root / inner_path).resolve()

    try:
        target.relative_to(repo_root)
    except ValueError:
        return None, f"repo source ref `{ref}` escapes the configured repo root `{repo_root}`"

    if not target.exists():
        return None, f"repo source ref `{ref}` points to a missing file `{target}`"
    if target.is_dir():
        index = target / "index.md"
        if index.exists():
            return index, None
        return None, f"repo source ref `{ref}` points to a directory without `index.md`"

    return target, None


def lint(root: str) -> int:
    root_path = Path(root)
    issues = 0

    root_markdown_files = collect_root_markdown_files(root_path)
    compiled_files = [
        p for p in collect_markdown_files(root_path, "compiled")
        if "_meta" not in p.relative_to(root_path).parts
    ]
    index_files = collect_markdown_files(root_path, "indexes")
    page_lookup = build_page_lookup(root_path)

    print("Research Workbench lint\n")

    # ── Pass 1: canonical root shape ──────────────────────────────────────
    root_issues: list[str] = []
    for rel in (
        "WORKBENCH.md",
        "compiled",
        "compiled/_meta/registry.json",
        "compiled/_meta/ops.json",
        "indexes",
        "audit",
        "log",
        "outputs/queries",
        "raw",
    ):
        path = root_path / rel
        if not path.exists():
            root_issues.append(f"missing `{rel}`")
    if root_issues:
        print(f"🔴 Canonical root shape issues ({len(root_issues)}):")
        for item in root_issues:
            print(f"   {item}")
        issues += len(root_issues)
    else:
        print("✅ Canonical root shape OK")

    # ── Pass 2: registry validity and drift ───────────────────────────────
    registry_path = root_path / "compiled/_meta/registry.json"
    registry, registry_issues = load_registry(registry_path)
    registry_objects = registry.get("objects", []) if registry else []
    registry_ids: set[str] = set()
    registry_paths: set[str] = set()
    duplicate_id_issues: list[str] = []
    duplicate_path_issues: list[str] = []
    missing_path_issues: list[str] = []
    object_by_path: dict[str, dict] = {}

    for obj in registry_objects:
        if not isinstance(obj, dict):
            continue
        object_id = obj.get("id")
        object_path = obj.get("path")
        if isinstance(object_id, str):
            if object_id in registry_ids:
                duplicate_id_issues.append(f"duplicate registry id `{object_id}`")
            registry_ids.add(object_id)
        if isinstance(object_path, str):
            if object_path in registry_paths:
                duplicate_path_issues.append(f"duplicate registry path `{object_path}`")
            registry_paths.add(object_path)
            object_by_path[object_path] = obj
            full = root_path / object_path
            if not full.exists():
                missing_path_issues.append(f"registry path missing on disk: `{object_path}`")

    unregistered_compiled = [
        p.relative_to(root_path).as_posix()
        for p in compiled_files
        if p.relative_to(root_path).as_posix() not in registry_paths
    ]

    registry_issue_block = registry_issues + duplicate_id_issues + duplicate_path_issues + missing_path_issues
    if registry_issue_block or unregistered_compiled:
        total = len(registry_issue_block) + len(unregistered_compiled)
        print(f"\n🔴 Registry issues ({total}):")
        for item in registry_issue_block:
            print(f"   {item}")
        for item in unregistered_compiled:
            print(f"   compiled page missing from registry: `{item}`")
        issues += total
    else:
        print("✅ Registry valid and aligned with compiled pages")

    # ── Pass 3: ops.json and Current Focus readiness ─────────────────────
    ops_path = root_path / "compiled/_meta/ops.json"
    ops, ops_schema_issues = load_ops(ops_path)
    runtime_issues: list[str] = list(ops_schema_issues)

    home_path = "indexes/Home.md"
    home_text = (root_path / home_path).read_text(encoding="utf-8") if (root_path / home_path).exists() else ""
    focus_fields = parse_current_focus(home_text) if home_text else {}
    missing_focus_keys = [key for key in CURRENT_FOCUS_KEYS if not focus_fields.get(key, "").strip()]
    for key in missing_focus_keys:
        runtime_issues.append(f"indexes/Home.md has empty Current Focus field `{key}`")

    expected_focus_ok = not missing_focus_keys
    if ops is not None:
        if ops.get("current_focus_ok") != expected_focus_ok:
            runtime_issues.append(
                "ops.json `current_focus_ok` does not match indexes/Home.md Current Focus readiness"
            )
        if expected_focus_ok and ops.get("maintenance_mode") == "blocked":
            runtime_issues.append(
                "ops.json keeps `maintenance_mode` blocked even though Current Focus is filled"
            )
        if not expected_focus_ok and ops.get("maintenance_mode") != "blocked":
            runtime_issues.append(
                "ops.json should be `blocked` while required Current Focus fields are empty"
            )

    if runtime_issues:
        print(f"\n🔴 Harness readiness issues ({len(runtime_issues)}):")
        for item in runtime_issues:
            print(f"   {item}")
        issues += len(runtime_issues)
    else:
        print("✅ Harness readiness OK")

    # ── Pass 4: index coverage and home structure ─────────────────────────
    index_issues: list[str] = []
    index_texts = {
        p.relative_to(root_path).as_posix(): p.read_text(encoding="utf-8")
        for p in index_files
    }
    home_text = index_texts.get(home_path, "")
    if not home_text:
        index_issues.append("missing indexes/Home.md")
    else:
        for heading in HOME_REQUIRED_HEADINGS:
            if re.search(rf"^##\s+{re.escape(heading)}\s*$", home_text, re.MULTILINE) is None:
                index_issues.append(f"indexes/Home.md missing section `{heading}`")

    for obj in registry_objects:
        if not isinstance(obj, dict):
            continue
        object_type = obj.get("type")
        object_path = obj.get("path")
        object_title = obj.get("title")
        if not isinstance(object_type, str) or not isinstance(object_path, str):
            continue
        index_rel = INDEX_BY_TYPE.get(object_type)
        if not index_rel:
            continue
        index_text = index_texts.get(index_rel)
        if not index_text:
            index_issues.append(f"missing `{index_rel}` for registry type `{object_type}`")
            continue
        object_no_ext = object_path[:-3] if object_path.endswith(".md") else object_path
        object_basename = Path(object_no_ext).name
        if (
            object_path not in index_text
            and object_no_ext not in index_text
            and (not isinstance(object_title, str) or f"[[{object_title}]]" not in index_text)
            and object_basename not in index_text
        ):
            index_issues.append(f"`{index_rel}` does not mention `{object_path}`")

    if index_issues:
        print(f"\n🟡 Index coverage issues ({len(index_issues)}):")
        for item in index_issues:
            print(f"   {item}")
        issues += len(index_issues)
    else:
        print("✅ Index coverage OK")

    # ── Pass 5: Chinese-first profile and local noise policy ─────────────
    profile_issues: list[str] = []
    for rel in CHINESE_PROFILE_TARGETS:
        path = root_path / rel
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if CJK_RE.search(text) is None:
            profile_issues.append(f"`{rel}` should be Chinese-first but currently contains no Chinese text")

    gitignore_path = root_path / ".gitignore"
    if not gitignore_path.exists():
        profile_issues.append("missing `.gitignore` at the workbench root")
    else:
        gitignore_text = gitignore_path.read_text(encoding="utf-8")
        if ".obsidian/graph.json" not in gitignore_text:
            profile_issues.append("`.gitignore` should ignore `.obsidian/graph.json`")

    if profile_issues:
        print(f"\n🟡 Profile / noise policy issues ({len(profile_issues)}):")
        for item in profile_issues:
            print(f"   {item}")
        issues += len(profile_issues)
    else:
        print("✅ Chinese-first profile and local noise policy OK")

    # ── Pass 6: provenance sections ───────────────────────────────────────
    provenance_issues = []
    for path in compiled_files:
        if path.relative_to(root_path).as_posix() == "compiled/review/Review.md":
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(r"^##\s+Provenance\s*$", text, re.MULTILINE) is None:
            provenance_issues.append(path.relative_to(root_path).as_posix())
    if provenance_issues:
        print(f"\n🟡 Missing provenance sections ({len(provenance_issues)}):")
        for rel in provenance_issues:
            print(f"   {rel}")
        issues += len(provenance_issues)
    else:
        print("✅ All compiled pages include a Provenance section")

    # ── Pass 7: disconnected compiled objects ─────────────────────────────
    compiled_lookup = {
        rel: path for rel, path in page_lookup.items()
        if isinstance(path, Path) and "compiled" in path.relative_to(root_path).parts
    }
    outbound_counts: dict[str, int] = defaultdict(int)
    inbound_counts: dict[str, int] = defaultdict(int)
    for path in compiled_files:
        rel = path.relative_to(root_path).as_posix()
        text = path.read_text(encoding="utf-8")
        resolved_targets: set[str] = set()
        for target in extract_wikilinks(text):
            candidate = (
                compiled_lookup.get(target)
                or compiled_lookup.get(target.lower())
                or compiled_lookup.get(Path(target).stem)
                or compiled_lookup.get(Path(target).stem.lower())
            )
            if not candidate:
                continue
            tgt_rel = candidate.relative_to(root_path).as_posix()
            if tgt_rel == rel or tgt_rel in resolved_targets:
                continue
            resolved_targets.add(tgt_rel)
            outbound_counts[rel] += 1
            inbound_counts[tgt_rel] += 1

    disconnected = []
    for path in compiled_files:
        rel = path.relative_to(root_path).as_posix()
        registry_obj = object_by_path.get(rel, {})
        related_ids = registry_obj.get("related_object_ids", []) if isinstance(registry_obj, dict) else []
        object_type = registry_obj.get("type")
        if object_type == "review":
            continue
        if outbound_counts[rel] == 0 and inbound_counts[rel] == 0 and not related_ids:
            disconnected.append(rel)

    if disconnected:
        print(f"\n🟡 Disconnected compiled objects ({len(disconnected)}):")
        for rel in disconnected:
            print(f"   {rel}")
        issues += len(disconnected)
    else:
        print("✅ No disconnected compiled objects")

    # ── Pass 8: stale compiled pages ──────────────────────────────────────
    registry_meta = registry.get("meta", {}) if isinstance(registry, dict) else {}
    repo_roots = registry_meta.get("repo_roots", {}) if isinstance(registry_meta, dict) else {}
    if not isinstance(repo_roots, dict):
        repo_roots = {}
    stale_issues: list[str] = []
    source_ref_issues: list[str] = []
    for obj in registry_objects:
        if not isinstance(obj, dict):
            continue
        object_path = obj.get("path")
        source_refs = obj.get("source_refs", [])
        if not isinstance(object_path, str) or not isinstance(source_refs, list):
            continue
        object_file = root_path / object_path
        if not object_file.exists():
            continue
        object_mtime = object_file.stat().st_mtime
        for ref in source_refs:
            if not isinstance(ref, str):
                continue
            if ref.startswith("repo:"):
                source_path, source_issue = resolve_repo_ref(root_path, ref, repo_roots)
                if source_issue:
                    source_ref_issues.append(source_issue)
                    continue
            else:
                source_path = resolve_vault_ref(root_path, ref)
                source_issue = None
            if not source_path:
                continue
            if source_path.stat().st_mtime > object_mtime:
                stale_issues.append(f"`{object_path}` is older than `{ref}`")

    if source_ref_issues:
        print(f"\n🔴 Source ref resolution issues ({len(source_ref_issues)}):")
        for item in source_ref_issues:
            print(f"   {item}")
        issues += len(source_ref_issues)

    if stale_issues:
        print(f"\n🟡 Potentially stale compiled pages ({len(stale_issues)}):")
        for item in stale_issues:
            print(f"   {item}")
        issues += len(stale_issues)
    else:
        if not source_ref_issues:
            print("✅ No stale compiled pages detected from vault or repo source refs")

    # ── Pass 9: unresolved wikilinks ──────────────────────────────────────
    link_issues: list[str] = []
    page_scan_files = root_markdown_files + compiled_files + index_files
    for path in page_scan_files:
        rel = path.relative_to(root_path).as_posix()
        text = path.read_text(encoding="utf-8")
        for target in extract_wikilinks(text):
            if (
                target not in page_lookup
                and target.lower() not in page_lookup
                and Path(target).stem not in page_lookup
                and Path(target).stem.lower() not in page_lookup
            ):
                link_issues.append(f"{rel} -> [[{target}]]")
    if link_issues:
        print(f"\n🟡 Unresolved wikilinks ({len(link_issues)}):")
        for item in link_issues:
            print(f"   {item}")
        issues += len(link_issues)
    else:
        print("✅ No unresolved wikilinks in compiled/index pages")

    # ── Pass 10: log shape ────────────────────────────────────────────────
    log_path = root_path / "log"
    log_issues: list[str] = []
    if log_path.exists() and log_path.is_dir():
        for path in sorted(log_path.iterdir()):
            if path.is_dir() or path.name == ".gitkeep":
                continue
            match = LOG_FILENAME_RE.match(path.name)
            if not match:
                log_issues.append(f"{path.relative_to(root_path)} filename does not match YYYYMMDD.md")
                continue
            year, month, day = match.groups()
            iso = f"{year}-{month}-{day}"
            first_line = path.read_text(encoding="utf-8").splitlines()[:1]
            if not first_line or first_line[0].strip() != f"# {iso}":
                log_issues.append(f"{path.relative_to(root_path)} expected H1 `# {iso}`")
    else:
        log_issues.append("log/ directory not found")

    if log_issues:
        print(f"\n🟡 log/ shape issues ({len(log_issues)}):")
        for item in log_issues:
            print(f"   {item}")
        issues += len(log_issues)
    else:
        print("✅ log/ shape OK")

    # ── Pass 11: audit shape and targets ──────────────────────────────────
    audit_dir = root_path / "audit"
    audit_issues: list[str] = []
    if audit_dir.exists() and audit_dir.is_dir():
        audit_files = [p for p in audit_dir.rglob("*.md") if p.name != ".gitkeep"]
        for path in audit_files:
            text = path.read_text(encoding="utf-8")
            fm = parse_frontmatter(text)
            rel = path.relative_to(root_path).as_posix()
            if fm is None:
                audit_issues.append(f"{rel} missing YAML frontmatter")
                continue
            missing = AUDIT_REQUIRED_FIELDS - set(fm.keys())
            if missing:
                audit_issues.append(f"{rel} missing fields: {', '.join(sorted(missing))}")
                continue
            if fm["severity"] not in VALID_SEVERITIES:
                audit_issues.append(f"{rel} invalid severity `{fm['severity']}`")
            if fm["source"] not in VALID_SOURCES:
                audit_issues.append(f"{rel} invalid source `{fm['source']}`")
            expected_status = "resolved" if "resolved" in path.parts else "open"
            if fm["status"] not in VALID_STATUSES or fm["status"] != expected_status:
                audit_issues.append(f"{rel} status `{fm['status']}` does not match directory")

            target = fm.get("target")
            if isinstance(target, str):
                target_path = root_path / target
                if not target_path.exists():
                    audit_issues.append(f"{rel} target does not exist: `{target}`")
    else:
        audit_issues.append("audit/ directory not found")

    if audit_issues:
        print(f"\n🟡 audit/ issues ({len(audit_issues)}):")
        for item in audit_issues:
            print(f"   {item}")
        issues += len(audit_issues)
    else:
        print("✅ audit/ shape and targets OK")

    print()
    if issues:
        print(f"Found {issues} issue(s).")
        return 1
    print("No issues found.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    sys.exit(lint(sys.argv[1]))
