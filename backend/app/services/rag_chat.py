from __future__ import annotations

from collections.abc import Iterable

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchFieldDataType, SearchIndex, SearchableField, SimpleField
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

    def rag_chat(self, question: str, history: list[Message], temperature: float) -> tuple[str, list[str]]:
        docs = self.search_documents(question)
        context = self._build_context(docs)
        rag_system_prompt = (
            f"{self.settings.system_prompt}\n\n"
            "Use only the provided context when possible. "
            "If context is insufficient, clearly say what is missing.\n\n"
            f"Context:\n{context}"
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
        return response.choices[0].message.content or "No answer returned.", sources

    def initialize_index(self, index_name: str | None = None) -> dict:
        target = index_name or self.settings.azure_search_index_name
        index_client = SearchIndexClient(
            endpoint=self.settings.azure_search_endpoint,
            credential=AzureKeyCredential(self.settings.azure_search_admin_key),
        )
        index = SearchIndex(
            name=target,
            fields=[
                SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
                SearchableField(name="title", type=SearchFieldDataType.String),
                SearchableField(name="content", type=SearchFieldDataType.String),
                SimpleField(name="source", type=SearchFieldDataType.String, filterable=True),
            ],
        )
        result = index_client.create_or_update_index(index)
        return {"message": f"Index '{result.name}' is ready."}

    def load_sample_documents(self, index_name: str | None = None) -> dict:
        target = index_name or self.settings.azure_search_index_name
        search_client = SearchClient(
            endpoint=self.settings.azure_search_endpoint,
            index_name=target,
            credential=AzureKeyCredential(self.settings.azure_search_admin_key),
        )
        docs = [
            {
                "id": "doc-001",
                "title": "Azure RAG Architecture",
                "content": "A RAG system retrieves relevant indexed content from Azure AI Search and augments prompts sent to Azure OpenAI.",
                "source": "architecture-notes.md",
            },
            {
                "id": "doc-002",
                "title": "Deployment Practice",
                "content": "Use staging and production environments with canary traffic splitting for safer releases.",
                "source": "deployment-guide.md",
            },
            {
                "id": "doc-003",
                "title": "Security",
                "content": "Run dependency and static code scans in CI before building and deploying images.",
                "source": "security-playbook.md",
            },
        ]
        result = search_client.upload_documents(docs)
        succeeded = sum(1 for item in result if item.succeeded)
        return {"message": f"Uploaded {succeeded} document(s) to '{target}'."}

    def search_documents(self, query: str) -> list[dict]:
        search_client = SearchClient(
            endpoint=self.settings.azure_search_endpoint,
            index_name=self.settings.azure_search_index_name,
            credential=AzureKeyCredential(self.settings.azure_search_admin_key),
        )
        results = search_client.search(search_text=query, top=self.settings.rag_top_k)
        return [self._to_doc(result) for result in results]

    @staticmethod
    def _to_doc(item: object) -> dict:
        doc = dict(item)
        return {
            "title": doc.get("title", "Untitled"),
            "content": doc.get("content", ""),
            "source": doc.get("source", "unknown"),
        }

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
