#!/usr/bin/env python3
"""
scaffold.py — Bootstrap a new Research Workbench directory structure.

Usage:
    python3 scaffold.py <workbench-root> "<Workbench Title>"

Example:
    python3 scaffold.py ~/workbenches/ai-research "AI Research Workbench"

Creates:
    <workbench-root>/
    ├── WORKBENCH.md
    ├── raw/
    │   ├── inbox/
    │   ├── daily/
    │   ├── projects/
    │   └── external/
    │       ├── papers/
    │       └── others/
    ├── compiled/
    │   ├── _meta/
    │   │   └── registry.json
    │   ├── projects/
    │   ├── ideas/
    │   ├── knowledge/
    │   ├── people/
    │   └── review/
    │       └── Review.md
    ├── indexes/
    │   ├── Home.md
    │   ├── Projects.md
    │   ├── Ideas.md
    │   ├── Knowledge.md
    │   ├── People.md
    │   └── Review.md
    ├── outputs/
    │   └── queries/
    ├── audit/
    │   └── resolved/
    └── log/
        └── YYYYMMDD.md
"""

from __future__ import annotations

import json
import os
import shlex
import sys
from datetime import date, datetime
from pathlib import Path


def scaffold(root: str, title: str) -> None:
    today = date.today()
    today_iso = today.isoformat()
    today_compact = today.strftime("%Y%m%d")
    now_hm = datetime.now().strftime("%H:%M")
    workbench_name = title.strip() or "Research Workbench"
    helper_dir = Path(__file__).resolve().parent

    dirs = [
        "raw/inbox",
        "raw/daily",
        "raw/projects",
        "raw/external/papers",
        "raw/external/others",
        "compiled/_meta",
        "compiled/projects",
        "compiled/ideas",
        "compiled/knowledge",
        "compiled/people",
        "compiled/review",
        "indexes",
        "outputs/queries",
        "log",
        "audit",
        "audit/resolved",
    ]

    for rel in dirs:
        os.makedirs(os.path.join(root, rel), exist_ok=True)
    print(f"✓ Created directory tree under {root}/")

    gitkeep_dirs = [
        "raw/inbox",
        "raw/daily",
        "raw/projects",
        "raw/external/papers",
        "raw/external/others",
        "compiled/projects",
        "compiled/ideas",
        "compiled/knowledge",
        "compiled/people",
        "outputs/queries",
        "audit",
        "audit/resolved",
    ]
    for rel in gitkeep_dirs:
        _write(root, os.path.join(rel, ".gitkeep"), "")

    _write(root, "WORKBENCH.md", render_workbench_md(workbench_name))
    print("✓ Created WORKBENCH.md")

    _write(root, "indexes/Home.md", render_home_md(workbench_name))
    _write(root, "indexes/Projects.md", render_projects_index_md())
    _write(root, "indexes/Ideas.md", render_ideas_index_md())
    _write(root, "indexes/Knowledge.md", render_knowledge_index_md())
    _write(root, "indexes/People.md", render_people_index_md())
    _write(root, "indexes/Review.md", render_review_index_md())
    print("✓ Created indexes/*.md")

    _write(root, "compiled/review/Review.md", render_review_md())
    print("✓ Created compiled/review/Review.md")

    registry = {
        "meta": {
            "schema_version": "1.0",
            "generated_at": f"{today_iso}T00:00:00",
            "workbench_title": workbench_name,
            "canonical_schema": "WORKBENCH.md",
            "repo_roots": {},
            "notes": "Registry is the machine-readable source for generated indexes and object-aware tooling.",
        },
        "objects": [
            {
                "id": "review:global",
                "type": "review",
                "path": "compiled/review/Review.md",
                "title": "Review",
                "status": "active",
                "summary": "Global digestion queue for newly noticed and organized knowledge.",
                "updated_at": today_iso,
                "source_count": 0,
                "audit_open_count": 0,
                "source_refs": [],
                "related_object_ids": [],
                "stage": "noticed",
                "next_action": "Ingest sources, promote durable ideas, and refresh this queue during review passes.",
            }
        ],
    }
    _write(root, "compiled/_meta/registry.json", json.dumps(registry, indent=2) + "\n")
    print("✓ Created compiled/_meta/registry.json")

    log_md = f"""# {today_iso}

## [{now_hm}] scaffold | Initialized {workbench_name}
- Created research workbench directory tree (`raw/`, `compiled/`, `indexes/`, `outputs/`, `audit/`, `log/`)
- Created `WORKBENCH.md` system protocol
- Created starter index pages and the global review page
- Seeded `compiled/_meta/registry.json`
"""
    _write(root, f"log/{today_compact}.md", log_md)
    print(f"✓ Created log/{today_compact}.md")

    print(
        f"""
✅ Research Workbench scaffolded at: {root}/

Next steps:
  1. Fill in WORKBENCH.md — scope, conventions, object policies, migration notes
  2. Capture new material into raw/inbox/ or raw/external/
  3. Promote stable ideas and projects only after confirmation
  4. Run compile/review passes in batches, not continuously
  5. Run lint periodically:  {render_helper_command(helper_dir / "lint_wiki.py", root)}
  6. Review audits:         {render_helper_command(helper_dir / "audit_review.py", root, "--open")}
"""
    )


def render_workbench_md(title: str) -> str:
    return f"""# {title}

> Stable system protocol for the AI-maintained research workbench.
> Read this together with `indexes/Home.md` at the start of every session.

## 1. Purpose and Scope

This workbench is the canonical home for AI-maintained long-term research support.
It is optimized for:
- low-friction capture into `raw/`
- AI-maintained compiled objects in `compiled/`
- human correction through `audit/`
- weekly or batch-oriented `compile` and `review` loops

It is not optimized for:
- turning Obsidian into the execution body of a software project
- mirroring a legacy vault one-to-one
- automatic promotion of every captured thought into a first-class object

## 2. Global Conventions

- Canonical root contract:
  - `WORKBENCH.md`
  - `raw/`
  - `compiled/`
  - `indexes/`
  - `outputs/`
  - `audit/`
  - `log/`
- `raw/` is evidence and capture, not the main user-facing layer.
- `compiled/` holds AI-maintained research objects.
- `indexes/` holds navigation and control pages.
- `outputs/` holds temporary query artifacts and non-canonical generated material.
- `log/YYYYMMDD.md` records operation history.
- All diagrams are mermaid. All formulas are KaTeX.
- The preferred linking style is natural inline Obsidian links with readable aliases when helpful.

## 3. Object Protocols

### Project

- Path pattern: `compiled/projects/<project-slug>/index.md`
- Status set: `active`, `holding`, `done`
- Purpose: light project control page, not the execution body
- Repo boundary: detailed execution should live in the corresponding repo
- Fixed structure:
  1. Overview
  2. Status
  3. Execution Entry
  4. Related Objects
  5. AI Compiled
  6. My Notes
  7. Provenance
- Ownership:
  - `My Notes` is human-owned
  - all other fixed sections are AI-maintained unless explicitly marked otherwise

### Idea

- Path pattern: `compiled/ideas/<idea-slug>.md`
- Status set: `spark`, `exploring`, `incubating`, `project-ready`
- Purpose: human-led idea page that may mature into a project
- Fixed structure:
  1. Proposition
  2. Status
  3. AI Judgment
  4. Related Objects
  5. My Notes
  6. Provenance
- Ownership:
  - `My Notes` is human-owned
  - `AI Judgment` is AI-maintained

### Knowledge

- Path pattern: `compiled/knowledge/<English Canonical Title>.md`
- Purpose: stable personal research understanding, not a neutral encyclopedia entry
- Fixed structure:
  1. Current Understanding
  2. Why It Matters
  3. Related Projects and Ideas
  4. AI Compiled Body
  5. Provenance
- Knowledge pages should carry their own digestion state in frontmatter or visible content.

### People

- Path pattern: `compiled/people/<source-facing name>.md`
- Purpose: AI-maintained relationship and academic context memory
- Fixed structure:
  1. Current Relationship
  2. Academic Profile
  3. Related Objects
  4. Recent Interactions
  5. Next Follow-up
  6. Provenance

### Review

- Path pattern: `compiled/review/Review.md`
- Purpose: global digestion queue rather than a long-form knowledge article
- Fixed structure:
  1. Overview
  2. Noticed
  3. Organized
  4. Retained
  5. Deferred

## 4. Object Matrix

| Object | Canonical path | Operating style | Human-owned zone |
|---|---|---|---|
| Project | `compiled/projects/<slug>/index.md` | AI-led control page | `My Notes` |
| Idea | `compiled/ideas/<slug>.md` | human-led with AI judgment | `My Notes` |
| Knowledge | `compiled/knowledge/<Title>.md` | AI-led compiled page | optional additive notes only |
| People | `compiled/people/<Name>.md` | AI-led compiled page | optional additive notes only |
| Review | `compiled/review/Review.md` | AI-led queue | none by default |

## 5. Operation Matrix

| Operation | Reads | Writes | Notes |
|---|---|---|---|
| `ingest` | source material, `WORKBENCH.md` | `raw/`, `log/` | ingest writes raw only |
| `compile` | raw, repo control docs, compiled, registry | `compiled/`, `indexes/`, registry, `log/` | default to signal-driven partial refresh |
| `query` | `WORKBENCH.md`, registry, compiled, selective raw/repo fallback | `outputs/queries/`, `log/` | durable results require `promote` |
| `lint` | registry, compiled, indexes, audit, log | report only by default | do not silently rewrite canonical content |
| `audit` | open audit files, target pages, supporting sources | target files, `audit/resolved/`, `log/` | never ignore open audits |
| `review` | knowledge pages, registry, selective raw evidence | `compiled/review/Review.md`, `log/` | organize digestion queue |
| `promote` | raw candidates, compiled pages, registry | target compiled object, `log/` | requires user confirmation |

## 6. Migration and Compatibility Notes

- `WORKBENCH.md` replaces `CLAUDE.md` as the canonical schema file.
- `compiled/` replaces `wiki/` as the canonical compiled layer.
- `indexes/` replaces the old single `wiki/index.md` navigation role.
- Legacy `CLAUDE.md` and `wiki/` content may still be read as migration input, but they are not canonical truth.
- This workbench should normally live in a new vault instead of mutating a legacy vault in place.
- Repo-aware project signals in v1 should stay limited to explicit execution-entry docs such as `PROJECT.md`, `README.md`, or `docs/index.md`.
"""


def render_home_md(title: str) -> str:
    return f"""# Home

> Default landing page for {title}.
> This page is hybrid: `Current Focus` is human-owned, while the remaining sections are AI-maintained summaries generated from the registry and compiled layer.

## Current Focus

<!-- Human-owned: compile must not rewrite this section. -->
- Primary active project:
- Current blocker:
- Primary repo jump point:
- Immediate next push:

## Inbox

- New raw captures to review: 0
- Default capture path: `raw/inbox/`
- Daily journal remains independent at `raw/daily/`

## Projects

- See [[indexes/Projects|Projects index]].
- No projects promoted yet.

## Ideas

- See [[indexes/Ideas|Ideas index]].
- No ideas promoted yet.

## Review

- See [[compiled/review/Review|global Review queue]] and [[indexes/Review|Review index]].

## People

- See [[indexes/People|People index]].
- No tracked people yet.

## Recent Changes

- Workbench initialized.
- Registry seeded at `compiled/_meta/registry.json`.
"""


def render_projects_index_md() -> str:
    return """# Projects

> Generated navigation page for project objects. Group by project status.

## Active

*(none yet)*

## Holding

*(none yet)*

## Done

*(none yet)*
"""


def render_ideas_index_md() -> str:
    return """# Ideas

> Generated navigation page for idea objects. Group by maturity.

## Spark

*(none yet)*

## Exploring

*(none yet)*

## Incubating

*(none yet)*

## Project-ready

*(none yet)*
"""


def render_knowledge_index_md() -> str:
    return """# Knowledge

> Generated navigation page for knowledge objects. Group by thematic domain when the collection grows.

## Core Domains

*(none yet)*

## Emerging Domains

*(none yet)*
"""


def render_people_index_md() -> str:
    return """# People

> Generated navigation page for people objects. Group by relationship role.

## Core Collaborators

*(none yet)*

## Active Contacts

*(none yet)*

## Watchlist

*(none yet)*
"""


def render_review_index_md() -> str:
    return """# Review

> Navigation and control page for the global digestion queue.

## Main Queue

- [[compiled/review/Review|Open global Review queue]]

## Notes

- Group entries by digestion stage: noticed, organized, retained, deferred.
- Review is a control surface, not a long-form article family.
"""


def render_review_md() -> str:
    today = date.today().isoformat()
    return f"""---
title: Review
type: review
status: active
updated: {today}
source_refs: []
related_object_ids: []
stage: noticed
next_action: Refresh this page after new ingest or compile passes.
---

# Review

## Overview

This page is the global knowledge digestion queue for the workbench.
It should answer:
- what new knowledge entered the system
- what remains unlinked
- what should be applied
- what can be deferred

## Noticed

*(none yet)*

## Organized

*(none yet)*

## Retained

*(none yet)*

## Deferred

*(none yet)*
"""


def _write(root: str, rel_path: str, content: str) -> None:
    full_path = os.path.join(root, rel_path)
    os.makedirs(os.path.dirname(full_path) or ".", exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as handle:
        handle.write(content)


def render_helper_command(script_path: Path, root: str, *extra_args: str) -> str:
    parts = [shlex.quote(sys.executable), shlex.quote(str(script_path)), shlex.quote(root)]
    parts.extend(shlex.quote(arg) for arg in extra_args)
    return " ".join(parts)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    scaffold(sys.argv[1], sys.argv[2])
