"""Runtime settings."""

from typing import Literal, Self

from pydantic import BaseModel, model_validator


class Settings(BaseModel):
    profile: Literal["stub", "local"] = "stub"
    qdrant_url: str | None = None
    ollama_base_url: str | None = None
    ollama_chat_model: str | None = None

    @model_validator(mode="after")
    def local_profile_requires_its_settings(self) -> Self:
        if self.profile != "local":
            return self
        missing: list[str] = []
        if not self.qdrant_url:
            missing.append("qdrant_url")
        if not self.ollama_base_url:
            missing.append("ollama_base_url")
        if not self.ollama_chat_model:
            missing.append("ollama_chat_model")
        if missing:
            raise ValueError(f"{', '.join(missing)} is required")
        return self
