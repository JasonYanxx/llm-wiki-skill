---
name: llm-wiki
description: >-
  Build and maintain an AI-native Obsidian research workbench: a persistent
  system where an agent ingests raw captures, compiles long-lived research
  objects, maintains indexes and review queues, answers grounded questions,
  audits human feedback, and keeps a machine-readable registry for long-term
  support. Use when: (1) scaffolding a new research workbench, (2) migrating
  high-value material from a legacy vault into a new canonical structure, (3)
  compiling and maintaining project/idea/knowledge/people/review objects, (4)
  answering workbench-grounded questions, (5) running lint passes over the
  registry, compiled layer, indexes, audit files, and logs, and (6) processing
  anchored human feedback filed from Obsidian or the local web viewer. Not for
  general note-taking, pure topic encyclopedias, or repo execution itself.
---

# Research Workbench — AI-Maintained Obsidian Operating Layer

> Experimental skill — iterating from the original `llm-wiki` pattern into a long-term research workbench.

## Core idea

The old pattern compiled raw sources into a topic wiki.
The new pattern keeps the strongest parts of that system:
- raw capture
- compiled knowledge
- anchored audit feedback
- structured operations
- log-based maintenance

But the canonical object model changes. The workbench is no longer centered on `concepts / entities / summaries`. It is centered on long-lived research objects:
- `projects`
- `ideas`
- `knowledge`
- `people`
- `review`

The system is designed for low-friction daily use and batch-oriented AI maintenance.

## Session start

Every session starts by reading:
- `WORKBENCH.md`
- `indexes/Home.md`

These replace the old `CLAUDE.md + wiki/index.md` entrypoint.

## Canonical layout

```text
<workbench-root>/
├── WORKBENCH.md
├── raw/
│   ├── inbox/
│   ├── daily/
│   ├── projects/
│   │   └── <project-slug>/
│   └── external/
│       ├── papers/
│       └── others/
├── compiled/
│   ├── _meta/
│   │   └── registry.json
│   ├── projects/
│   │   └── <project-slug>/
│   │       └── index.md
│   ├── ideas/
│   │   └── <idea-slug>.md
│   ├── knowledge/
│   │   └── <English Canonical Title>.md
│   ├── people/
│   │   └── <source-facing name>.md
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
```

## System principles

### 1. Separate the new workbench from the legacy vault

Do not blindly mutate the old vault into the new system.
The legacy vault is migration input, not canonical truth.

### 2. Keep raw lightweight

`raw/` is for:
- inbox captures
- daily notes
- project-local raw notes
- external material

It is not the main browsing surface.

### 3. Keep project execution in repos

A project page in Obsidian should stay light.
It should record:
- project essence
- current status
- repo execution entry
- related objects
- rolling AI summary
- human notes

It should not become the execution body.

### 4. Preserve human-owned zones

AI maintains most fixed sections, but some zones are human-owned:
- `indexes/Home.md` → `Current Focus`
- project and idea pages → `My Notes`

Compile should not overwrite these sections.

### 5. Use the registry as machine-readable truth

`compiled/_meta/registry.json` is the machine-readable support layer for:
- compile
- lint
- query
- web navigation/graph support
- generated indexes

The registry `meta` block may also carry:
- `repo_roots`
  - shape: `{ "<repo-slug>": "<absolute-or-workbench-relative-local-path>" }`
  - purpose: resolve `repo:<project-slug>/<path-inside-repo>` source refs for lint and other repo-aware maintenance

## Object rules

### Project

- Path: `compiled/projects/<project-slug>/index.md`
- Status: `active | holding | done`
- Fixed structure:
  1. Overview
  2. Status
  3. Execution Entry
  4. Related Objects
  5. AI Compiled
  6. My Notes
  7. Provenance

### Idea

- Path: `compiled/ideas/<idea-slug>.md`
- Status: `spark | exploring | incubating | project-ready`
- Fixed structure:
  1. Proposition
  2. Status
  3. AI Judgment
  4. Related Objects
  5. My Notes
  6. Provenance

### Knowledge

- Path: `compiled/knowledge/<English Canonical Title>.md`
- Fixed structure:
  1. Current Understanding
  2. Why It Matters
  3. Related Projects and Ideas
  4. AI Compiled Body
  5. Provenance

### People

- Path: `compiled/people/<source-facing name>.md`
- Fixed structure:
  1. Current Relationship
  2. Academic Profile
  3. Related Objects
  4. Recent Interactions
  5. Next Follow-up
  6. Provenance

### Review

- Path: `compiled/review/Review.md`
- Fixed structure:
  1. Overview
  2. Noticed
  3. Organized
  4. Retained
  5. Deferred

## Operations

The workbench keeps the original operation skeleton:
- `ingest`
- `compile`
- `query`
- `lint`
- `audit`

And adds:
- `review`
- `promote`

Each operation appends an entry to `log/YYYYMMDD.md`.

### `ingest`

Purpose: normalize incoming material into `raw/`.

Rules:
- Write into `raw/` only.
- Do not create compiled objects directly during ingest.
- Prefer `raw/inbox/` for low-friction capture.
- Keep `raw/daily/` as an independent journal layer.

Typical destinations:
- ad hoc capture → `raw/inbox/`
- daily journal → `raw/daily/`
- project-local raw notes → `raw/projects/<project-slug>/`
- literature PDF/extracted text → `raw/external/papers/`
- other imported material → `raw/external/others/`

### `compile`

Purpose: refresh compiled objects, indexes, and the registry from signals already in the system.

Rules:
- Default to signal-driven partial refresh, not full rewrite.
- Read `WORKBENCH.md`, `compiled/_meta/registry.json`, relevant compiled pages, raw inputs, and explicit repo execution docs when needed.
- Update only objects with new signals.
- Refresh generated indexes and registry together with compiled pages.

### `query`

Purpose: answer questions grounded in the workbench.

Rules:
- Read compiled first.
- Fall back to raw or repo control docs only if compiled is insufficient.
- Save temporary answers to `outputs/queries/<date>-<slug>.md`.
- Promote only after an explicit `promote` decision.

### `review`

Purpose: maintain the global digestion queue.

Rules:
- Read knowledge pages first.
- Use selected raw candidates only when necessary.
- Update `compiled/review/Review.md`.
- Group entries by `noticed / organized / retained / deferred`.

### `promote`

Purpose: turn stable candidates into first-class compiled objects.

Allowed directions:
- raw-derived candidate → idea
- idea → project

Rules:
- Surface candidates first.
- Require user confirmation before creating the target object.

### `lint`

Purpose: health check the workbench.

Focus:
- registry drift
- missing provenance
- disconnected compiled objects
- stale compiled pages whose source refs changed
- audit/log shape

For repo-backed stale checks, `repo:` refs are resolved through `compiled/_meta/registry.json.meta.repo_roots`.

Default behavior:
- report issues
- suggest safe fixes
- do not silently rewrite canonical content

### `audit`

Purpose: process anchored human feedback from `audit/`.

Rules:
- never ignore open audit files
- use anchor windows to locate the target region
- resolve as `accept | partial | reject | defer`
- move resolved items to `audit/resolved/`
- log the resolution

## Web and plugin surfaces

- `plugins/obsidian-audit/` remains audit-focused
- `web/` is a secondary browsing surface for:
  - `indexes/`
  - `compiled/`
  - audit filing
  - compiled-object graph browsing

The web interface is not the primary editing surface.

## Scaffold and scripts

```bash
# Scaffold a new workbench
python3 llm-wiki/scripts/scaffold.py ~/my-workbench "My Research Workbench"

# Run lint
python3 llm-wiki/scripts/lint_wiki.py ~/my-workbench

# Review open audits
python3 llm-wiki/scripts/audit_review.py ~/my-workbench --open
```

## Compatibility policy

- Keep existing script paths and plugin IDs stable.
- Keep the web `--wiki` flag as a compatibility alias for the workbench root.
- Legacy `wiki/` and `CLAUDE.md` may still be read during migration.
- Do not treat legacy structures as canonical truth.

## References

- `references/schema-guide.md` — how to author `WORKBENCH.md`
- `references/article-guide.md` — writing guide for compiled objects
- `references/log-guide.md` — `log/` conventions
- `references/audit-guide.md` — anchored audit workflow
- `references/tooling-tips.md` — Obsidian, web viewer, and migration usage notes
