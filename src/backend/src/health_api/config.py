"""Runtime settings."""

from typing import Literal, Self

from pydantic import BaseModel, model_validator


class Settings(BaseModel):
    profile: Literal["stub", "local"] = "stub"
    qdrant_url: str | None = None

    @model_validator(mode="after")
    def local_profile_requires_its_settings(self) -> Self:
        if self.profile != "local":
            return self
        if not self.qdrant_url:
            raise ValueError("qdrant_url is required")
        return self
