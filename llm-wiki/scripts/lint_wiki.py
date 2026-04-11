#!/usr/bin/env python3
"""
lint_wiki.py — Health check for a Research Workbench.

Usage:
    python3 lint_wiki.py <workbench-root>

Checks:
  1. Canonical root shape (`WORKBENCH.md`, `compiled/`, `indexes/`, registry)
  2. Registry validity and registry/page drift
  3. Missing or incomplete generated index coverage
  4. Missing provenance sections on compiled pages
  5. Disconnected compiled objects
  6. Stale compiled pages whose source refs changed
  7. Unresolved wikilinks in compiled/index pages
  8. log/ shape
  9. audit/ shape and audit target validity

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


def resolve_vault_ref(root: Path, ref: str) -> Path | None:
    if not ref.startswith("vault:"):
        return None
    rel = ref[len("vault:"):].lstrip("/")
    full = root / rel
    if full.is_dir():
        index = full / "index.md"
        return index if index.exists() else None
    return full if full.exists() else None


def lint(root: str) -> int:
    root_path = Path(root)
    issues = 0

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

    # ── Pass 3: index coverage and home structure ─────────────────────────
    index_issues: list[str] = []
    index_texts = {
        p.relative_to(root_path).as_posix(): p.read_text(encoding="utf-8")
        for p in index_files
    }
    home_path = "indexes/Home.md"
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

    # ── Pass 4: provenance sections ───────────────────────────────────────
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

    # ── Pass 5: disconnected compiled objects ─────────────────────────────
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

    # ── Pass 6: stale compiled pages ──────────────────────────────────────
    stale_issues: list[str] = []
    skipped_repo_refs = 0
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
                skipped_repo_refs += 1
                continue
            source_path = resolve_vault_ref(root_path, ref)
            if not source_path:
                continue
            if source_path.stat().st_mtime > object_mtime:
                stale_issues.append(f"`{object_path}` is older than `{ref}`")
    if stale_issues:
        print(f"\n🟡 Potentially stale compiled pages ({len(stale_issues)}):")
        for item in stale_issues:
            print(f"   {item}")
        issues += len(stale_issues)
    else:
        print("✅ No stale compiled pages detected from vault source refs")
    if skipped_repo_refs:
        print(f"ℹ️  Skipped {skipped_repo_refs} repo source refs (repo timestamps are not resolved by this lint pass)")

    # ── Pass 7: unresolved wikilinks ──────────────────────────────────────
    link_issues: list[str] = []
    page_scan_files = compiled_files + index_files
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

    # ── Pass 8: log shape ─────────────────────────────────────────────────
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

    # ── Pass 9: audit shape and targets ───────────────────────────────────
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
