# Architecture

The backend is a FastAPI service that exposes standard chat and RAG chat APIs.

RAG flow:

1. Query arrives at `/api/rag/chat`.
2. Backend searches Azure AI Search index for relevant documents.
3. Retrieved snippets are assembled into context.
4. Context + user question are sent to Azure OpenAI chat deployment.
5. Response and source list are returned to the frontend.
