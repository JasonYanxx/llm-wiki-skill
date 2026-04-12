# Compiled Object Writing Guide

Use this guide when creating or refreshing pages in `compiled/`.
The goal is not to write neutral encyclopedia articles. The goal is to maintain reusable research objects that support the user's ongoing work.

## General rules

- Keep the fixed section structure stable for each object family.
- Write with natural inline Obsidian links.
- Make provenance visible in-page.
- Use mermaid for flows, hierarchies, and state diagrams.
- Use KaTeX for formulas.
- Preserve human-owned sections such as `My Notes`.

## Project page template

```markdown
---
title: <Project Title>
type: project
status: active | holding | done
updated: YYYY-MM-DD
repo_slug: <repo-slug>
execution_entry: PROJECT.md | README.md | docs/index.md
source_refs: [vault:raw/..., repo:<project-slug>/PROJECT.md]
related_object_ids: [idea:..., knowledge:...]
---

# <Project Title>

## Overview

<What the project is and why it exists.>

## Status

<Visible status summary matching frontmatter.>

## Execution Entry

- Repo: `<repo-slug>`
- Main entry: `<path>`

## Related Objects

- [[Related Idea]]
- [[Related Knowledge]]

## AI Compiled

<Rolling AI-maintained summary of the project's current state.>

## My Notes

<!-- Human-owned. Compile must not rewrite. -->

## Provenance

<Natural prose with inline links to raw notes, repo control docs, and related pages.>
```

When using `repo:` source refs, make sure `compiled/_meta/registry.json.meta.repo_roots` maps the same `<project-slug>` to the local repo root so lint can resolve the execution doc on disk.

## Idea page template

```markdown
---
title: <Idea Title>
type: idea
status: spark | exploring | incubating | project-ready
updated: YYYY-MM-DD
proposition: <single proposition sentence>
source_refs: [vault:raw/...]
related_object_ids: [knowledge:..., project:...]
---

# <Idea Title>

## Proposition

<One concrete research question, claim, or hypothesis.>

## Status

<Visible state explanation.>

## AI Judgment

<What the idea is, what it connects to, what is unclear, and how close it is to project-ready.>

## Related Objects

- [[Related Project]]
- [[Related Knowledge]]

## My Notes

<!-- Human-owned. -->

## Provenance

<Link back to the raw notes or prior compiled pages that gave rise to the idea.>
```

## Knowledge page template

```markdown
---
title: <English Canonical Title>
type: knowledge
status: noticed | organized | retained
updated: YYYY-MM-DD
domain: <theme or domain>
source_refs: [vault:raw/..., vault:compiled/projects/...]
related_object_ids: [project:..., idea:...]
---

# <English Canonical Title>

## Current Understanding

<The user's current understanding, not a neutral dictionary definition.>

## Why It Matters

<Why this concept matters for the user's research agenda.>

## Related Projects and Ideas

- [[Project]]
- [[Idea]]

## AI Compiled Body

<AI-maintained synthesis with natural inline links and visible traceability.>

## Provenance

<Key supporting sources and where this understanding came from.>
```

## People page template

```markdown
---
title: <Name>
type: people
status: active
updated: YYYY-MM-DD
role: <relationship role>
affiliation: <institution or org>
next_followup: YYYY-MM-DD | free text
source_refs: [vault:raw/..., vault:compiled/projects/...]
related_object_ids: [project:..., idea:..., knowledge:...]
---

# <Name>

## Current Relationship

<Who this person currently is in the user's world and why they matter now.>

## Academic Profile

<External/public context plus research relevance.>

## Related Objects

- [[Project]]
- [[Knowledge]]

## Recent Interactions

<Recent interaction context.>

## Next Follow-up

<What the next follow-up should be.>

## Provenance

<Traceable links to raw notes, meeting notes, and other supporting material.>
```

## Review page template

```markdown
---
title: Review
type: review
status: active
updated: YYYY-MM-DD
source_refs: []
related_object_ids: []
---

# Review

## Overview

<What changed in the queue and what needs attention now.>

## Noticed

<Knowledge objects that entered the system but are not yet organized.>

## Organized

<Knowledge objects that are linked and structured but not retained.>

## Retained

<Knowledge objects that are now stable and reusable.>

## Deferred

<Items that are intentionally postponed.>
```

## Writing style guidance

- Projects: concise control-page prose, not task-spam.
- Ideas: preserve ambiguity where needed; do not over-formalize too early.
- Knowledge: write for the user's research context, not for a generic audience.
- People: maintain relationship memory and academic context at the same time.
- Review: keep it action-oriented; every entry should imply the next best move.

## Provenance guidance

Good provenance feels readable:
- `This understanding mainly came from [[raw/external/papers/foo]] and was sharpened during [[compiled/projects/bar/index|Bar]].`
- `The idea first appeared in [[raw/daily/2026-04-11]] and later connected to [[Calibration]].`

Bad provenance feels bolted on:
- giant detached citation dumps
- no visible traceability
- links that only appear in frontmatter and nowhere in the page body
