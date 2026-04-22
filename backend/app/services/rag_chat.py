from __future__ import annotations

from collections.abc import Iterable

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import AzureOpenAI

from app.config import Settings
from app.schemas import Message


class RagChatService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
        )

    def chat(self, question: str, history: list[Message], temperature: float) -> str:
        messages = self._build_messages(question, history)
        response = self.client.chat.completions.create(
            model=self.settings.azure_openai_chat_deployment,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content or "No answer returned."

    def rag_chat(self, question: str, history: list[Message], temperature: float) -> tuple[str, list[str], list[dict]]:
        docs = self.search_documents(question)
        context = self._build_context(docs)
        rag_system_prompt = (
            f"{self.settings.system_prompt}\n\n"
            "You have access to retrieved documents from the knowledge base. "
            "Combine the retrieved context with your own knowledge to give a comprehensive answer. "
            "Always cite the relevant documents when you use their information.\n\n"
            f"Retrieved Context:\n{context}"
        )

        messages: list[dict[str, str]] = [{"role": "system", "content": rag_system_prompt}]
        for item in history:
            messages.append({"role": item.role, "content": item.content})
        messages.append({"role": "user", "content": question})

        response = self.client.chat.completions.create(
            model=self.settings.azure_openai_chat_deployment,
            messages=messages,
            temperature=temperature,
        )

        sources = [doc.get("source", "unknown") for doc in docs]
        return response.choices[0].message.content or "No answer returned.", sources, docs

    def search_documents(self, query: str) -> list[dict]:
        search_client = SearchClient(
            endpoint=self.settings.azure_search_endpoint,
            index_name=self.settings.azure_search_index_name,
            credential=AzureKeyCredential(self.settings.azure_search_admin_key),
        )

        
        
        mode = (self.settings.rag_retrieval_mode or "hybrid").strip().lower()
        if mode not in {"text", "vector", "hybrid"}:
            mode = "hybrid"

        vector_query = self._build_vector_query(query)
        if mode in {"vector", "hybrid"} and vector_query is not None:
            search_text = query if mode == "hybrid" else "*"
            results = search_client.search(
                search_text=search_text,
                vector_queries=[vector_query],
                top=self.settings.rag_top_k,
            )
        else:
            results = search_client.search(search_text=query, top=self.settings.rag_top_k)

        return [self._to_doc(result) for result in results]

    def _build_vector_query(self, query: str) -> VectorizedQuery | None:
        vector_field = (self.settings.azure_search_vector_field or "").strip()
        embedding_deployment = (self.settings.azure_openai_embedding_deployment or "").strip()
        if not vector_field or not embedding_deployment:
            return None

        embedding_response = self.client.embeddings.create(
            model=embedding_deployment,
            input=query,
        )
        embedding = embedding_response.data[0].embedding
        return VectorizedQuery(
            vector=embedding,
            k_nearest_neighbors=self.settings.rag_top_k,
            fields=vector_field,
        )

    def _to_doc(self, item: object) -> dict:
        doc = dict(item)
        title_field = self.settings.azure_search_title_field
        content_field = self.settings.azure_search_content_field
        source_field = self.settings.azure_search_source_field

        # Include all fields from the index document
        result = {k: v for k, v in doc.items() if not k.startswith("@") and not isinstance(v, list)}
        result["title"] = doc.get(title_field, doc.get("title", "Untitled"))
        result["content"] = doc.get(content_field, doc.get("content", ""))
        result["source"] = doc.get(source_field, doc.get("source", "unknown"))
        return result

    @staticmethod
    def _build_context(documents: Iterable[dict]) -> str:
        lines: list[str] = []
        for i, doc in enumerate(documents, start=1):
            lines.append(f"[{i}] Title: {doc.get('title', 'Untitled')}")
            lines.append(f"[{i}] Source: {doc.get('source', 'unknown')}")
            lines.append(f"[{i}] Content: {doc.get('content', '')}")
            lines.append("")
        return "\n".join(lines).strip() or "No relevant documents found."

    def _build_messages(self, question: str, history: list[Message]) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = [{"role": "system", "content": self.settings.system_prompt}]
        for item in history:
            messages.append({"role": item.role, "content": item.content})
        messages.append({"role": "user", "content": question})
        return messages
