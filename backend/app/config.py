from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "Azure RAG OpenAI Assistant"

    azure_openai_endpoint: str = Field(default="", alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str = Field(default="", alias="AZURE_OPENAI_API_KEY")
    azure_openai_api_version: str = Field(default="2024-02-01", alias="AZURE_OPENAI_API_VERSION")
    azure_openai_chat_deployment: str = Field(default="", alias="AZURE_OPENAI_CHAT_DEPLOYMENT")

    azure_search_endpoint: str = Field(default="", alias="AZURE_SEARCH_ENDPOINT")
    azure_search_admin_key: str = Field(default="", alias="AZURE_SEARCH_ADMIN_KEY")
    azure_search_index_name: str = Field(default="rag-docs-index", alias="AZURE_SEARCH_INDEX_NAME")
    rag_top_k: int = Field(default=5, alias="RAG_TOP_K")

    system_prompt: str = Field(default="You are a helpful assistant.", alias="SYSTEM_PROMPT")

    frontend_dir: Path = Path(__file__).resolve().parents[2] / "frontend"

    model_config = SettingsConfigDict(
        env_file=(Path(__file__).resolve().parents[2] / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
