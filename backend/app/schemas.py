from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(pattern="^(system|user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    question: str
    history: list[Message] = Field(default_factory=list)
    temperature: float = Field(default=0.2, ge=0, le=2)


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)
    docs: list[dict] = Field(default_factory=list)
