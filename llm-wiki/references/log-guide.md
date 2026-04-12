# Log Guide — `log/`

The workbench log is one file per day: `log/YYYYMMDD.md`.
It records operations, not full content.

## File shape

- Filename: `log/YYYYMMDD.md`
- H1: `# YYYY-MM-DD`
- Each operation entry starts with:
  - `## [HH:MM] <op> | <one-line description>`

Example:

```markdown
# 2026-04-11

## [09:15] ingest | imported trust-calibration paper
- Source: raw/external/papers/trust-calibration.md
- Result: raw material normalized for later compile

## [11:20] compile | refreshed calibration knowledge object
- Updated: compiled/knowledge/Calibration.md
- Updated: indexes/Knowledge.md
- Updated: compiled/_meta/registry.json

## [14:05] review | regrouped digestion queue
- Updated: compiled/review/Review.md
- Moved 2 items from noticed to organized

## [16:40] audit | resolved 20260411-164001-a1b2
- Target: compiled/knowledge/Calibration.md
- Change: corrected the trust definition and clarified provenance
```

## Allowed operation labels

- `scaffold`
- `ingest`
- `compile`
- `query`
- `promote`
- `review`
- `lint`
- `audit`

## Logging rules

- Keep entries short and scannable.
- Mention touched canonical files when helpful.
- Log what changed, not the entire rationale.
- Put durable system rules in `WORKBENCH.md`, not here.

## Good examples

- `## [10:00] compile | refreshed two active projects from new repo signals`
- `## [11:35] promote | trust-metric idea -> project candidate`
- `## [15:05] lint | found 3 registry/index drift issues`

## Avoid

- copying large content blocks into the log
- writing private notes or secrets
- treating the log as a general journal

Use `raw/daily/` for personal journaling instead.
