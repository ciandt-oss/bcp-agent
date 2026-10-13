# BCP Calculator — Troubleshooting Guide

This guide maps the most common environment and network errors reported when setting up and
running bcp-agent to their verified root causes and fixes.

> **Agents:** when a user reports a setup, network, or provider error — `pip install` failures,
> SSL/certificate errors, HTTP redirects to sign-in pages, authentication failures — read this
> document **before** debugging from scratch. Find the matching error below and follow its section.

## Quick Reference

| # | Error message | Root cause | Section |
|---|---------------|------------|---------|
| 1 | `ERROR: No matching distribution found for langchain==1.4.2` | Python older than 3.10 | [1 — Installation failure](#1-installation-failure-no-matching-distribution-found) |
| 2 | `[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain` | Corporate VPN/proxy TLS inspection | [2 — SSL error](#2-ssl-error-self-signed-certificate-in-certificate-chain) |
| 3 | `Redirect response '302 Found' ... /account/sign-in` | Missing or invalid authentication against the Flow gateway | [3 — HTTP 302 redirect](#3-http-302-redirect-to-the-flow-sign-in-page) |
| 4 | Fix applied to `.env` has no effect, or job stuck with an old error | Environment is read once at startup; jobs live in memory | [4 — Changes to `.env` have no effect](#4-changes-to-env-have-no-effect) |

## How errors surface

The HTTP API uses an async job model: `POST /calculate` returns a `job_id`, the calculation runs
in a background task, and `GET /status/{job_id}` reports progress. When the calculation fails,
the job status becomes `failed` and the raw exception text appears in the `error` field of the
status response.

The local API itself is plain HTTP on `127.0.0.1` — there is no TLS involved. An SSL or HTTP
error seen while polling `/status` is therefore almost always the failure of the **background
LLM call**, not of the status request itself.

---

## 1. Installation failure: no matching distribution found

### Symptom

```
ERROR: No matching distribution found for langchain==1.4.2 or no matches found: mcp[cli]
```

Happens during `pip install -r requirements.txt`. Upgrading pip does **not** fix it.

### Root cause

The Python interpreter is older than 3.10 (in the reported case, Python 3.9 — check the path in
`pip3 --version` output). `langchain==1.4.2` (and other pinned dependencies) only publish wheels
for Python >= 3.10, so pip finds no compatible distribution and reports the error above.

The message is misleading: it suggests a connectivity or index problem, but it means "no wheel
exists for your interpreter". Note that `pip install -r requirements.txt` does **not** enforce
the `python_requires=">=3.10"` declared in `setup.py` — that check only applies when installing
the package itself (`pip install bcp-calculator`), so the version mismatch surfaces as this
generic distribution error.

### Diagnosis

```bash
python3 --version    # must print 3.10 or higher
pip3 --version       # the interpreter path in this output is the one pip will use
```

### Solution

Install Python 3.10+ (Homebrew, python.org installer, or pyenv), then create the virtual
environment with that specific interpreter — `python3` may still point to the old version:

```bash
# Example with Python 3.12 (adjust to the version you installed)
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 2. SSL error: self-signed certificate in certificate chain

### Symptom

```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in
certificate chain (_ssl.c:1017)
```

Seen in the `error` field of a failed job (`GET /status/{job_id}`) or in CLI output. It happens
when a corporate VPN is **active**.

### Root cause

A corporate VPN or security proxy (Zscaler-style TLS inspection) re-signs all HTTPS traffic with
the company's internal root CA. Python does not use the operating system trust store (e.g. the
macOS Keychain) by default — HTTP clients in this project validate against the `certifi` bundle
(`httpx` in `src/bcp/simple_llm_provider.py`, `requests` in `src/bcp/llm_providers.py`) — so the
corporate CA is unknown to Python and verification fails.

### Solution A — trust the corporate CA (VPN stays active)

1. Obtain the corporate root CA certificate: export it from Keychain Access on macOS (find the
   corporate/Zscaler root CA → File → Export Items → `.pem` format), or request the `.pem` file
   from your IT team.
2. Build a combined bundle (public CAs + corporate CA). The corporate CA alone would break every
   other HTTPS destination:

   ```bash
   mkdir -p ~/.certs
   cat "$(python -m certifi)" ~/Downloads/corp-root-ca.pem > ~/.certs/corp-bundle.pem
   ```

3. Export **both** variables and start the application from the same shell — background tasks
   inherit the environment of the process that started them:

   ```bash
   export SSL_CERT_FILE="$HOME/.certs/corp-bundle.pem"
   export REQUESTS_CA_BUNDLE="$HOME/.certs/corp-bundle.pem"
   source .venv/bin/activate
   python run_api_server.py
   ```

   Two variables are needed because the project uses two HTTP clients: `httpx` reads
   `SSL_CERT_FILE` and `requests` reads `REQUESTS_CA_BUNDLE`.

4. Verify before re-submitting a job — an HTTP status code means TLS passed (401 without an API
   key is expected); an SSL error means it is still broken:

   ```bash
   python -c "import httpx; print(httpx.get('https://api.openai.com/v1/models').status_code)"
   ```

### Solution B — disconnect the VPN

If the endpoints you need are reachable without the VPN, disconnecting it removes the TLS
interception and public certificates validate normally. This is the quickest unblock, at the
cost of losing access to internal-only gateways.

### Related variant

`certificate verify failed: unable to get local issuer certificate` (without "self-signed")
on a Python installed from python.org installers means the interpreter is missing its root
certificate bundle entirely — run the `Install Certificates.command` script bundled inside the
`/Applications/Python 3.x/` folder, then retry.

---

## 3. HTTP 302 redirect to the Flow sign-in page

### Symptom

```
Redirect response '302 Found' for url 'https://flow.ciandt.com/flow-llm-proxy/v1/chat/completions'
Redirect location: 'https://flow.ciandt.com/account/sign-in?sourceUrl=...'
```

Seen in the `error` field of a failed job. Typically appears **after** the SSL error is solved
(the request now reaches the gateway).

### Root cause

The Flow gateway received the request without valid credentials and responded as it would to an
unauthenticated browser: a 302 redirect to the HTML sign-in page. The HTTP client correctly
refuses to follow the redirect (the response would be HTML, not JSON), and reports it as an
error. This is an authentication problem, not a network problem — do not try to "follow" the
redirect.

Two common paths lead here:

1. **Wrong provider for the gateway.** The job ran with the default `openai` provider while
   `OPENAI_BASE_URL` points to the Flow gateway. `SimpleLLMProvider`
   (`src/bcp/simple_llm_provider.py`) only sends an `Authorization` header when the API key looks
   real (see `PLACEHOLDER_KEYS` / `_should_send_auth()`) — with an empty or placeholder key,
   **no authentication header is sent at all**, and it never sends the `FlowTenant` header the
   gateway expects.
2. **Expired or missing JWT with the correct provider.** The `flow-openai` provider sends
   `Authorization: Bearer <JWT>`, but JWTs expire — an expired token produces the same redirect.

### Diagnosis

- Check which provider the job used (default is `openai` — see `StoryRequest.provider` in
  `src/api/models.py`).
- Check the redirect URL: the `sourceTenant` query parameter shows which tenant the gateway
  resolved. If it does not match your team's tenant, `FLOW_TENANT` in `.env` needs adjusting.

### Solution

Use the provider designed for the Flow gateway — `flow-openai` — which sends the JWT bearer
token and the `FlowTenant` header (`src/bcp/llm_providers.py`, `FlowLiteLLMChatModel`):

1. Configure `.env` following `.env.flow.example`:

   ```dotenv
   FLOW_LLM_LITE_HOST=https://flow.ciandt.com/flow-litellm
   FLOW_LITELLM_TOKEN_JWT=<valid JWT>
   FLOW_TENANT=<your team's tenant>
   ```

   Confirm `FLOW_LLM_LITE_HOST` with your team — the gateway path must match the host your team
   documented (e.g. `flow-litellm` vs `flow-llm-proxy`).

2. Submit jobs with that provider:

   ```bash
   # CLI
   python run_cli.py story.md --provider flow-openai

   # HTTP API
   curl -X POST http://127.0.0.1:8000/calculate \
     -H "Content-Type: application/json" \
     -d '{"content": "<story text>", "provider": "flow-openai"}'
   ```

3. If the JWT is expired, renew it through your team's Flow OAuth credentials and update
   `FLOW_LITELLM_TOKEN_JWT`.

4. Restart the API server after changing `.env` (see section 4).

If a valid token still yields a 302, re-check the tenant (`sourceTenant` in the redirect) and
the gateway host with your team.

---

## 4. Changes to `.env` have no effect

### Symptom

You fixed `.env` (or exported CA variables), but the same job keeps failing with the old error —
or the error message does not change at all.

### Root cause

Two behaviors combine here:

1. **Environment is read at startup.** `load_dotenv()` runs once when the server (or CLI)
   starts; background calculation tasks inherit that environment. Editing `.env` afterwards
   changes nothing for the running process.
2. **Jobs live in memory.** The API server stores jobs in an in-memory dict
   (`src/api/server.py`). Restarting the server loses every pending and completed job, and
   failed jobs are never retried automatically.

### Solution

1. Stop the running server.
2. Apply your fix (`.env` edit or exported variables) in the shell you will use to start it.
3. Start the server again:

   ```bash
   source .venv/bin/activate
   python run_api_server.py
   ```

4. Submit a **new** job — old `job_id`s no longer exist after a restart.

---

## Pre-flight checklist

Run through this list before reporting a new environment issue:

- [ ] `python3 --version` prints 3.10 or higher, and the venv was created with that interpreter
- [ ] The venv is active (`which python` points inside `.venv/`)
- [ ] `.env` matches the chosen provider (see the `.env.*.example` templates)
- [ ] The API server was (re)started **after** the last `.env` change
- [ ] VPN state matches the endpoints in use: internal gateways need the VPN plus a trusted
      corporate CA (section 2); public endpoints work without it
- [ ] For Flow gateway jobs: provider is `flow-openai`, the JWT is fresh, and the tenant matches
      your team
