# HTTP API Usage Guide for BCP Calculator

This guide explains how to use the BCP Calculator as an HTTP API service.

## Prerequisites

Before using the HTTP API, make sure you have:

1. Installed all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your environment variables:
   ```bash
   cp .env.flow.example .env
   ```
   Then edit the `.env` file to add your API keys for the providers you want to use (OpenAI and/or Anthropic).

## Starting the API Server

You can start the API server using the provided script:

```bash
python run_api_server.py [OPTIONS]
```

Available options:
- `--host`: Host to bind the server to (default: 127.0.0.1)
- `--port`: Port to bind the server to (default: 8000)
- `--reload`: Enable auto-reload on code changes (development mode)

You can also configure the server using environment variables in the `.env` file:
```
API_HOST=127.0.0.1
API_PORT=8000
```

Once started, the API server will be available at `http://host:port/`.

## API Endpoints

### Root Endpoint

- **URL**: `/`
- **Method**: `GET`
- **Description**: Returns basic information about the API

**Example Response**:
```json
{
  "name": "BCP Calculator API",
  "version": "1.0.0",
  "description": "API for calculating Business Complexity Points (BCP) of user stories"
}
```

### Calculate BCP

- **URL**: `/calculate`
- **Method**: `POST`
- **Description**: Start a BCP calculation job

**Request Body**:
```json
{
  "content": "# User Story\n\nAs a user, I want to...",
  "provider": "openai"
}
```

Parameters:
- `content`: The content of the user story (required)
- `provider`: The LLM provider to use (`openai` or `claude`, default: `openai`)

**Response**:
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Get Job Status

- **URL**: `/status/{job_id}`
- **Method**: `GET`
- **Description**: Get the status and results of a BCP calculation job

**Path Parameters**:
- `job_id`: The ID of the job to get status for

**Response**:
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "result": {
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
      "functional_business_rules": {"score": 7, "raw_output": {"summary": "3 rules identified", "items": ["Rule 1 — Score: 3", "Rule 2 — Score: 2", "Rule 3 — Score: 2"], "scores_extracted": [3, 2, 2]}},
      "functional_interface_elements": {"score": 5, "raw_output": {"summary": "3 static + 1 dynamic (existing context)", "context": "existing", "static_elements": ["Payment form", "Card number field", "Expiry field"], "dynamic_elements": ["Card type dropdown"], "static_weight": 2, "dynamic_weight": 5}},
      "functional_solution_variabilities": {"score": 1, "raw_output": {"dimension_solution_variabilities": 1, "classification": "XS", "summary": "No explicit variabilities"}},
      "functional_domain_entities": {"score": 2, "raw_output": {"dimension_domain_entities": 2, "entity_count": 3, "classification": "S", "summary": "3 entities: Payment, Card, Account"}},
      "functional_new_domain_entities": {"score": 0, "raw_output": {"block_a_modified": [], "block_b_new": [], "relevant": false, "classification": null}},
      "functional_roles_permissions": {"score": 2, "raw_output": {"dimension_roles_permissions": 2, "classification": "S", "summary": "User role with basic permissions"}},
      "functional_boundaries": {"score": 3, "raw_output": {"summary": "1 boundary: Payment gateway (M)", "items": ["Payment gateway -> M (3)"], "scores_extracted": [3]}},
      "functional_background_processes": {"score": 0, "raw_output": {"dimension_background_processes": 0, "classification": "XS", "summary": "No background processes"}},
      "functional_notifications": {"score": 0, "raw_output": {"notification_events": [], "summary": "No notification events"}},
      "functional_audits": {"score": 0, "raw_output": {"audited_entities": [], "summary": "No audit requirements"}},
      "nfr_scoring": {"score": 8, "raw_output": {"dimension_quality_attributes": 3, "dimension_security_compliance": 5, "dimension_user_experience_accessibility": 0, "classification_quality_attributes": "M", "classification_security_compliance": "L", "classification_user_experience_accessibility": null}},
      "functional_aggregator": {"score": 20, "raw_output": {"score": 20, "total_bcp_functional": 20, "dim_business_rules": 7, "dim_interface_elements": 5, "dim_solution_variabilities": 1, "dim_domain_entities": 2, "dim_new_domain_entities": 0, "dim_roles_permissions": 2, "dim_boundaries": 3, "dim_background_processes": 0, "dim_notifications": 0, "dim_audits": 0}},
      "complexity_maturity": {"score": 3, "raw_output": {"score": 3, "classification": "Meets Basic Standards", "complexity_breakdown": {"clarity": 3, "completeness": 3, "explicit_definitions": 2, "testability": 4, "business_value": 4}, "gaps": ["Payment validation rules not fully specified", "Error handling for failed payments undefined"]}},
      "invest_maturity": {"score": 4, "raw_output": {"score": 4, "classification": "Demonstrates Good Maturity", "invest_breakdown": {"independent": 4, "negotiable": 4, "valuable": 5, "estimable": 3, "small": 4, "testable": 4}, "gaps": ["Payment gateway integration details not specified"]}}
    }
  }
}
```

The `status` field can be one of:
- `pending`: The job is waiting to be processed
- `processing`: The job is being processed
- `completed`: The job has been completed successfully
- `failed`: The job has failed

If the job has failed, the response will include an `error` field with details about the error.

## Using the API with curl

### Start a Calculation

```bash
curl -X POST http://localhost:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# User Story: View Account Balance\n\nAs a bank customer, I want to view my account balance, so that I can keep track of my finances.\n\n## Acceptance Criteria:\n1. Customer can log in and see their account dashboard\n2. Dashboard displays current balance for all accounts\n3. Balance is updated in real-time when transactions occur\n4. Customer can click on an account to view detailed transaction history",
    "provider": "openai"
  }'
```

This will return a response with a job ID:
```json
{"job_id": "123e4567-e89b-12d3-a456-426614174000"}
```

### Check Job Status

```bash
curl http://localhost:8000/status/123e4567-e89b-12d3-a456-426614174000
```

## Using the API with Python

You can use the `requests` library in Python to interact with the API:

```python
import requests
import time
import json

# API base URL
base_url = "http://localhost:8000"

# User story content
story_content = """
# User Story: View Account Balance

As a bank customer, I want to view my account balance, so that I can keep track of my finances.

## Acceptance Criteria:
1. Customer can log in and see their account dashboard
2. Dashboard displays current balance for all accounts
3. Balance is updated in real-time when transactions occur
4. Customer can click on an account to view detailed transaction history
"""

# Start BCP calculation
response = requests.post(
    f"{base_url}/calculate",
    json={
        "content": story_content,
        "provider": "openai"
    }
)
job_id = response.json()["job_id"]
print(f"Job ID: {job_id}")

# Poll for results
while True:
    response = requests.get(f"{base_url}/status/{job_id}")
    status_data = response.json()
    
    if status_data["status"] == "completed":
        print("BCP calculation completed!")
        result = status_data["result"]
        print(f"Total BCP: {result['total_bcp']}")
        print("Breakdown:")
        for dimension, points in result["breakdown"].items():
            print(f"  {dimension}: {points}")
        print(f"Complexity Maturity: {result['maturity']['complexity']}/5")
        print(f"INVEST Maturity: {result['maturity']['invest']}/5")
        break
    elif status_data["status"] == "failed":
        print(f"BCP calculation failed: {status_data.get('error', 'Unknown error')}")
        break
    else:
        print(f"Status: {status_data['status']}. Waiting...")
        time.sleep(2)
```

## API Documentation

The API includes automatic OpenAPI documentation using FastAPI:

- **API Documentation**: `http://localhost:8000/docs`
- **Alternative Documentation**: `http://localhost:8000/redoc`

These pages provide interactive documentation that allows you to try out the API directly from your browser.

## Troubleshooting

### Common Issues

1. **API Not Starting**:
   - Check that the port is not already in use by another application
   - Ensure you have all the required dependencies installed

2. **Provider Errors**:
   - Ensure the appropriate API keys are properly set in `.env`
   - Check that you have access to the LLM provider you're trying to use

3. **Job Not Completing**:
   - Long stories or high server load might cause jobs to take longer to complete
   - Check the server logs for any error messages