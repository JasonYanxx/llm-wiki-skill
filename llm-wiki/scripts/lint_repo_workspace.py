#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

from generate_repo_inventory import GENERATED_OUTPUTS, ROOT_ENTRY_DOCS, build_outputs

ALLOWED_ROOT_MARKDOWN = {"README.md", *ROOT_ENTRY_DOCS}
REQUIRED_DIRS = [
    "docs/design-docs",
    "docs/exec-plans/active",
    "docs/exec-plans/completed",
    "docs/product-specs",
    "docs/generated",
    "docs/references",
]
REQUIRED_FILES = [
    "AGENTS.md",
    "PROJECT.md",
    "ARCHITECTURE.md",
    "DESIGN.md",
    "FRONTEND.md",
    "PLANS.md",
    "QUALITY_SCORE.md",
    "RELIABILITY.md",
    "SECURITY.md",
    "docs/index.md",
    "docs/design-docs/index.md",
    "docs/design-docs/core-beliefs.md",
    "docs/design-docs/research-workbench-evolution.md",
    "docs/exec-plans/active/harness-engineering-workspace-rollout.md",
    "docs/exec-plans/completed/research-workbench-upgrade-tasks.md",
    "docs/exec-plans/tech-debt-tracker.md",
    "docs/product-specs/index.md",
    "docs/product-specs/workbench-runtime-contract.md",
    "docs/product-specs/web-viewer.md",
    "docs/product-specs/obsidian-audit-plugin.md",
    "docs/references/index.md",
]
CROSS_REFS = {
    "README.md": ["AGENTS.md", "PROJECT.md", "ARCHITECTURE.md", "PLANS.md", "docs/index.md"],
    "AGENTS.md": ["PROJECT.md", "ARCHITECTURE.md", "PLANS.md", "docs/index.md"],
    "PROJECT.md": ["README.md", "ARCHITECTURE.md", "PLANS.md", "docs/index.md"],
    "PLANS.md": [
        "docs/exec-plans/active/harness-engineering-workspace-rollout.md",
        "docs/exec-plans/completed/research-workbench-upgrade-tasks.md",
        "docs/exec-plans/tech-debt-tracker.md",
    ],
    "docs/index.md": [
        "../README.md",
        "../PROJECT.md",
        "design-docs/index.md",
        "exec-plans/active/harness-engineering-workspace-rollout.md",
        "product-specs/index.md",
        "references/index.md",
        "generated/repo-inventory.md",
        "generated/command-inventory.md",
    ],
    "docs/references/index.md": ["../../llm-wiki/references/harness-guide.md", "../../llm-wiki/references/schema-guide.md"],
}
ENTRY_CONTRACT_SENTENCE = "Canonical repo-aware entry set: `PROJECT.md`, `README.md`, `docs/index.md`."
SECONDARY_DOC_SENTENCE = "`ARCHITECTURE.md` 与 `PLANS.md` 是进入之后的次级文档，不是 primary repo-aware jump targets"
ARCHITECTURE_SECONDARY_SENTENCE = "当前文件是进入之后的次级架构文档，不是 primary repo-aware jump target"
CONTRACT_DOCS = [
    "AGENTS.md",
    "README.md",
    "PROJECT.md",
    "ARCHITECTURE.md",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def lint(root: Path) -> list[str]:
    issues: list[str] = []

    root_markdown = {path.name for path in root.glob("*.md")}
    missing_root = sorted(ALLOWED_ROOT_MARKDOWN - root_markdown)
    extra_root = sorted(root_markdown - ALLOWED_ROOT_MARKDOWN)
    if missing_root:
        issues.append(f"missing root markdown files: {', '.join(missing_root)}")
    if extra_root:
        issues.append(f"unexpected root markdown files: {', '.join(extra_root)}")

    for rel in REQUIRED_DIRS:
        if not (root / rel).is_dir():
            issues.append(f"missing required directory: {rel}")

    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            issues.append(f"missing required file: {rel}")

    for rel, needles in CROSS_REFS.items():
        path = root / rel
        if not path.is_file():
            continue
        text = read_text(path)
        for needle in needles:
            if needle not in text:
                issues.append(f"missing cross-reference in {rel}: {needle}")

    for rel in CONTRACT_DOCS:
        path = root / rel
        if not path.is_file():
            continue
        text = read_text(path)
        if ENTRY_CONTRACT_SENTENCE not in text:
            issues.append(f"missing canonical entry contract in {rel}")
        if rel == "ARCHITECTURE.md" and ARCHITECTURE_SECONDARY_SENTENCE not in text:
            issues.append(f"missing architecture secondary-doc note in {rel}")
        if rel != "ARCHITECTURE.md" and SECONDARY_DOC_SENTENCE not in text:
            issues.append(f"missing secondary-doc note in {rel}")

    expected_outputs = build_outputs(root)
    for rel in GENERATED_OUTPUTS:
        path = root / rel
        if not path.is_file():
            issues.append(f"missing generated artifact: {rel}")
            continue
        actual = read_text(path)
        expected = expected_outputs[rel]
        if actual != expected:
            issues.append(f"stale generated artifact: {rel}")

    return issues


def main(argv: list[str]) -> int:
    root = Path(argv[1] if len(argv) > 1 else ".").resolve()
    issues = lint(root)
    if issues:
        print("repo workspace lint failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("repo workspace lint passed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
