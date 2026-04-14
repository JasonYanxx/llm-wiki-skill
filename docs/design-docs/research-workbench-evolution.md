# Research Workbench Evolution

> Working design memo for evolving `llm-wiki-skill` from a topic-oriented LLM wiki into an AI-native long-term research workbench.
> This document is the source of truth for product direction, object model, and system boundaries.
> Status: active discussion draft

## 1. Product Direction

The future system is not just a wiki knowledge base.

It should evolve into an AI-native research workbench with:
- raw input layers
- compiled research objects
- audit-driven correction
- repo-aware project control
- weekly compile/review loops

The goal is to support long-term research work with minimal daily friction, while allowing strong maintenance through AI-assisted compilation.

## 2. Core Positioning

### 2.1 What to preserve from `llm-wiki-skill`

Keep the underlying ideas of:
- `raw`
- `log`
- `audit`
- fixed operation loop
- human-in-the-loop correction

These are the strongest parts of the existing system.

### 2.2 What must change

The current project is built around a topic wiki model:
- `wiki/concepts`
- `wiki/entities`
- `wiki/summaries`

This is too narrow for the target system.

The future system should be modeled around research workbench objects instead of wiki article categories.

### 2.3 New positioning

This project should evolve from:
- an LLM-maintained topic wiki

into:
- an AI-native research operating system / research workbench

## 3. New System Boundary

### 3.1 Separate new vault

The future workbench should live in a separate new vault/system instead of directly mutating the current legacy vault.

### 3.2 Legacy vault relation

The current vault is a transition source system:
- early stage: source of active and high-value material
- middle stage: progressively ingested and rewritten
- later stage: temporary transition area
- long term: no longer the main workbench

### 3.3 Migration style

Migration should:
- start from high-activity areas
- progressively expand
- rewrite important pages into new object types
- avoid mirroring old structure blindly

## 4. Core Object Model

### 4.1 Raw objects

Raw should be minimal and readable.

Main raw categories:
- inbox captures
- daily notes
- raw project notes
- external inputs

Raw should remain mostly hidden from the user-facing main workbench.
It exists primarily as:
- evidence
- compilation input
- traceability layer

Primary raw capture should enter through `raw/inbox/`.
`raw/daily/` should remain an independent journal layer and preserve the richer legacy daily-note role rather than becoming a thin mirror of inbox items.

### 4.2 Compiled objects

Compiled should replace the old `wiki/` idea.

Core compiled object families:
- `projects`
- `ideas`
- `knowledge`
- `people`
- `review`

`deliverable` should not remain a long-term top-level compiled object.
Its long-term home should be the GitHub repo under a project context.

### 4.3 Repo boundary

A `project` page in Obsidian should be very light.

Project page should keep:
- project essence
- main entry points
- current next step

Project page should not become the execution body.

Execution body should live in repo:
- code
- docs
- deliverables
- implementation material
- detailed working content

Project raw notes should be pushed into repo as early as possible.

A project should normally correspond to exactly one repo.
When an idea becomes a project, the system should suggest creating a repo.

### 4.4 Top-level directory skeleton

The future system should use the following top-level structure:

- `WORKBENCH.md`
- `raw/`
- `compiled/`
- `indexes/`
- `outputs/`
- `audit/`
- `log/`

Rationale:
- `WORKBENCH.md` stores the global system protocol
- `raw/` stores original inputs
- `compiled/` stores AI-maintained research objects
- `indexes/` stores homepage and object-level navigation pages
- `outputs/` stores temporary and non-canonical generated artifacts
- `audit/` stores human correction and review feedback
- `log/` stores operation history

### 4.5 Index placement

Homepage and major object indexes should live under `indexes/`, not under `compiled/`.

This keeps navigation pages separate from compiled object bodies.

### 4.6 Review placement

`review` should remain a first-class compiled object family.

It should live under:
- `compiled/review/`

Even though review also functions as a global queue/control surface, it should still be modeled as a compiled object family rather than being reduced to a pure index page.

### 4.7 Raw directory skeleton

`raw/` should start with four main subdirectories:
- `raw/inbox/`
- `raw/daily/`
- `raw/projects/`
- `raw/external/`

Rationale:
- `inbox/` is the default first landing zone for new raw captures
- `daily/` remains an independent journal layer with legacy-style daily usage
- `projects/` stores raw project notes before or alongside repo integration
- `external/` stores imported outside material

`raw/inbox/` should stay flat at first.
Default unit:
- one capture per file

The system should not require a strict daily-to-inbox synchronization pass.
Daily notes may remain manually maintained and semantically independent.

### 4.8 Raw project layout

`raw/projects/` should be organized as one directory per project.

Pattern:
- `raw/projects/<project-slug>/`

This keeps project-local raw signals grouped for compile and traceability.

### 4.9 Raw external layout

`raw/external/` should begin with a minimal subdivision:
- `raw/external/papers/`
- `raw/external/others/`

This is intentionally lighter than a full external taxonomy, while still separating paper inputs from all other imported material.

### 4.10 Compiled directory skeleton

`compiled/` should initially contain:
- `compiled/_meta/`
- `compiled/projects/`
- `compiled/ideas/`
- `compiled/knowledge/`
- `compiled/people/`
- `compiled/review/`

This directly mirrors the confirmed core object families of the workbench.
`compiled/_meta/` should hold hidden machine-readable support files such as the global object registry.

### 4.11 Knowledge directory policy

`compiled/knowledge/` should start flat.

Do not over-design theme folders from day one.
Only split by topic later if scale and usage clearly demand it.

### 4.12 People directory policy

`compiled/people/` should also start flat.

Each person should begin as one page under `compiled/people/`.
Do not pre-split by role, activity level, or organization.

### 4.13 Project directory policy

`compiled/projects/` should use one directory per project.

Pattern:
- `compiled/projects/<project-slug>/`

This leaves room for a light project homepage plus possible future auxiliary compiled pages for the same project.

### 4.14 Idea directory policy

`compiled/ideas/` should use one page per idea.

Pattern:
- `compiled/ideas/<idea-slug>.md`

Do not create idea directories by default.
The idea model should remain lightweight.

### 4.15 Review directory policy

`compiled/review/` should center on one main global review page.

Pattern:
- one main Review page
- optional small number of supporting pages later if needed

Review should remain a control surface first, not a large content family.

### 4.16 Index directory skeleton

`indexes/` should initially contain:
- `indexes/Home.md`
- `indexes/Projects.md`
- `indexes/Ideas.md`
- `indexes/Knowledge.md`
- `indexes/People.md`
- `indexes/Review.md`

These pages are navigation and control pages, not compiled object bodies.

### 4.17 Home page naming

The main homepage should be:
- `indexes/Home.md`

This is the primary entry point of the system.

### 4.18 Object index style

Each object family should have its own dedicated index page.

Do not merge all object indexes into one giant navigation page.

### 4.19 Project naming policy

Project directories under `compiled/projects/` should use stable kebab-case slugs.

Pattern:
- `compiled/projects/<project-slug>/`

### 4.20 Idea naming policy

Idea pages under `compiled/ideas/` should use short kebab-case slugs.

Pattern:
- `compiled/ideas/<idea-slug>.md`

### 4.21 People naming policy

People pages under `compiled/people/` should preserve the original source-facing naming style when possible.

Do not force a uniform slug-only naming policy for people pages if it harms continuity with existing names and external identity.

### 4.22 Knowledge naming policy

Knowledge pages under `compiled/knowledge/` should use English canonical titles.

This supports:
- stable linking
- readable natural inline links
- continuity across research contexts

### 4.23 Review naming policy

The main global review page should be:
- `compiled/review/Review.md`

### 4.24 Global schema placement

The system should keep one global schema file at the repository root.

However, the schema filename should no longer be tied to a specific agent name such as `CLAUDE.md`.

A neutral system-level schema name is required.

### 4.25 Outputs directory

The top-level directory skeleton should also retain:
- `outputs/`

Rationale:
- temporary query outputs
- intermediate generated material
- non-canonical artifacts that should not pollute `compiled/`

### 4.26 Query output placement

Temporary query outputs should live under:
- `outputs/queries/`

Durable query results can later be promoted into compiled objects.

### 4.27 Global schema filename

The root-level system schema file should be:
- `WORKBENCH.md`

This replaces agent-specific names such as `CLAUDE.md` and makes the system protocol agent-neutral.

`WORKBENCH.md` should be treated as a stable system constitution, not a live active-project list.
Its preferred internal style is:
- short rule sections
- key decision tables / matrices

At minimum it should contain:
- an object matrix
- an operation matrix

The canonical section order of `WORKBENCH.md` should be:
1. Purpose and Scope
2. Global Conventions
3. Object Protocols
4. Object Matrix
5. Operation Matrix
6. Migration and Compatibility Notes

Inside `Object Protocols`, the object chapters should appear in this order:
1. Project
2. Idea
3. Knowledge
4. People
5. Review

This means the preferred high-level shape is:
- total principles first
- global conventions second
- object families third
- system matrices after object rules
- migration and compatibility notes at the end

### 4.28 Current canonical directory skeleton

The current canonical directory skeleton is:

```text
/
  WORKBENCH.md
  raw/
    inbox/
    daily/
    projects/
      <project-slug>/
    external/
      papers/
      others/
  compiled/
    _meta/
    projects/
      <project-slug>/
    ideas/
      <idea-slug>.md
    knowledge/
      <English Canonical Title>.md
    people/
      <source-facing name>.md
    review/
      Review.md
      ...
  indexes/
    Home.md
    Projects.md
    Ideas.md
    Knowledge.md
    People.md
    Review.md
  outputs/
    queries/
  audit/
    resolved/
  log/
```

### 4.29 Project internal minimum layout

Each project directory should begin with only:
- `compiled/projects/<project-slug>/index.md`

Do not pre-create multiple standard project subpages from day one.

### 4.30 Project index page role

`index.md` is the light project control page.

It should not become the execution body.
Its role is to:
- state project essence
- show current status
- point to the execution entry in repo
- expose lightweight related objects
- hold a rolling AI summary
- leave room for human notes

### 4.31 Project status model

Projects should use the lightweight status set:
- `active`
- `holding`
- `done`

Project status should exist in:
- frontmatter
- visible page content

### 4.32 Project execution entry

The primary execution entry on a project page should point to the repo-level project control document, such as:
- `PROJECT.md`
- `README.md`
- `docs/index.md`

The project page should not itself hold detailed task execution.

### 4.33 Project index fixed structure

`compiled/projects/<project-slug>/index.md` should use the following fixed structure:

1. Overview
2. Status
3. Execution Entry
4. Related Objects
5. AI Compiled
6. My Notes
7. Provenance

### 4.34 Project AI/Human zones

Project pages should use one-file split zones:
- AI zone in the same page
- human notes in the same page

Do not split project pages into separate `ai.md` and `human.md` files.

### 4.35 Project AI zone

The AI zone should be a rolling project summary rather than a weekly-only note or a pure link list.

### 4.36 Project human zone

The human zone should remain a free-form note area.

### 4.37 Project provenance style

Project provenance should be embedded naturally into the AI-generated prose when possible, using Obsidian-style inline links.

Do not force provenance to exist only as a detached citation block.

### 4.38 Project auxiliary pages policy

Project directories should not have mandatory auxiliary pages by default.

Auxiliary pages may be added later only when clearly needed.

## 5. Idea Model

### 5.1 Role of Idea

Idea is not an early form of knowledge.

Idea is an independent long-lived object.
It may mature over time.
It only upgrades toward `project`, not toward `knowledge`.

### 5.2 Idea granularity

One idea page should correspond to one concrete idea.

Not:
- one giant idea garden page
- one topic collecting many unrelated ideas

### 5.3 Idea generation

Idea pages should not be created blindly.

The system should first surface idea candidates based on:
- repeated appearance
- cross-page association
- recurring mention across daily/project/knowledge contexts

Then the user confirms promotion into a formal idea page.

### 5.4 Idea states

Idea should use four states:
- `spark`
- `exploring`
- `incubating`
- `project-ready`

### 5.5 Idea content shape

Idea is closer to an idea pool than a rigid research spec.
It should preserve ambiguity and evolution, not force premature formalization.

### 5.6 Idea page operating style

Idea pages should be human-led rather than AI-led.

Default pattern:
- one idea page per file
- AI and human content share the same page
- frontmatter stores machine-readable state
- page body visibly exposes the current idea state

### 5.7 Idea top anchor

Each idea page should begin with a single problem/proposition sentence.

This keeps the idea page anchored around one clear research question, claim, or hypothesis instead of drifting into a loose dump.

### 5.8 Idea AI block role

On a human-led idea page, the AI should maintain a compact judgment block.

Its job is to summarize:
- what the idea currently is
- what it is connected to
- what is still unclear
- how close it is to `project-ready`

### 5.9 Idea promotion checklist policy

Idea pages should not include a mandatory hard-coded project promotion checklist by default.

Promotion judgment should remain flexible and rely on:
- idea state
- AI judgment block
- user decision

### 5.10 Idea fixed page structure

`compiled/ideas/<idea-slug>.md` should use the following fixed structure:

1. Proposition
2. Status
3. AI Judgment
4. Related Objects
5. My Notes
6. Provenance

This page should remain human-led.
The fixed structure exists to keep idea pages comparable and machine-maintainable, not to force them into mini project proposals.

## 6. Knowledge Model

### 6.1 Role of Knowledge

Knowledge should be a stable personal research knowledge object.

It should come from:
- external input
- literature
- meetings
- workshop/conference input
- generalized understanding distilled from project learning

It should not be a direct upgrade target of ideas.

### 6.2 Knowledge page style

Knowledge pages should be:
- personalized for the user's research context
- not neutral encyclopedia pages
- not just method flashcards

They should explain concepts in a way that matters for the user's own research.

### 6.3 When to create a knowledge page

A concept deserves a knowledge page only when it has sustained relevance to the user's research.

Not every new concept should become a page.

### 6.4 Evidence style

Knowledge must remain traceable.

A knowledge page should be able to point back to:
- literature notes
- raw notes
- project context

Traceability should be visible in the page itself.

### 6.5 Link writing style

The preferred link style is natural inline Obsidian linking.

Example pattern:
- `[[Canonical Page|natural reading phrase]]`

Preferred writing should feel like natural prose instead of mechanical citation.

Canonical title should stay stable.
Display text can vary naturally in context.

### 6.6 Title policy

Page titles should tend toward English canonical titles.
The system should avoid relying heavily on a global alias system.
Display-level variation should happen mainly inline in prose.

### 6.7 Knowledge page operating style

Knowledge pages should be AI-led compiled pages.

Human notes may still coexist, but the page should primarily behave as:
- a maintained knowledge asset
- a reusable research understanding page
- a compiled long-term object

### 6.8 Knowledge top anchor

The top anchor of a knowledge page should be:
- the user's current understanding

This is preferable to a neutral encyclopedia-style definition because the workbench is intended to support the user's own research judgment.

### 6.9 Knowledge split trigger

Knowledge pages should remain one page by default and split only when the page becomes too large or too unwieldy.

Do not split only because there are multiple sources.
Do not split only because multiple possible subthemes exist.

### 6.10 Knowledge review-state storage

Each knowledge page should carry its own current digestion state.

`Review` should read and organize those states.
It should not become the sole owner of knowledge progression state.

### 6.11 Knowledge fixed page structure

`compiled/knowledge/<title>.md` should use the following fixed structure:

1. Current Understanding
2. Why It Matters
3. Related Projects and Ideas
4. AI Compiled Body
5. Provenance

Knowledge pages are AI-led pages.
Human additions may exist, but the canonical top-level structure should remain stable.

## 7. Review Model

### 7.1 Role of Review

Review is not a long-term content page.
It is a global knowledge digestion queue.

Its job is to answer:
- what new knowledge entered the system
- what remains unlinked
- what remains unapplied
- what should be deferred

### 7.2 Review scope

There should be one global main Review page/queue.

Not:
- one review page per topic
- one review page per project

### 7.3 Review sources

Review items should come primarily from:
- knowledge pages
- supplemented by selected raw candidates

### 7.4 Review actions

For each review item, the primary actions should be:
- link
- apply
- defer

The system should provide explicit AI recommendations for these actions.

Items should remain in Review until they are:
- processed
- deferred

### 7.5 Review state complexity

Knowledge digestion should use a lightweight three-stage model:
- `noticed`
- `organized`
- `retained`

### 7.6 Review grouping

The main Review page should be grouped primarily by digestion stage.

The first-class grouping axis should therefore be:
- `noticed`
- `organized`
- `retained`

### 7.7 Review display unit

The main unit in Review should be:
- one knowledge object per entry

Review should not primarily show:
- vague theme clusters
- generic action buckets without object identity

### 7.8 Review action surface

Each Review entry should visibly answer:
- what is the next best move

Examples:
- connect it
- apply it
- revisit it later
- leave it retained

### 7.9 Review fixed page structure

`compiled/review/Review.md` should use the following fixed structure:

1. Overview
2. Noticed
3. Organized
4. Retained
5. Deferred

Review remains a global queue and aggregation page, not a conventional long-form knowledge page.

## 8. People Model

### 8.1 Role of People

People is a full compiled object family, not a peripheral note collection.

All people should be automatically maintained.

### 8.2 People page content

People pages should be strong in both:
- relationship / interaction tracking
- academic profile / external image

A people page should ideally integrate:
- internal interaction records
- linked projects
- linked ideas
- linked knowledge
- public academic information

### 8.3 People sources

People pages should compile from:
- internal records
- public external information

### 8.4 Update cadence

People should update through:
- event-triggered local refresh
- weekly summary refresh

### 8.5 People page operating style

People pages should be AI-led compiled pages.

This is the best fit for:
- sustained relationship tracking
- academic profile maintenance
- follow-up memory
- project / idea / knowledge association

### 8.6 People top anchor

The top anchor of a people page should be:
- the current relationship state

This should answer things like:
- who this person currently is in the user's world
- why they matter now
- in what context they are relevant

### 8.7 People follow-up visibility

People pages should visibly expose follow-up information in-page.

At minimum this should include:
- recent interaction context
- next follow-up

### 8.8 People fixed page structure

`compiled/people/<name>.md` should use the following fixed structure:

1. Current Relationship
2. Academic Profile
3. Related Objects
4. Recent Interactions
5. Next Follow-up
6. Provenance

People pages are AI-led pages.
The fixed structure should support both relationship memory and academic/work context.

## 9. Homepage and Interaction Model

### 9.1 Homepage style

Homepage should be a mixed control console.

Primary homepage order:
- Projects
- Ideas
- Review
- People
- Recent Changes

People remains a secondary core object relative to the first three sections, but it should still be visible on the homepage.

### 9.2 Interface split

Use dual interface:
- Obsidian
- Web

Preferred split:
- Obsidian: primary editing and note environment
- Web: browsing compiled results + audit + object-level navigation

### 9.3 Web role

The web interface should mainly support:
- compiled-page browsing
- audit interaction
- object dashboard + left tree navigation
- object relation graph

The web interface should be treated as a secondary browser, not the primary product frontstage.

Therefore the design should not assume:
- web-first search workflows
- card-first product discovery
- richer product logic than needed for browsing, graph, and audit

Web light actions may be considered later, but are not part of the canonical core system contract.

### 9.4 Obsidian plugin role

The Obsidian plugin should remain audit-focused.
It should not yet become a full workbench operations plugin.

### 9.5 Default landing page

The default front-stage landing page should be:
- `indexes/Home.md`

This should be the default entry in both:
- Obsidian
- Web

### 9.6 Home page maintenance mode

`indexes/Home.md` should be a hybrid page.

It should combine:
- a small manually maintained section
- larger AI-maintained compiled sections

### 9.7 Current Focus block

The main manual block at the top of Home should be:
- `Current Focus`

Its main purpose is to pin:
- primary active project
- current blocker
- primary repo jump point
- immediate next push

### 9.8 Home inbox visibility

Because `inbox` is the default first landing zone for raw capture, Home should still expose it lightly.

Preferred form:
- small entry point
- count / reminder signal

Home should not promote raw inbox into a full equal-sized major section.

### 9.9 Web navigation scope

The web left navigation should expose:
- `indexes/`
- `compiled/`

It should not foreground `raw/` in the main navigation tree.

### 9.10 Graph scope

The first graph view should include only:
- compiled objects

Do not put:
- raw items
- index pages

into the primary graph model by default.

## 10. Audit and Provenance

### 10.1 Audit priority

Audit should be high-intensity.

All compiled page families should be auditable:
- projects
- ideas
- knowledge
- people
- review

Raw pages may also support audit as a secondary capability.

### 10.2 Provenance visibility

Compiled pages should visibly expose provenance.

Preferred style:
- provenance should appear in-page
- references should feel natural and readable
- links should be embedded in prose instead of added as awkward afterthoughts

### 10.3 Manual edits on compiled pages

Compiled pages should support both:
- AI-maintained zones
- human-maintained zones

This prevents manual content from being overwritten by later compile runs.

## 11. Operation Model

### 11.1 Keep the original operation skeleton

Retain:
- `ingest`
- `compile`
- `query`
- `lint`
- `audit`

Add:
- `review`
- `promote`

### 11.2 Query behavior

Query should:
- read compiled first
- fall back to raw/repo when needed

Query outputs should be temporary by default.
Durable outputs can later be promoted.

Canonical query contract:
- Inputs:
  - a natural-language question
  - optional scope constraint
- Reads:
  - `WORKBENCH.md`
  - `compiled/_meta/registry.json`
  - relevant compiled pages
  - raw or repo sources only when compiled is insufficient
- Writes:
  - `outputs/queries/<date>-<slug>.md`
  - `log/YYYYMMDD.md`
- Primary output:
  - a temporary query artifact
- Non-goals:
  - directly creating compiled objects without `promote`

### 11.3 Compile behavior

Compile should:
- run on a weekly cadence
- be triggered by semi-automatic reminder
- update only objects that show new signals
- avoid heavy full recompile

Canonical compile contract:
- Inputs:
  - explicit compile request or scheduled compile trigger
  - optional target scope
- Reads:
  - `WORKBENCH.md`
  - `compiled/_meta/registry.json`
  - raw sources
  - repo signals
  - existing compiled objects
- Writes:
  - compiled object pages
  - generated index pages
  - `compiled/_meta/registry.json`
  - `log/YYYYMMDD.md`
- Primary outputs:
  - refreshed compiled layer
  - refreshed indexes
  - refreshed registry
- Selection rule:
  - default to signal-driven partial updates
  - full recompile should be an explicit management action
- Non-goals:
  - unconditional full rewrite of all objects on every run

### 11.4 Promote behavior

Promote should support:
- `raw-derived candidate -> idea`
- `idea -> project`

Canonical promote contract:
- Inputs:
  - candidate object
  - target type
- Reads:
  - relevant raw pages
  - relevant compiled pages
  - `compiled/_meta/registry.json`
- Writes:
  - target compiled object only after confirmation
  - `log/YYYYMMDD.md`
- Promotion rule:
  - candidates should be surfaced first
  - final promotion requires user confirmation
- Non-goals:
  - silent automatic creation of new `idea` or `project` objects

### 11.5 Ingest behavior

Ingest should absorb:
- external materials
- legacy vault pages
- repo signals

Canonical ingest contract:
- Inputs:
  - legacy vault pages
  - external materials
  - repo-derived signals or control documents
- Reads:
  - source material being ingested
  - `WORKBENCH.md` for policy
- Writes:
  - raw-layer files only
  - `log/YYYYMMDD.md`
- Primary outputs:
  - normalized raw material available for later compile
- Non-goals:
  - direct writing into `compiled/`
  - direct writing into `indexes/`
  - direct writing into `compiled/_meta/registry.json`

### 11.6 Lint behavior

Lint should focus on:
- disconnected objects
- missing provenance
- stale compiled pages whose source signals have changed

Canonical lint contract:
- Inputs:
  - explicit lint request
- Reads:
  - `WORKBENCH.md`
  - `compiled/_meta/registry.json`
  - compiled pages
  - indexes
  - audit files
  - log files
- Writes:
  - no canonical content files by default
  - optional `log/YYYYMMDD.md` entry
- Default behavior:
  - report issues
  - suggest safe fixes when mechanical remediation is obvious
- Non-goals:
  - directly rewriting content by default

### 11.7 Capture behavior

New low-friction capture should default to:
- `raw/inbox/`

Recommended baseline behavior:
- one capture per file
- inbox first
- daily independent

Daily notes may remain manually authored without requiring strict synchronization from inbox items.

### 11.8 Review behavior

Canonical review contract:
- Inputs:
  - current knowledge objects
  - selected raw candidates
- Reads:
  - `compiled/_meta/registry.json`
  - knowledge pages
  - supporting raw evidence when needed
- Writes:
  - `compiled/review/Review.md`
  - `log/YYYYMMDD.md`
- Primary outputs:
  - refreshed review queue
  - updated `next_action` recommendations
- Non-goals:
  - directly advancing knowledge digestion state by itself

### 11.9 Audit behavior

Canonical audit contract:
- Inputs:
  - open audit files
- Reads:
  - audit entries
  - target pages
  - supporting source material when needed
- Writes:
  - target file if correction is accepted or partially accepted
  - audit resolution notes
  - movement to `audit/resolved/` when resolved
  - `log/YYYYMMDD.md`
- Resolution classes:
  - `accept`
  - `partial`
  - `reject`
  - `defer`
- Non-goals:
  - silently ignoring open audit entries

## 12. Module Evolution from Current `llm-wiki-skill`

### 12.1 Keep

Keep and adapt:
- raw/log/audit backbone
- audit review logic
- audit plugin
- web browsing + audit structure
- operation-based maintenance approach

### 12.2 Redesign

Redesign:
- `wiki/` into `compiled/`
- scaffold output
- schema structure
- graph model
- lint rules
- compile target model

### 12.3 Add

Add:
- project compiler
- idea compiler
- review compiler
- repo-aware project signal reader
- generated index pages for each object family
- signal-based compile orchestration

### 12.4 Compatibility strategy

Compatibility should be explicitly one-way and migration-oriented.

The new canonical system should not continue treating the old `wiki/` tree and `CLAUDE.md` as primary truth.

Compatibility policy:
- `WORKBENCH.md` replaces `CLAUDE.md`
- `compiled/` replaces `wiki/`
- `indexes/` replaces the old single `wiki/index.md` navigation role
- minimal transitional compatibility may exist for browsing or migration
- long-term dual-canonical support is not a design goal

## 13. Generated Indexes and Registry

The system should auto-maintain object-level index pages for:
- Projects
- Ideas
- Knowledge
- People
- Review

Homepage is not enough by itself.

### 13.1 Index grouping rules

Recommended grouping for user-facing index pages:
- `Projects.md`: grouped by project status
- `Ideas.md`: grouped by idea maturity
- `Knowledge.md`: grouped by thematic domain
- `People.md`: grouped by relationship role
- `Review.md`: grouped by digestion stage

### 13.2 Home page section order

The current preferred stable order for `indexes/Home.md` is:
1. Current Focus
2. Projects
3. Ideas
4. Review
5. People
6. Recent Changes

Additionally:
- keep a light inbox entry and count near the top

### 13.3 Hidden machine registry

The system should maintain a hidden machine-readable registry at:
- `compiled/_meta/registry.json`

This registry is:
- not a primary user-facing page
- part of compiled system support
- intended for `compile`, `lint`, `web`, and `query` support

### 13.4 Registry format policy

Registry should use:
- JSON as the primary format

Registry design should follow:
- a thin shared core
- type-specific extensions per object family

The canonical top-level shape should be:
- `meta`
- `objects`

`objects` should be one unified array.
Do not split the top level into per-type buckets.

The minimum public contract for every registry object should be:
- `id`
- `type`
- `path`
- `title`
- `status`
- `summary`
- `updated_at`
- `source_count`
- `audit_open_count`
- `source_refs`

The minimum registry `id` policy should be:
- `type + stable slug or canonical path fragment`

Examples:
- `project:droi`
- `idea:trust-metric`
- `knowledge:Calibration`
- `people:Penggao Yan`

`source_refs` should use explicit namespace prefixes.
Preferred forms:
- `vault:raw/...`
- `vault:compiled/...`
- `repo:<project-slug>/...`

The common relationship field should be:
- `related_object_ids`

The registry is the canonical generation source for:
- `indexes/Home.md`
- `indexes/Projects.md`
- `indexes/Ideas.md`
- `indexes/Knowledge.md`
- `indexes/People.md`
- `indexes/Review.md`

Generated indexes should not become a second competing source of truth.

### 13.5 Registry type-specific extensions

Type-specific extension objects should remain thin.

Minimum extension fields by type:
- `project`
  - `repo_slug`
  - `execution_entry`
  - `related_object_ids`
- `idea`
  - `proposition`
  - `related_object_ids`
- `knowledge`
  - `domain`
  - `related_object_ids`
- `people`
  - `role`
  - `affiliation`
  - `next_followup`
  - `related_object_ids`
- `review`
  - `stage`
  - `next_action`
  - `related_object_ids`

`review` may be represented as logical queue entries rather than standalone long-form pages.
The main rendered aggregation surface should still center on `compiled/review/Review.md`.

### 13.6 Provenance rule scope

Compiled page families should follow one shared provenance philosophy:
- provenance is visible in-page
- links feel natural in prose
- the rule is shared across object families, even if exact page wording varies

## 14. Risks

Primary risk:
- the system becomes too heavy to maintain

Therefore the front-stage user experience must remain light:
- daily capture stays simple
- compile happens in batches
- AI absorbs complexity in the background
- the user should not need to manually maintain many dashboards

## 15. Open Questions

There are no remaining blocking open questions for the core system contract.

Remaining future-facing questions, if any, should be treated as later product expansion topics rather than blockers for implementation of the canonical system.
