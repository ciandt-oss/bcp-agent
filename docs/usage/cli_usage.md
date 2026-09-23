# CLI Usage Guide for BCP Calculator

This guide explains how to use the BCP Calculator as a command-line tool.

## Prerequisites

Before using the CLI, make sure you have:

1. Installed all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your environment variables:
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file to add your API keys for the providers you want to use (OpenAI and/or Anthropic).

## Basic Usage

The basic syntax for using the BCP Calculator CLI is:

```bash
python run_cli.py <story_file> [OPTIONS]
```

Where:
- `<story_file>` is the path to the markdown file containing your user story

## Options

The CLI supports the following options:

| Option | Description | Default |
|--------|-------------|---------|
| `--log-level` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | INFO |
| `--output-file` | Path to save the output results | None (print to stdout) |
| `--provider` | LLM provider to use (openai, claude, flow-openai, flow-bedrock) | openai |
| `--max-workers` | Maximum parallel threads per wave | 5 |
| `--format` | Output format (text or json) | json |

## Examples

### Basic Example

Process a user story with the default provider (OpenAI):

```bash
python run_cli.py tests/data/story1.md
```

### Using Different Providers

Process with OpenAI (explicitly):

```bash
python run_cli.py tests/data/story1.md --provider openai
```

Process with Claude:

```bash
python run_cli.py tests/data/story1.md --provider claude
```

### Saving Results

Save the results to a JSON file:

```bash
python run_cli.py tests/data/story1.md --output-file results.json
```

Save results in text format:

```bash
python run_cli.py tests/data/story1.md --format text --output-file results.txt
```

### Detailed Logging

Run with detailed debug logs:

```bash
python run_cli.py tests/data/story1.md --log-level DEBUG
```

### Complete Example

Process a story with Claude, save as text with detailed logs:

```bash
python run_cli.py tests/data/story1.md --provider claude --format text --output-file claude_results.txt --log-level DEBUG
```

## Understanding the Output

The output includes:

- **BCP Total**: Sum of all functional dimension scores + NFR score
- **Breakdown**: Individual scores for all 11 dimensions (10 functional + 1 NFR)
- **Maturity**: Complexity Maturity Score (CMS) and INVEST Maturity Score (IMS)
- **Cells**: Detailed results from each of the 14 pipeline cells

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
    "functional_solution_variabilities": {"score": 1, "raw_output": {"summary": "No variabilities"}},
    "functional_domain_entities": {"score": 2, "raw_output": {"summary": "3 entities"}},
    "functional_new_domain_entities": {"score": 0, "raw_output": {"summary": "No new entities"}},
    "functional_roles_permissions": {"score": 2, "raw_output": {"summary": "Basic permissions"}},
    "functional_boundaries": {"score": 3, "raw_output": {"summary": "1 boundary: Payment gateway"}},
    "functional_background_processes": {"score": 0, "raw_output": {"summary": "No background processes"}},
    "functional_notifications": {"score": 0, "raw_output": {"summary": "No notifications"}},
    "functional_audits": {"score": 0, "raw_output": {"summary": "No audits"}},
    "nfr_scoring": {"score": 8, "raw_output": {"summary": "Security L=5, Quality M=3"}},
    "functional_aggregator": {"score": 20, "raw_output": {"summary": "10 dimensions consolidated"}},
    "complexity_maturity": {"score": 3, "raw_output": {"classification": "Meets Basic Standards"}},
    "invest_maturity": {"score": 4, "raw_output": {"classification": "Demonstrates Good Maturity"}}
  }
}
```

### Sample Text Output

```
=== BCP 13 DIMENSIONS — RESULTS ===
Story: User Story: Add Payment Method

=== DIMENSION BREAKDOWN ===
  business_rules: 7
  interface_elements: 5
  solution_variabilities: 1
  domain_entities: 2
  new_domain_entities: 0
  roles_permissions: 2
  boundaries: 3
  background_processes: 0
  notifications: 0
  audits: 0
  nfr: 8

=== MATURITY ===
  Complexity Maturity: 3
  INVEST Maturity: 4

=== CELL DETAILS ===
  functional_business_rules: score=7
  functional_interface_elements: score=5
  functional_solution_variabilities: score=1
  functional_domain_entities: score=2
  functional_new_domain_entities: score=0
  functional_roles_permissions: score=2
  functional_boundaries: score=3
  functional_background_processes: score=0
  functional_notifications: score=0
  functional_audits: score=0
  nfr_scoring: score=8
  functional_aggregator: score=20
  complexity_maturity: score=3
  invest_maturity: score=4

=== TOTAL BCP ===
  Total: 28
```

## Troubleshooting

### Common Issues

1. **API Key Issues**:
   - Ensure the appropriate API keys are properly set in `.env`
   - Check that you have access to the LLM provider you're trying to use

2. **File Path Errors**:
   - Use absolute paths if experiencing issues with relative paths
   - Ensure the story file exists and has the correct permissions

3. **Provider Issues**:
   - If a provider is not working, try switching to a different provider
   - Check the API key and network connection