# Tooling Tips

Practical setup notes for the research workbench stack.

## Obsidian

Recommended defaults:

1. Attachment folder: `raw/assets/`
2. Default new note location: keep manual notes in the area that matches intent
3. Use `raw/inbox/` for low-friction capture
4. Keep `raw/daily/` as an independent daily journal layer

## Suggested plugins

- `plugins/obsidian-audit/` from this repo — anchored audit filing
- Obsidian Web Clipper — save external material into `raw/`
- Dataview (optional) — inspect frontmatter across compiled objects

## Audit plugin workflow

1. Build the plugin:
   ```bash
   cd plugins/obsidian-audit
   npm install
   npm run build
   ```
2. Link it into a vault:
   ```bash
   npm run link -- "/path/to/your/vault"
   ```
3. In Obsidian, enable the community plugin.
4. Configure:
   - Workbench root
   - Audit directory
   - Author

The plugin stays audit-focused. It is not yet a full workbench operations plugin.

## Web viewer

The local web viewer is a secondary browsing surface:

```bash
cd web
npm install
npm run build
npm start -- --wiki "/path/to/your/workbench-root" --port 4175
```

What it is for:
- browse `indexes/` and `compiled/`
- inspect the compiled object graph
- file anchored audit feedback

What it is not for:
- being the primary editing environment
- foregrounding `raw/` as the main navigation surface

## Recommended capture flow

- quick thought, clipped note, or ad hoc observation -> `raw/inbox/`
- daily journal -> `raw/daily/`
- project-local raw note -> `raw/projects/<project-slug>/`
- imported literature -> `raw/external/papers/`
- other outside material -> `raw/external/others/`

## Repo-aware project usage

For v1, keep repo-aware signals intentionally shallow:
- prefer explicit control docs such as `PROJECT.md`, `README.md`, `docs/index.md`
- do not rely on deep repo crawling
- do not treat Obsidian as the execution body

## Graph expectations

The primary graph should show compiled objects only:
- projects
- ideas
- knowledge
- people
- review

Do not expect raw notes or index pages to be first-class graph nodes by default.
