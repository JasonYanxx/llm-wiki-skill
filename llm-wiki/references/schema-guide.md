# WORKBENCH.md Guide

`WORKBENCH.md` is the canonical system protocol for the research workbench.
It replaces the old `CLAUDE.md` schema role.

Every session should start by reading:
- `WORKBENCH.md`
- `indexes/Home.md`

## Required section order

`WORKBENCH.md` should use this stable order:

1. Purpose and Scope
2. Global Conventions
3. Object Protocols
4. Object Matrix
5. Operation Matrix
6. Migration and Compatibility Notes

Inside `Object Protocols`, keep the object chapters in this order:
1. Project
2. Idea
3. Knowledge
4. People
5. Review

## What it should decide

`WORKBENCH.md` is not a scratchpad.
It should lock the stable rules of the system:
- canonical directory layout
- object families and naming rules
- ownership boundaries between AI-maintained and human-owned sections
- operation contracts
- compatibility rules for migration from legacy material

## What it should not do

Avoid turning `WORKBENCH.md` into:
- a live task tracker
- a project dashboard
- a list of every current object
- a long dump of volatile notes

That information belongs in:
- `indexes/Home.md`
- object pages in `compiled/`
- `log/`

## Minimal template

```markdown
# <Workbench Title>

> Stable system protocol for the AI-maintained research workbench.
> Read this together with `indexes/Home.md` at the start of every session.

## 1. Purpose and Scope

What this workbench is for:
- <research support use cases>

What it is not for:
- <non-goals>

## 2. Global Conventions

- Canonical root contract:
  - `WORKBENCH.md`
  - `raw/`
  - `compiled/`
  - `indexes/`
  - `outputs/`
  - `audit/`
  - `log/`
- Preferred link style: natural inline Obsidian links
- All diagrams are mermaid
- All formulas are KaTeX

## 3. Object Protocols

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

## 4. Object Matrix

| Object | Canonical path | Operating style | Human-owned zone |
|---|---|---|---|
| Project | `compiled/projects/<slug>/index.md` | AI-led control page | `My Notes` |
| Idea | `compiled/ideas/<slug>.md` | human-led with AI judgment | `My Notes` |
| Knowledge | `compiled/knowledge/<Title>.md` | AI-led compiled page | optional additive notes |
| People | `compiled/people/<Name>.md` | AI-led compiled page | optional additive notes |
| Review | `compiled/review/Review.md` | AI-led queue | none |

## 5. Operation Matrix

| Operation | Reads | Writes | Notes |
|---|---|---|---|
| `ingest` | source material, `WORKBENCH.md` | `raw/`, `log/` | writes raw only |
| `compile` | raw, repo control docs, compiled, registry | `compiled/`, `indexes/`, registry, `log/` | signal-driven by default |
| `query` | registry, compiled, selective raw/repo fallback | `outputs/queries/`, `log/` | durable results require `promote` |
| `lint` | registry, compiled, indexes, audit, log | report only by default | do not silently rewrite canonical files |
| `audit` | audit entries, targets, supporting sources | target files, `audit/resolved/`, `log/` | never ignore open audits |
| `review` | knowledge pages, registry, selective evidence | `compiled/review/Review.md`, `log/` | maintain digestion queue |
| `promote` | candidates, compiled pages, registry | target compiled object, `log/` | requires confirmation |

## 6. Migration and Compatibility Notes

- `WORKBENCH.md` replaces `CLAUDE.md`
- `compiled/` replaces `wiki/`
- `indexes/` replaces the old single `wiki/index.md`
- legacy material may be read as migration input but is not canonical
```

## Maintenance guidance

- Update `WORKBENCH.md` only when a system rule changes.
- Update `indexes/Home.md` and object pages for day-to-day state.
- Keep object and operation matrices short and stable.
