---
name: bcp-calculator-13d
description: >
  Calculates BCP (Business Complexity Points) using the 13-dimensions engine.
  Runs locally — the agent processes the prompts directly, no external API.
  Triggers: "calculate BCP 13 dimensions", "bcp 13d", "assess complexity 13d",
  "BCP 13 dimensions", "how much is this story in BCP 13d", "bcp-calculator-13d".
---

# BCP Calculator 13D — Local Execution

BCP (Business Complexity Points) is the complexity metric used in CI&T Flow. This skill runs the 13-dimensions decomposed pipeline locally — the agent itself processes the 14 prompts directly. No external API, no MCP, no SDK. The agent IS the LLM.

The result includes: **BCP Total**, **CMS** (Complexity Maturity Score), **IMS** (INVEST Maturity Score), and the scores of all 13 dimensions (10 functional + 3 NFR).

## Language

Always respond in the user's language. If the user writes in Portuguese, respond in Portuguese. If in English, respond in English. Dimension names and technical terms (Business Rules, Interface Elements, NFR, BCP, CMS, IMS, etc.) remain in English. Translate any prompt output that comes in English to the user's language in the final presentation.

## Absolute Determinism

> **Absolute determinism:** When processing each prompt, return EXACTLY the requested JSON — no variations, no abstractions, no paraphrases, no additions. The prompt defines the output format; follow it rigorously. Do not add extra fields, do not omit required fields, do not reinterpret the instructions. Each cell must produce the same output for the same input, always. If the prompt asks for `{"scores_extracted": [1, 3]}`, return exactly that — not `"scores_extracted": [1, 3, "extra"]` nor `{"scores": [1, 3]}`.

## Time Warning

⚠️ The 13D calculation evaluates each story in 14 independent steps. It may take 15-60 seconds per story. Inform the user before starting.

## How It Works

The pipeline runs 14 cells in 3 waves:

- **Wave 1:** 10 functional dimension prompts + 1 NFR prompt = 11 cells
- **Wave 2:** 1 aggregator cell (depends on the 10 functional scores from Wave 1)
- **Wave 3:** 2 maturity cells (depend on the aggregator + NFR from Wave 1/2)

**Total BCP = aggregator.score + nfr_scoring.score**

Maturity scores (CMS and IMS) are complementary — they do not factor into the Total BCP.

---

## Step 1 — Identify the Stories

The input can be:

| Format | Description |
|--------|-------------|
| Inline text | The user pastes the story directly into the chat |
| `.md` file | The user provides a path to a `.md` file |
| Folder | The user provides a path to a folder containing `story-*.md` files |

For `.md` files, extract:

- **Title:** the `title:` field from frontmatter, or the first `# ` heading
- **Description:** concatenate sections matching "Business Narrative", "Technical Narrative", "Acceptance Criteria" (and synonyms like "Flows", "Preconditions", "User View")
- **Key:** the `jira_issue:` field from frontmatter, or the filename (without extension)

## Step 2 — Prepare Story Variables

For each story, prepare:

- `key`: traceability ID (jira_issue > filename > STORY-{id})
- `summary`: the story title
- `description`: concatenated relevant sections

These variables fill `{{story.key}}`, `{{story.summary}}`, `{{story.description}}` in the prompts.

## Step 3 — Group Stories into Waves

If there are multiple stories: group 3-5 stories per wave. Process each wave completely before moving to the next. Show progress: "Processing wave 1/3 — Story 2/5..."

## Step 4 — Execute Wave 1 (11 Cells)

For each story, process 11 prompts. The prompts and their paths (relative to this skill's directory):

| Cell | Prompt |
|------|--------|
| functional_business_rules | `prompts/thirteen/functional/business-rules.md` |
| functional_interface_elements | `prompts/thirteen/functional/interface-elements.md` |
| functional_solution_variabilities | `prompts/thirteen/functional/solution-variabilities.md` |
| functional_domain_entities | `prompts/thirteen/functional/domain-entities.md` |
| functional_new_domain_entities | `prompts/thirteen/functional/new-domain-entities.md` |
| functional_roles_permissions | `prompts/thirteen/functional/roles-permissions.md` |
| functional_boundaries | `prompts/thirteen/functional/boundaries.md` |
| functional_background_processes | `prompts/thirteen/functional/background-processes.md` |
| functional_notifications | `prompts/thirteen/functional/notifications.md` |
| functional_audits | `prompts/thirteen/functional/audits.md` |
| nfr_scoring | `prompts/thirteen/nfr-scoring.md` |

For each prompt:

1. Read the `.md` file from this skill's `prompts/` directory (relative to the SKILL.md location)
2. Replace `{{story.key}}`, `{{story.summary}}`, `{{story.description}}` with the story's values
3. Process the prompt — you ARE the LLM. Follow the prompt's instructions exactly. Return ONLY the specified JSON.
4. Extract the JSON from your response
5. Store the raw JSON output for this cell

## Step 5 — Execute Wave 2 (Aggregator)

Read `prompts/thirteen/functional/aggregator.md`. Replace:

- `{{story.key}}`, `{{story.summary}}`, `{{story.description}}` — story variables
- `{{dim_business_rules}}`, `{{dim_interface_elements}}`, `{{dim_solution_variabilities}}`, `{{dim_domain_entities}}`, `{{dim_new_domain_entities}}`, `{{dim_roles_permissions}}`, `{{dim_boundaries}}`, `{{dim_background_processes}}`, `{{dim_notifications}}`, `{{dim_audits}}` — the numeric scores extracted from Wave 1

Process the prompt, extract the JSON, store the raw output.

## Step 6 — Execute Wave 3 (Maturity)

Two prompts in parallel:

| Cell | Prompt |
|------|--------|
| complexity_maturity | `prompts/thirteen/complexity-maturity.md` |
| invest_maturity | `prompts/thirteen/invest-maturity.md` |

For each, replace:

- `{{story.key}}`, `{{story.summary}}`, `{{story.description}}` — story variables
- `{{functional_scoring}}` — the complete JSON output from the aggregator (Wave 2)
- `{{nfr_scoring}}` — the complete JSON output from nfr_scoring (Wave 1)

Process each prompt, extract the JSON, store the raw output.

## Step 7 — Calculate Scores with the Script

Use the bundled script to calculate scores and consolidate:

```bash
# For each cell, calculate the score:
python scripts/bcp_pipeline.py score --cell business_rules --output '{"scores_extracted": [3, 5]}'

# For the aggregator:
python scripts/bcp_pipeline.py aggregate --bindings '{"dim_business_rules": 8, ...}'

# To consolidate a complete story:
python scripts/bcp_pipeline.py consolidate --input story_results.json

# To aggregate multiple stories:
python scripts/bcp_pipeline.py aggregate-stories --input all_stories.json
```

## Score Formulas

The 14 formulas used to calculate each cell's score from the JSON output:

| Cell | Formula |
|------|---------|
| business_rules | Sum all values in the `scores_extracted` array |
| interface_elements | `ceil(len(static_elements)/5) × static_weight + ceil(len(dynamic_elements)/5) × dynamic_weight` |
| solution_variabilities | Direct value from the `dimension_solution_variabilities` field |
| domain_entities | Direct value from the `dimension_domain_entities` field |
| new_domain_entities | `2 × ceil(len(block_a_modified)/3) + 5 × ceil(len(block_b_new)/3)` |
| roles_permissions | Direct value from the `dimension_roles_permissions` field |
| boundaries | Sum all values in the `scores_extracted` array |
| background_processes | Direct value from the `dimension_background_processes` field |
| notifications | Count elements in the `notification_events` array |
| audits | Count elements in the `audited_entities` array |
| nfr_scoring | Sum `dimension_quality_attributes + dimension_security_compliance + dimension_user_experience_accessibility` |
| aggregator | Sum the 10 `dim_*` scores |
| complexity_maturity | Direct value from the `score` field (0-5) |
| invest_maturity | Direct value from the `score` field (0-5) |

**Total BCP = aggregator.score + nfr_scoring.score**

## Step 8 — Present the Result

### Single Story

Present the following tables:

**Summary:**

| Metric | Value |
|--------|-------|
| BCP Total | {total_bcp} |
| CMS (Complexity Maturity) | {complexity_maturity_score}/5 — {classification} |
| IMS (INVEST Maturity) | {invest_maturity_score}/5 — {classification} |

**Functional Dimensions (D1-D10):**

| ID | Dimension | Score |
|----|-----------|-------|
| D1 | Business Rules | {score} |
| D2 | Interface Elements | {score} |
| D3 | Solution Variabilities | {score} |
| D4 | Domain Entities | {score} |
| D5 | New Domain Entities | {score} |
| D6 | Roles & Permissions | {score} |
| D7 | Boundaries | {score} |
| D8 | Background Processes | {score} |
| D9 | Notifications | {score} |
| D10 | Audits | {score} |
| | **Functional Subtotal** | **{aggregator_score}** |

**NFR Dimensions (D11-D13):**

| ID | Dimension | Score |
|----|-----------|-------|
| D11 | Quality Attributes | {score} |
| D12 | Security & Compliance | {score} |
| D13 | UX & Accessibility | {score} |
| | **NFR Subtotal** | **{nfr_score}** |

**Complexity Maturity:**

| Criterion | Value |
|-----------|-------|
| Clarity | {clarity}/5 |
| Completeness | {completeness}/5 |
| Explicit Definitions | {explicit_definitions}/5 |
| Testability | {testability}/5 |
| Business Value | {business_value}/5 |
| **Score** | **{score}/5 — {classification}** |

Gaps: list each item from the `gaps` array. Questions: list each item from the `questions` array.

**INVEST Maturity:**

| Criterion | Value |
|-----------|-------|
| Independent | {independent}/5 |
| Negotiable | {negotiable}/5 |
| Valuable | {valuable}/5 |
| Estimable | {estimable}/5 |
| Small | {small}/5 |
| Testable | {testable}/5 |
| **Score** | **{score}/5 — {classification}** |

Gaps: list each item from the `gaps` array. Questions: list each item from the `questions` array.

### Batch (Multiple Stories)

First, a summary table:

| Story | Key | BCP Total | Functional | NFR | CMS | IMS |
|-------|-----|-----------|------------|-----|-----|-----|
| {summary} | {key} | {total_bcp} | {functional} | {nfr} | {cms}/5 | {ims}/5 |

Then, the individual details for each story in the same format as the single story.

## Trigger Examples

- "Calculate BCP 13 dimensions for this story: ..."
- "Calculate BCP 13d for the file `docs/stories/story-001.md`"
- "Calculate BCP 13d for all stories in the folder `docs/PRD/sprint-42/`"
- "bcp-calculator-13d"

## Complete Flow Summary

```
Warning:  Inform wait time (~15-60s per story)
Step 1: Identify stories (inline, --file, or folder)
Step 2: Prepare variables (key, summary, description)
Step 3: Group into waves (3-5 stories per wave if batch)
Step 4: Wave 1 — process 11 prompts per story
Step 5: Wave 2 — process aggregator with Wave 1 bindings
Step 6: Wave 3 — process 2 maturity prompts with Wave 2 + NFR bindings
Step 7: Calculate scores and consolidate via bcp_pipeline.py
Step 8: Present results (tables)
```
