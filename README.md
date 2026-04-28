# Azure RAG OpenAI Assistant

A complete full-stack sample for Azure OpenAI + Retrieval Augmented Generation (RAG) with Azure AI Search.

This project includes:

- Chat mode: ask a question directly to an Azure OpenAI deployment.
- RAG mode: retrieve context from indexed Azure AI Search documents, then answer with Azure OpenAI.
- Frontend + backend in one container.
- GitHub Actions pipeline for image build/push to ACR and deployment to Azure Container Apps.

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
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` (required for vector/hybrid vector part)
- `AZURE_OPENAI_API_VERSION`
- `AZURE_SEARCH_ENDPOINT`
- `AZURE_SEARCH_ADMIN_KEY`
- `AZURE_SEARCH_INDEX_NAME`
- `AZURE_SEARCH_CONTENT_FIELD`
- `AZURE_SEARCH_TITLE_FIELD`
- `AZURE_SEARCH_SOURCE_FIELD`
- `AZURE_SEARCH_VECTOR_FIELD`
- `RAG_RETRIEVAL_MODE` (`text`, `vector`, or `hybrid`)
- `RAG_TOP_K`

## Run with Docker

```powershell
docker compose up --build
```

Open `http://localhost:8010`.

Stop:

```powershell
docker compose down
```

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

## How RAG works in this app

1. Frontend sends question to `POST /api/rag/chat`.
2. Backend queries Azure AI Search for top documents.
3. Retrieved context is added to the system prompt.
4. Azure OpenAI generates the final answer.
5. API returns `answer`, `sources`, and `docs` for UI rendering.

Vector retrieval requires both:
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`
- `AZURE_SEARCH_VECTOR_FIELD`

## GitHub Actions and Azure Container Apps (Current Workflow)

Workflow file:

- `.github/workflows/azure-rag-openai-assistant.yml`

Current pipeline stages:

1. Checkout repository
2. Login to Azure using `AZURE_CREDENTIALS`
3. Login to Azure Container Registry (ACR)
4. Build and tag image (`<acr>.azurecr.io/<image>:sha` and `latest`)
5. Push image to ACR
6. Update Azure Container App image

Required secret:

- `AZURE_CREDENTIALS`

Configured workflow environment values:

- `ACR_NAME`
- `RESOURCE_GROUP`
- `CONTAINER_APP_NAME`
- `IMAGE_NAME`

## Note on infra scripts

The `infra/scripts/` and `infra/environments/` files are available, but the current GitHub workflow does not call them directly.
If you want staged deployments, traffic split, and alert setup from CI/CD, wire these scripts into the workflow:

1. `infra/scripts/export_env_config.py`
2. `infra/scripts/deploy_containerapp.sh`
3. `infra/scripts/configure_traffic.sh`
4. `infra/scripts/configure_alerts.sh`
