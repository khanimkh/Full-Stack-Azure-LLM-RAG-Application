# Azure RAG OpenAI Assistant

A complete full-stack sample for Azure OpenAI + Retrieval Augmented Generation (RAG) with Azure AI Search.

This project includes:

- Chat mode: ask a question directly to an Azure OpenAI deployment.
- RAG mode: retrieve context from indexed Azure AI Search documents, then answer with Azure OpenAI.
- Frontend + backend in one container.
- GitHub Actions pipeline for validation, security scanning, image build, and Azure Container Apps deployment.

## Project layout

- `backend/app/`: FastAPI API server and Azure integration.
- `frontend/`: Static web UI for chat and RAG chat.
- `infra/scripts/`: Deployment, traffic splitting, alert, and profile scripts.
- `infra/environments/`: Staging and production profile values.
- `tests/`: Basic tests for core helper behavior.

## Environment setup

1. Copy `.env.example` to `.env`.
2. Fill in Azure values.

```powershell
copy .env.example .env
```

Important variables:

- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_CHAT_DEPLOYMENT`
- `AZURE_OPENAI_API_VERSION`
- `AZURE_SEARCH_ENDPOINT`
- `AZURE_SEARCH_ADMIN_KEY`
- `AZURE_SEARCH_INDEX_NAME`

## Run with Docker

```powershell
docker compose up --build
```

Open `http://localhost:8010`.

## Run locally without Docker

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --app-dir backend --reload --port 8010
```

## API endpoints

- `GET /api/health`
- `GET /api/config`
- `POST /api/chat`
- `POST /api/rag/chat`
- `POST /api/rag/index/init`
- `POST /api/rag/index/load-sample`

## GitHub Actions and Azure Container Apps

Workflow file:

- `.github/workflows/azure-rag-openai-assistant.yml`

Pipeline stages:

1. Validate + tests
2. Security scans (`pip-audit`, `bandit`, `trivy`)
3. Build and push container image to GHCR
4. Deploy staging
5. Deploy production
6. Configure traffic split and alerts

Required secret:

- `AZURE_CREDENTIALS`

Recommended environment variables in GitHub environments (`staging` and `production`):

- `AZURE_SUBSCRIPTION_ID`
- `RESOURCE_GROUP`
- `CONTAINER_APP_NAME`
- `SEARCH_ENDPOINT`
- `SEARCH_INDEX_NAME`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_CHAT_DEPLOYMENT`
