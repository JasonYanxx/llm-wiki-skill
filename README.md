# llm-wiki-skill

**An agent skill and tooling stack for an AI-maintained Obsidian research workbench.**

This project started from the Karpathy-style `llm-wiki` pattern and is being evolved into a research workbench centered on:
- low-friction raw capture
- compiled research objects
- audit-driven correction
- registry-aware maintenance
- weekly compile/review loops

The canonical model is now:
- `WORKBENCH.md`
- `raw/`
- `compiled/`
- `indexes/`
- `outputs/`
- `audit/`
- `log/`

The registry contract now includes:
- `compiled/_meta/registry.json`
- `meta.repo_roots`: a mapping of `repo_slug -> local repo path`

`repo:` source refs keep the form `repo:<project-slug>/<path-inside-repo>` and are resolved through `meta.repo_roots`.

Legacy `CLAUDE.md` and `wiki/` material may still be used as migration input, but they are no longer canonical truth.

## What is included

- `llm-wiki/` — the skill, references, and Python helper scripts
- `plugins/obsidian-audit/` — Obsidian audit plugin for anchored feedback
- `web/` — local viewer for `indexes/` and `compiled/`, plus audit filing and graph browsing
- `audit-shared/` — shared schema and anchor logic used by the web viewer and the Obsidian plugin

## Install the skill

```bash
cp -r llm-wiki/ ~/.codex/skills/llm-wiki/
```

Then reference `llm-wiki/SKILL.md` in your agent context.

## Quick start

```bash
# 1. Scaffold a new workbench
python3 llm-wiki/scripts/scaffold.py ~/my-workbench "My Research Workbench"

# 2. Capture new material into raw/
#    e.g. raw/inbox/, raw/daily/, raw/external/papers/

# 3. Ask your agent to ingest/compile/review against the new workbench

# 4. Run lint periodically
python3 llm-wiki/scripts/lint_wiki.py ~/my-workbench

# 5. Review open audits
python3 llm-wiki/scripts/audit_review.py ~/my-workbench --open
```

## Repo contents

```text
llm-wiki-skill/
├── llm-wiki/
│   ├── SKILL.md
│   ├── references/
│   │   ├── schema-guide.md
│   │   ├── article-guide.md
│   │   ├── log-guide.md
│   │   ├── audit-guide.md
│   │   └── tooling-tips.md
│   └── scripts/
│       ├── scaffold.py
│       ├── lint_wiki.py
│       └── audit_review.py
├── audit-shared/
├── plugins/obsidian-audit/
└── web/
```

## Web viewer

```bash
cd audit-shared && npm install && npm run build && cd ..
cd web && npm install && npm run build && cd ..
cd web
npm start -- --wiki "/path/to/your/workbench-root" --port 4175
```

Open `http://127.0.0.1:4175`.

The web viewer is intentionally a secondary browsing surface. It focuses on:
- `indexes/`
- `compiled/`
- graph browsing for compiled objects
- anchored audit filing

## Obsidian plugin

```bash
cd audit-shared && npm install && npm run build && cd ..
cd plugins/obsidian-audit
npm install
npm run build
npm run link -- "/path/to/your/Obsidian vault"
```

Then enable **Research Workbench Audit** in Obsidian community plugins.

## Notes

- Existing technical IDs and script paths are kept stable for compatibility.
- The web `--wiki` flag still points at the workbench root.
- Repo-aware project signals in v1 should stay limited to explicit control docs such as `PROJECT.md`, `README.md`, or `docs/index.md`.
- To enable repo-backed stale checks in lint, keep `compiled/_meta/registry.json.meta.repo_roots` updated with local repo roots.
