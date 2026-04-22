from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import Settings, get_settings
from app.schemas import ChatRequest, ChatResponse
from app.services.rag_chat import RagChatService


@lru_cache(maxsize=1)
def get_service() -> RagChatService:
    return RagChatService(get_settings())


settings = get_settings()
app = FastAPI(title=settings.project_name)
static_root = Path(settings.frontend_dir)
app.mount("/static", StaticFiles(directory=str(static_root)), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(static_root / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.project_name}


@app.get("/api/config")
def config() -> dict[str, str]:
    return {
        "openAiEndpoint": settings.azure_openai_endpoint,
        "chatDeployment": settings.azure_openai_chat_deployment,
        "embeddingDeployment": settings.azure_openai_embedding_deployment,
        "searchEndpoint": settings.azure_search_endpoint,
        "searchIndexName": settings.azure_search_index_name,
        "searchVectorField": settings.azure_search_vector_field,
        "retrievalMode": settings.rag_retrieval_mode,
        "ragTopK": str(settings.rag_top_k),
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    try:
        answer = get_service().chat(payload.question, payload.history, payload.temperature)
        return ChatResponse(answer=answer)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/rag/chat", response_model=ChatResponse)
def rag_chat(payload: ChatRequest) -> ChatResponse:
    try:
        answer, sources, docs = get_service().rag_chat(payload.question, payload.history, payload.temperature)
        return ChatResponse(answer=answer, sources=sources, docs=docs)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
