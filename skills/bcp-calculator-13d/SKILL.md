---
name: bcp-calculator-13d
description: >
  (flow-ciandt) Calculates BCP (Business Complexity Points) using the 13-dimensions engine from the local BCP Calculator API.
  Use when the user wants to calculate, estimate, or evaluate BCP with the full 13-dimensions model
  — whether by pasting the story in chat, pointing to a .md file, or a folder of stories.
  Triggers: "calcular BCP 13 dimensões", "bcp 13d", "avaliar complexidade 13d",
  "BCP 13 dimensões", "quanto vale essa story em BCP 13d", "bcp-calculator-13d".
---

# BCP Calculator 13D — Local API

BCP (Business Complexity Points) is the complexity metric used in CI&T's Flow. This skill
calls the **13-dimensions** engine of the local BCP Calculator API (`run_api_server.py`) to
calculate BCP from the story title and technical refinement.

It returns the BCP Total, CMS (Complexity Maturity Score), IMS (INVEST Maturity Score), and
the complete breakdown of all 13 dimensions — 10 functional and 3 non-functional — with
individual scores and justifications.

The skill is responsible only for the **calculation**. Saving results to files is the
responsibility of the agent that invokes the skill.

### Language

**Always respond in the same language the user is interacting in.** The API returns summaries,
classifications, and gaps in English — **translate everything** when presenting the result. Examples:

- `"Demonstrates Good Maturity"` → `"Demonstra Boa Maturidade"` (if pt-BR)
- `"Eight rules identified with a total score of 20"` → `"Oito regras identificadas com score total de 20"`
- `"Missing error handling scenarios"` → `"Cenários de tratamento de erro ausentes"`

Dimension names (D1 · Business Rules, D12 · Security & Compliance, etc.) and technical
terms (BCP, CMS, IMS) **keep their original English names** — they are domain terms.

> **Important:** The 13D calculation runs **14 independent LLM steps** and may take
15 to 60 seconds per story. Inform the user about the wait time before starting:

> ⏳ The BCP 13-dimensions calculation evaluates your story in 14 independent LLM steps.
> This may take 15 to 60 seconds per story. Please wait...

---

## Step 1 — Verify the local server is running

The skill calls the local BCP Calculator API (`run_api_server.py`), which runs by default at
`http://127.0.0.1:8000`. Before proceeding, verify that the server is active:

```bash
curl -s http://127.0.0.1:8000/ || echo "SERVER OFFLINE"
```

- **Online:** proceed to Step 2.
- **Offline:** guide the user to start the server:
  ```bash
  cd projects/bcp-agent
  python run_api_server.py
  ```
  Wait for confirmation that the server started (`"Starting BCP Calculator API server on 127.0.0.1:8000"`)
  before continuing.

> The local API **does not require authentication** — the local server accepts requests
> directly, without a token.

---

## Step 2 — Identify the stories

| Source | How to obtain |
|--------|---------------|
| Text in chat | Extract title and relevant sections directly |
| Single `.md` file | Use `--file` — the script extracts automatically |
| Folder | Glob to list `story-*.md` files, use `--file` for each |

For each story:

- **`.md` file:** pass `--file path/to/story.md`. The script automatically extracts the title
  (frontmatter `title:` or first `# `) and composes the `description` by concatenating the sections:
  - `## Narrativa de Negócio` (Business Narrative — includes `### Regras de Negócio` (Business Rules) and relevant `### Edge Cases`)
  - `## Narrativa Técnica` (Technical Narrative)
  - `## Critérios de Aceite` (Acceptance Criteria)

- **Inline text:** pass `--title` and `--description` with the content of the same sections above.
- `id` — incremental index (0, 1, 2…) if no explicit ID

> If the script returns a "No relevant sections found" error, the story is incomplete — notify
> the user and do not proceed with the calculation.

If the user triggers the skill **without providing a story**, request the content before
proceeding. Do not attempt to calculate without input.

---

## Step 3 — Calculate BCP via script

Use the bundled script for each story. The script encapsulates the API call and returns JSON:

```bash
python /path/to/skill/scripts/bcp_calculate_13d.py \
  --file path/to/story.md \
  --id 0
```

Or with inline text:

```bash
python /path/to/skill/scripts/bcp_calculate_13d.py \
  --title "Story Title" \
  --description "Complete technical refinement" \
  --id 0
```

With explicit LLM provider:

```bash
python /path/to/skill/scripts/bcp_calculate_13d.py \
  --file path/to/story.md \
  --provider openai
```

> The script path is relative to the skill location. Use the absolute path when executing.

### Complete parameter reference

| Parameter | Required | Default | Description |
|-----------|:---------:|---------|-------------|
| `--file` | ⚠️ exclusive with `--title` | — | Path to `.md` file — extracts title and sections automatically |
| `--title` | ⚠️ exclusive with `--file` | — | Story title (requires `--description`) |
| `--description` | ✅ when `--title` | — | Complete technical refinement/description |
| `--id` | ❌ | `0` | Numeric incremental ID for batch identification |
| `--key` | ❌ | auto | Traceability key. Fallback: frontmatter `jira_issue:` → filename → `STORY-{id}` |
| `--base-url` | ❌ | `http://127.0.0.1:8000` | Local API base URL — allows pointing to a different port/host |
| `--provider` | ❌ | `openai` | LLM provider. Options: `openai`, `claude`, `flow-openai` |

**Two mutually exclusive modes:**
- **`--file`** → extracts title (frontmatter `title:` or `# `) + relevant sections automatically
- **`--title` + `--description`** → text passed directly

For large batches (>5 stories), process in groups of up to 5 and show progress to the user:
`"Calculating story 2/5..."`

> **Sequential processing:** each story is calculated individually (~15-60s). For 10
> stories, total time is ~3-10 min. There is no parallelism — the API processes one at a time.

### Retry on failure

If the script returns `"has_failures": true`, re-run the call (up to 2 retries).
The script already does internal retries, but if the final result still has failures, inform the user:

> ❌ Could not calculate complete BCP — X dimensions failed after 3 attempts.
> Try again later or verify that the API is stable.

### Error codes

| HTTP | Action |
|------|--------|
| 404 | Job not found — server may have restarted (jobs are in-memory). Re-run |
| 400 | Invalid data — verify that `title` and `description` are filled |
| 5xx | Server error — wait and try again; if persistent, inform the user |
| Conn | Server offline — guide the user to start `python run_api_server.py` |

---

## Step 4 — Present the result

### Single story

```
## BCP 13D — <story name>

**BCP Total:** X points
**CMS (Complexity Maturity Score):** Y/5 — <classification>
**IMS (INVEST Maturity Score):** Z/5 — <classification>

### Functional Dimensions (D1–D10)
| # | Dimension | Score | Details |
|---|----------|------:|---------|
| D1 | Business Rules | X | <summary> · Items: <items joined by "; "> · Reasoning: <reasoning> |
| D2 | Interface Elements | X | <detail> |
| D3 | Boundaries | X | <detail> |
| D4 | Roles & Permissions | X | <detail> |
| D5 | Solution Variabilities | X | <detail> |
| D6 | Domain Entities | X | <detail> |
| D7 | New Domain Entities | X | <detail> |
| D8 | Background Processes | X | <detail> |
| D9 | Notifications | X | <detail> |
| D10 | Audits | X | <detail> |

> The **Details** column combines up to 3 fields separated by " · ":
> `summary` (always present) + `Items: <items>` (if any) + `Reasoning: <reasoning>` (if any).
> If items or reasoning are empty, omit that part — do not show "Items: —".

### Non-Functional Dimensions (D11–D13)
| # | Dimension | Score | Details |
|---|----------|------:|---------|
| D11 | Quality Attributes | X | <assessment> · <detailed_explanation> |
| D12 | Security & Compliance | X | <assessment> · <detailed_explanation> |
| D13 | UX & Accessibility | X | <assessment> · <detailed_explanation> |

> The **Details** column combines `assessment` + `detailed_explanation` separated by " · ".
> If detailed_explanation is empty, show only the assessment.

### Maturity — Complexity (CMS)
<summary returned by the API>

| Sub-criterion | Score |
|---------------|------:|
| Clarity | X/5 |
| Completeness | X/5 |
| Explicit definitions | X/5 |
| Testability | X/5 |
| Business value | X/5 |

**Identified gaps:**
- <gap 1>
- <gap 2>

### Maturity — INVEST (IMS)
<summary returned by the API>

| Sub-criterion | Score |
|---------------|------:|
| Independent | X/5 |
| Negotiable | X/5 |
| Valuable | X/5 |
| Estimable | X/5 |
| Small | X/5 |
| Testable | X/5 |

**Identified gaps:**
- <gap 1>
- <gap 2>
```

The fields are extracted from the JSON returned by the script:
- `bcp_total` → BCP Total
- `story_name` → story name
- `cms.score`, `cms.classification`, `cms.summary`, `cms.gaps` → CMS section
- `cms.breakdown` → CMS sub-criteria table (clarity, completeness, explicit_definitions, testability, business_value)
- `ims.score`, `ims.classification`, `ims.summary`, `ims.gaps` → IMS section
- `ims.breakdown` → INVEST sub-criteria table (independent, negotiable, valuable, estimable, small, testable)
- `functional_dimensions[].id`, `.name`, `.score`, `.summary`, `.items`, `.reasoning` → Functional Dimensions table
- `nfr_dimensions[].id`, `.name`, `.score`, `.summary`, `.detailed_explanation` → Non-Functional Dimensions table

**Translation:** The fields `summary`, `classification`, `gaps`, and `questions` come in English from the API.
Translate to the user's language when presenting. Keep dimension names
(D1 · Business Rules, etc.) and technical terms (BCP, CMS, IMS) in English.

### Batch (multiple stories)

Present the summary table first, then individual details:

```
## BCP 13D — Batch (N stories)

| # | Story | BCP | CMS | IMS |
|---|-------|-----|-----|-----|
| 1 | Name 1 | X   | Y/5 | Z/5 |
| 2 | Name 2 | X   | Y/5 | Z/5 |
|   | **Total** | **X** | — | — |

**Average BCP:** W pts
**Highest complexity:** <story with highest BCP>
**Lowest complexity:** <story with lowest BCP>
```

After the summary table, present the individual details for each story in the
"Single story" format above.

Errors in one story do not interrupt processing of the others — record the error in
the corresponding row of the table and continue.

---

## Trigger examples

The skill is designed for pt-BR users (Flow/CI&T). Triggers are in Portuguese by design:

- "Calcula o BCP 13 dimensões dessa história: Título: Exportar relatório CSV..."
- "Calcula o BCP 13d do arquivo `docs/stories/story-001.md`"
- "Calcula o BCP 13d de todas as histórias na pasta `docs/PRD/sprint-42/`"
- "Quanto vale essa story em BCP 13 dimensões?" (with story pasted in chat)
- "bcp-calculator-13d" (direct invocation by name)
- "Avaliar complexidade 13d do arquivo `planning/story-login.md`"

## Complete flow summary

```
Notice:  Inform wait time (~15-60s per story)
Step 1:  Verify the local server (run_api_server.py) is running at http://127.0.0.1:8000
Step 2:  Identify story title and description (via script --file or inline)
Step 3:  Call script bcp_calculate_13d.py → retry if has_failures
Step 4:  Present result with BCP total, CMS, IMS, 13 dimensions, and gaps
```
