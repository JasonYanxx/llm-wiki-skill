# Audit Guide

`audit/` is the human correction surface for the research workbench.
It keeps feedback durable, anchored, and tool-readable.

## Directory layout

```text
<workbench-root>/audit/
├── 20260411-103000-provenance-gap.md
├── 20260411-110500-status-wording.md
└── resolved/
    └── 20260410-160100-old-definition.md
```

- `audit/*.md` -> open feedback
- `audit/resolved/*.md` -> processed feedback with a resolution note

## File contract

Each file has:
- YAML frontmatter
- `# Comment`
- `# Resolution`

The anchored fields stay compatible with the shared `audit-shared/` library:
- `target_lines`
- `anchor_before`
- `anchor_text`
- `anchor_after`

## Required frontmatter fields

- `id`
- `target`
- `target_lines`
- `anchor_before`
- `anchor_text`
- `anchor_after`
- `severity`
- `author`
- `source`
- `created`
- `status`

## Severity meaning

- `info` -> worth noting
- `suggest` -> consider changing
- `warn` -> something looks off
- `error` -> something is wrong

Process `error` and `warn` first.

## Target policy

Targets are paths relative to the workbench root.
Typical targets include:
- `compiled/projects/<slug>/index.md`
- `compiled/ideas/<slug>.md`
- `compiled/knowledge/<Title>.md`
- `compiled/people/<Name>.md`
- `compiled/review/Review.md`
- `indexes/Home.md`

Raw files may also be audited, but compiled pages are the primary audit surface.

## Processing workflow

1. Run:
   ```bash
   python3 scripts/audit_review.py <workbench-root> --open
   ```
2. For each open audit:
   - locate the target region using the anchor window
   - decide `accept | partial | reject | defer`
   - apply the smallest edit that resolves the issue
   - append the resolution note
   - move the file to `audit/resolved/` if resolved
   - log the action in `log/YYYYMMDD.md`

## Defer policy

If feedback exposes an unresolved research question:
- keep the audit open if needed
- record the unresolved issue in the relevant compiled page or in `WORKBENCH.md` if it is a system-level rule question
- do not silently drop the feedback

## Resolution note format

```markdown
# Resolution

2026-04-11 · accepted.
Clarified the project status wording and added explicit provenance to the repo entry.
Updated: compiled/projects/example/index.md.
```

## Tooling

- `audit-shared/` defines the schema and anchor behavior
- `scripts/audit_review.py` groups audits
- `scripts/lint_wiki.py` validates audit shape and target existence
- `plugins/obsidian-audit/` files audits from Obsidian
- `web/` files audits from the browser
