# BCP Agent Usage Guide

The Business Complexity Points (BCP) Agent is a command-line tool that helps calculate the complexity of user stories using advanced language models. This guide provides detailed instructions on how to use the tool effectively.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd bcp-agent
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   ```
   cp .env.flow.example .env
   ```

4. Edit the `.env` file to add your API keys:
   ```
   # OpenAI API Key (required if using OpenAI provider)
   OPENAI_API_KEY=your_openai_api_key_here

   # Anthropic API Key (required if using Claude provider)
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

## Basic Usage

Run the BCP Agent with a user story file:

```bash
python run_cli.py path/to/user_story.md
```

This will process the user story using the default settings (OpenAI provider, JSON output format).

## Command-Line Arguments

The BCP Agent supports several command-line arguments to customize its behavior:

| Argument | Description | Default |
|----------|-------------|---------|
| `story_file` | Path to the user story markdown file (required) | - |
| `--log-level` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | INFO |
| `--output-file` | Path to save the results (if not specified, prints to stdout) | None |
| `--format` | Output format (text or json) | json |
| `--provider` | LLM provider to use (openai, claude, flow-openai, flow-bedrock) | openai |
| `--max-workers` | Maximum parallel threads per wave | 5 |

## Examples

### Process a Story with Default Settings

```bash
python run_cli.py tests/data/story1.md
```

### Using Different Providers

With OpenAI:
```bash
python run_cli.py tests/data/story1.md --provider openai
```

With Claude:
```bash
python run_cli.py tests/data/story1.md --provider claude
```

### Saving Results

Save as JSON:
```bash
python run_cli.py tests/data/story1.md --output-file results.json
```

Save as text:
```bash
python run_cli.py tests/data/story1.md --format text --output-file results.txt
```

### Detailed Debugging

For verbose output:
```bash
python run_cli.py tests/data/story1.md --log-level DEBUG
```

## Understanding the Output

The BCP Agent provides a comprehensive output that includes:

1. **Total BCP**: Sum of all functional dimension scores + NFR score (aggregator.score + nfr_scoring.score)
2. **Breakdown**: Individual scores for all 11 dimensions (10 functional + 1 NFR)
3. **Maturity**: Complexity Maturity Score (CMS, 0-5) and INVEST Maturity Score (IMS, 0-5)
4. **Cells**: Detailed results from each of the 14 pipeline cells across 3 waves

### Sample JSON Output

```json
{
  "story_name": "User Story: Add Payment Method",
  "total_bcp": 28,
  "breakdown": {
    "business_rules": 7,
    "interface_elements": 5,
    "solution_variabilities": 1,
    "domain_entities": 2,
    "new_domain_entities": 0,
    "roles_permissions": 2,
    "boundaries": 3,
    "background_processes": 0,
    "notifications": 0,
    "audits": 0,
    "nfr": 8
  },
  "maturity": {
    "complexity": 3,
    "invest": 4
  },
  "cells": {
    "functional_business_rules": {"score": 7, "raw_output": {"summary": "3 rules identified"}},
    "functional_interface_elements": {"score": 5, "raw_output": {"summary": "3 static + 1 dynamic"}},
    "nfr_scoring": {"score": 8, "raw_output": {"summary": "Security L=5, Quality M=3"}},
    "functional_aggregator": {"score": 20, "raw_output": {"summary": "10 dimensions consolidated"}},
    "complexity_maturity": {"score": 3, "raw_output": {"classification": "Meets Basic Standards"}},
    "invest_maturity": {"score": 4, "raw_output": {"classification": "Demonstrates Good Maturity"}}
  }
}
```

### Understanding the 13 Dimensions

**Functional Dimensions (D1-D10):**
1. **Business Rules** — Logical rules and their complexity
2. **Interface Elements** — User-facing UI elements (static and dynamic)
3. **Solution Variabilities** — Distinct behavioral paths that converge to the same output
4. **Domain Entities** — Business entities mentioned in the story
5. **New Domain Entities** — Novelty in the domain model (new entities or modified attributes)
6. **Roles & Permissions** — Access control and permission levels
7. **Boundaries** — External system integrations
8. **Background Processes** — Async/scheduled/event-driven processes
9. **Notifications** — Business event notifications
10. **Audits** — Audit trail requirements

**NFR Dimensions (D11-D13):**
11. **Quality Attributes** — Performance, scalability, reliability requirements
12. **Security & Compliance** — Authentication, encryption, compliance frameworks
13. **UX & Accessibility** — WCAG, i18n, responsive design requirements

**Maturity (complementary, not in BCP total):**
- **Complexity Maturity Score (CMS)** — How well the story is defined (0-5)
- **INVEST Maturity Score (IMS)** — Readiness for sprint planning (0-5)

## User Story Format

For optimal results, user stories should include:

1. A clear title
2. User story in the format: "As a [role], I want [feature], so that [benefit]"
3. Acceptance criteria
4. Any additional context or technical notes

Example:
```markdown
# Add Payment Method

As a customer, I want to add a new payment method to my account so that I can use it for future purchases.

## Acceptance Criteria
- User can access the "Add Payment Method" form from account settings
- User can enter credit card details (number, expiry, CVV)
- System validates card details in real-time
- User receives confirmation when card is successfully added
- New payment method appears in the list of saved payment methods

## Technical Notes
- Integration with payment processor API required
- Need to encrypt and securely store payment information
```

## Troubleshooting

### Common Issues

- **API Key Errors**: Ensure your API keys are correctly set in the `.env` file.
- **Missing Dependencies**: Make sure you've installed all dependencies with `pip install -r requirements.txt`.
- **File Path Errors**: Use the correct path to your user story files.

### Debugging

Use the `--log-level DEBUG` flag to get detailed information about the execution process:

```bash
python run_cli.py tests/data/story1.md --log-level DEBUG
```

## Advanced Usage

### Comparing Different Providers

You can compare results between OpenAI and Claude:

```bash
python tests/compare_providers.py tests/data/story1.md
```

### Testing Custom Prompts

If you've modified the prompt templates, you can test them:

```bash
python tests/test_bcp_calculator.py --provider openai
```