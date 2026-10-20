"""Runtime settings."""

from typing import Literal

from pydantic import BaseModel


class Settings(BaseModel):
    profile: Literal["stub", "local"] = "stub"
