# Research Workbench Upgrade Tasks

> Execution checklist for evolving `llm-wiki-skill` into an AI-maintained Obsidian research workbench.
> This file is the working task board for the current upgrade pass and should be updated as implementation progresses.

## Status

- Started: 2026-04-11
- Mode: incremental upgrade on top of a dirty worktree
- Canonical target: `WORKBENCH.md + raw/ + compiled/ + indexes/ + outputs/ + audit/ + log/`

## Phase 1. Task Board And Baseline

- [x] Create this root task board and use it as the execution checklist.
- [x] Preserve existing user changes and work incrementally without reverting unrelated modifications.
- [x] Re-run build and smoke-test checks after the upgrade.

## Phase 2. Core Skill And Documentation

- [x] Rewrite `llm-wiki/SKILL.md` around the research workbench model.
- [x] Update supporting references to replace the old `CLAUDE.md + wiki/` canonical model.
- [x] Refresh `README.md` so setup and usage describe the workbench rather than the old topic wiki.

## Phase 3. Scaffold And Canonical Layout

- [x] Redesign `llm-wiki/scripts/scaffold.py` to generate the new directory skeleton.
- [x] Generate starter `WORKBENCH.md`, `indexes/*.md`, `compiled/review/Review.md`, and `compiled/_meta/registry.json`.
- [x] Encode the fixed page templates and ownership rules in scaffolded starter content.

## Phase 4. Lint And Compatibility

- [x] Rebuild `llm-wiki/scripts/lint_wiki.py` for registry-aware workbench linting.
- [x] Keep `audit_review.py` and `audit-shared/` compatible with the anchored audit format.
- [x] Ensure legacy `wiki/` content remains readable as migration input, not canonical truth.

## Phase 5. Web And Plugin Surface

- [x] Make the web viewer default to `indexes/Home.md`.
- [x] Restrict the main tree navigation to `indexes/` and `compiled/`.
- [x] Update graph generation to show only compiled object families.
- [x] Update user-facing web and plugin copy to say "Research Workbench" while keeping technical IDs stable.

## Phase 6. Verification

- [x] Run scaffold smoke tests in a temporary directory.
- [x] Build `audit-shared`.
- [x] Build `plugins/obsidian-audit`.
- [x] Build `web`.
- [x] Perform lint and web behavior smoke checks against a scaffolded workbench.

## Notes

- Keep existing script paths, plugin id, and the web `--wiki` flag for compatibility.
- Repo-aware signals stay limited to explicit repo control docs in v1.
- `My Notes` and Home `Current Focus` remain human-owned zones and should never be treated as compile-owned output.
- Verification highlights:
  - `python3 -m py_compile llm-wiki/scripts/scaffold.py llm-wiki/scripts/lint_wiki.py llm-wiki/scripts/audit_review.py`
  - `npm run build` passed in `audit-shared/`, `plugins/obsidian-audit/`, and `web/`
  - scaffold + lint smoke test passed on a temporary workbench root
  - web smoke test passed for default Home routing, `indexes/` + `compiled/` tree scope, project directory-to-`index.md` routing, compiled-object graph grouping, and audit create/resolve flow
