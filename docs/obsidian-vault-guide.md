# Obsidian Vault Guide
**Version:** 1.0  
**Applies to:** Work Vault + Personal Vault (parallel, no sync)  
**Maintainer:** `[your name/handle]`  

---

## Philosophy

Two vaults. One purpose each.

**Work vault** — execution context for active programs. Lives on your work machine. Disposable when you leave a job. Contains everything you need to operate; nothing you need to keep.

**Personal vault** — your long-term professional asset. Lives on your personal machine. Survives every job transition. Contains abstracted knowledge, lessons learned, career development, and transferable program patterns.

The bridge between them is **you** — a deliberate end-of-day ritual where you decide what's worth keeping and abstract it into your personal vault.

**Rule:** Never store anything in your work vault that you couldn't recreate from scratch. Anything irreplaceable belongs in your personal vault.

---

## Vault Structures

### Work Vault

```
Work Vault/
│
├── 000_HOME.md                        ← daily entry point, links to active programs
│
├── Programs/
│   └── [PROGRAM_NAME]/
│       ├── _index.md                  ← program hub note
│       ├── Meetings/
│       │   └── YYYY-MM-DD_[topic].md
│       ├── Decisions/
│       │   └── YYYY-MM-DD_[decision].md
│       ├── Vendors/
│       │   └── [VENDOR_NAME].md
│       ├── Pipeline/
│       │   └── YYYY-MM-DD_run.md      ← converted pipeline briefing outputs
│       └── Reference/
│           └── [document or standard].md
│
├── Stakeholders/
│   └── [NAME].md                      ← one note per person, linked from programs
│
├── Templates/
│   ├── meeting-note.md
│   ├── decision-note.md
│   ├── vendor-note.md
│   └── pipeline-wrap-up.md
│
└── Inbox/
    └── [unsorted notes land here]     ← process weekly, file or discard
```

### Personal Vault

```
Personal Vault/
│
├── 000_HOME.md                        ← entry point, links to current focus areas
│
├── Programs/
│   └── [PROGRAM_NAME]/                ← mirrors work vault structure
│       ├── _index.md                  ← high-level program context only
│       ├── Lessons/
│       │   └── YYYY-MM-DD_[topic].md  ← what you learned, not what happened
│       └── Patterns/
│           └── [reusable pattern].md  ← approaches worth reusing
│
├── Career/
│   ├── brag-doc.md                    ← running log of wins and impact
│   ├── skills-inventory.md            ← what you know and at what depth
│   ├── goals.md                       ← short and long term
│   └── roles/
│       └── [COMPANY]_[ROLE].md        ← one note per job, archived on exit
│
├── Knowledge/
│   ├── Frameworks/
│   │   └── [FRAMEWORK_NAME].md        ← your summaries of standards and frameworks
│   ├── Concepts/
│   │   └── [concept].md               ← evergreen notes on ideas worth keeping
│   └── Tools/
│       └── [tool or system].md        ← how you use things, lessons from use
│
├── Lessons/
│   └── YYYY-MM-DD_[topic].md          ← cross-program lessons, not tied to one job
│
├── Templates/
│   ├── meeting-note.md                ← same templates as work vault
│   ├── decision-note.md
│   ├── vendor-note.md
│   ├── pipeline-wrap-up.md
│   └── lesson-note.md                 ← personal vault only
│
└── Inbox/
    └── [unsorted notes land here]
```

---

## Templates

Copy these into the `Templates/` folder of each vault.

---

### `meeting-note.md`

```markdown
---
tags: [meeting, {{program}}]
date: {{date:YYYY-MM-DD}}
program: 
attendees: 
type: [standup | review | kickoff | vendor | stakeholder | 1on1]
---

# {{date:YYYY-MM-DD}} — [Meeting Topic]

**Program:** [[Programs/[PROGRAM_NAME]/_index]]  
**Attendees:**  
**Duration:**  

---

## Context
[1-2 sentences — why this meeting happened]

## Discussion
[bullet points — what was covered, not full transcript]

## Decisions Made
[list any decisions — link to Decisions/ note if significant]

## Actions
| Action | Owner | Due |
|---|---|---|
| | | |

## Open Questions
[anything unresolved that needs follow-up]

## Notes for Personal Vault
[anything worth abstracting — lessons, patterns, flags]
```

---

### `decision-note.md`

```markdown
---
tags: [decision, {{program}}]
date: {{date:YYYY-MM-DD}}
program: 
status: [decided | pending | reversed]
---

# Decision: [Title]

**Date:** {{date:YYYY-MM-DD}}  
**Program:** [[Programs/[PROGRAM_NAME]/_index]]  
**Decision Maker(s):**  
**Status:**  

---

## Context
[Why did this decision need to be made?]

## Options Considered
| Option | Pros | Cons |
|---|---|---|
| | | |

## Decision
[What was decided, in one clear sentence]

## Rationale
[Why this option over others]

## Implications
[What changes as a result of this decision]

## Revisit Conditions
[Under what circumstances should this be revisited?]

## Notes for Personal Vault
[Is this a pattern worth keeping? A lesson? A cautionary tale?]
```

---

### `vendor-note.md`

```markdown
---
tags: [vendor, {{program}}]
date: {{date:YYYY-MM-DD}}
program: 
vendor: 
contact: 
contract_ref: 
---

# Vendor: [VENDOR NAME]

**Program:** [[Programs/[PROGRAM_NAME]/_index]]  
**Primary Contact:**  
**Contract / SOW Ref:**  
**Engagement Start:**  

---

## Scope of Work
[What is this vendor responsible for delivering?]

## Current Status
[1-2 sentences — where things stand today]

## Performance History
| Date | Score | Notes |
|---|---|---|
| | | |

## Open Issues
[list any active concerns, blockers, or escalations]

## Communication Log
| Date | Type | Summary | Follow-up Needed |
|---|---|---|---|
| | | | |

## Notes for Personal Vault
[Vendor management lessons worth keeping]
```

---

### `pipeline-wrap-up.md`

```markdown
---
tags: [pipeline, {{program}}]
date: {{date:YYYY-MM-DD}}
program: 
run_intent: [new_program | monitoring_run | vendor_review | full_run]
---

# Pipeline Run — {{date:YYYY-MM-DD}}

**Program:** [[Programs/[PROGRAM_NAME]/_index]]  
**Intent:** 
**Overall Health:** [🟢 GREEN | 🟡 YELLOW | 🔴 RED]  
**One-line status:**  

---

## Decision Queue
[paste or summarize from briefing output]

## Watch Items
[paste or summarize from briefing output]

## Escalations
[paste or summarize — none if clean]

## Communications Sent Today
[list what you sent, to whom]

## Flags Resolved
[any flags from prior run you closed today]

## Flags Still Open
[carry forward unresolved flags]

## Next Run
**Recommended date:**  
**Recommended intent:**  
**Reason:**  

---

## Notes for Personal Vault
[Anything from today's run worth abstracting — patterns, lessons, decisions]
```

---

### `lesson-note.md` *(Personal vault only)*

```markdown
---
tags: [lesson, {{context}}]
date: {{date:YYYY-MM-DD}}
source: [program | vendor | stakeholder | general]
program: 
---

# Lesson: [Title]

**Date:** {{date:YYYY-MM-DD}}  
**Source:**  
**Program context:** *(leave blank if general)*  

---

## What Happened
[Brief, factual summary — 2-4 sentences]

## What I Learned
[The transferable insight — written as if advising someone else]

## What I Would Do Differently
[Specific, actionable]

## Where This Applies
[Other contexts where this lesson is relevant]

## Related Notes
[links to related lessons, decisions, or concepts]
```

---

## Plugin Stack

Keep this minimal. Every plugin is a maintenance dependency. These are chosen for stability, active maintenance, and direct utility to this workflow.

### Core (install these first)

| Plugin | Purpose | Why it earns its place |
|---|---|---|
| **Templater** | Dynamic templates with dates, prompts, and logic | Replaces built-in templates — far more powerful, used by every template above |
| **Dataview** | Query your vault like a database | Surfaces all open actions, decisions by program, and vendor notes without manual linking |
| **Calendar** | Daily note navigation | Simple date-based entry point — pairs with your daily pipeline wrap-up habit |
| **Periodic Notes** | Daily and weekly note structure | Drives the end-of-day ritual and weekly review |

### Recommended (add when comfortable)

| Plugin | Purpose | Notes |
|---|---|---|
| **QuickAdd** | One-keystroke note creation from any template | Eliminates friction from creating meeting or decision notes mid-call |
| **Tag Wrangler** | Manage and rename tags across vault | Keeps your tag taxonomy clean as vault grows |
| **Obsidian Git** | Auto-commit vault to git on a schedule | Version control for your notes — especially valuable for work vault |

### Skip for now

- **Kanban** — your task management lives in pipeline JSON, not Obsidian
- **Excalidraw** — powerful but heavyweight; add only if you sketch architectures regularly
- **Omnisearch** — only needed when vault is very large; built-in search is sufficient early on

---

## Dataview Queries

Add these to your `000_HOME.md` in each vault for instant program visibility.

### All open actions across all meeting notes
````
```dataview
TABLE action, owner, due
FROM "Programs"
WHERE contains(tags, "meeting")
FLATTEN actions as action
SORT due ASC
```
````

### All programs and their health (from pipeline wrap-up notes)
````
```dataview
TABLE run_intent, file.mtime as "Last Updated"
FROM "Programs"
WHERE contains(tags, "pipeline")
SORT file.mtime DESC
```
````

### All open vendor issues
````
```dataview
TABLE vendor, contact, file.mtime as "Last Updated"
FROM "Programs"
WHERE contains(tags, "vendor")
SORT file.mtime DESC
```
````

### Recent decisions across all programs
````
```dataview
TABLE program, status, file.ctime as "Date"
FROM "Programs"
WHERE contains(tags, "decision")
SORT file.ctime DESC
LIMIT 10
```
````

---

## End-of-Day Ritual

This is the bridge between your pipeline outputs and your Obsidian vaults. Target time: **10–15 minutes.**

### Step 1 — Pipeline wrap-up note (Work vault)

Open Obsidian. Use QuickAdd or Templater to create a new note from `pipeline-wrap-up.md` in the relevant program's `Pipeline/` folder.

Paste or summarize from your daily briefing output:
- Decision queue items and how you resolved them
- Watch items
- Communications sent
- Flags resolved or still open
- Next run recommendation

### Step 2 — File any meeting or decision notes (Work vault)

If you took meeting notes during the day, move them from `Inbox/` into the correct program folder. Apply the appropriate template if notes are freeform.

### Step 3 — Personal vault transfer (Personal vault, 2–3 minutes)

Review your work vault notes from today. Ask for each one:

> *Is there anything here I'd want to know at my next job?*

If yes — open your personal vault and create a `lesson-note.md` or add to `brag-doc.md`. Abstract the insight away from company-specific context. One or two notes per day is enough. Most days will produce nothing worth keeping.

### Step 4 — Weekly (Fridays, 10 minutes)

- Process `Inbox/` in both vaults — file or delete everything
- Update `brag-doc.md` with any wins from the week
- Check `goals.md` — are you moving toward anything that matters?

---

## Suggested Repo Path

This guide lives in your personal vault at:  
`Knowledge/Tools/obsidian-vault-guide.md`

A copy can also live in your pipeline repo at:  
`/docs/obsidian-vault-guide.md`
