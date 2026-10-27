import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

_FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
_DEPENDENCIES = {
    "@eslint/js",
    "@fontsource-variable/geist",
    "@hookform/resolvers",
    "@tailwindcss/vite",
    "@tanstack/react-query",
    "@tanstack/react-query-devtools",
    "@testing-library/dom",
    "@testing-library/jest-dom",
    "@testing-library/react",
    "@testing-library/user-event",
    "@types/node",
    "@types/react",
    "@types/react-dom",
    "@vitejs/plugin-react",
    "@vitest/coverage-v8",
    "class-variance-authority",
    "cn",
    "eslint",
    "eslint-config-prettier",
    "eslint-plugin-oxlint",
    "eslint-plugin-react-hooks",
    "globals",
    "husky",
    "jsdom",
    "lint-staged",
    "lucide-react",
    "msw",
    "next-themes",
    "oxlint",
    "prettier",
    "prettier-plugin-tailwindcss",
    "radix-ui",
    "react",
    "react-dom",
    "react-hook-form",
    "react-markdown",
    "react-router",
    "remark-gfm",
    "shadcn",
    "sonner",
    "tailwindcss",
    "tw-animate-css",
    "typescript",
    "typescript-eslint",
    "vite",
    "vitest",
    "zod",
}


def test_the_web_image_should_proxy_the_api() -> None:
    # Given
    dockerfile = (_FRONTEND / "Dockerfile").read_text()
    nginx = (_FRONTEND / "nginx.conf").read_text()
    package = json.loads((_FRONTEND / "package.json").read_text())

    # When
    names = set(package["dependencies"]) | set(package["devDependencies"])

    # Then
    assert "npm run build" in dockerfile
    for path in ("/documents", "/chat", "/health"):
        assert path in nginx
    assert "http://api:8000" in nginx
    assert names == _DEPENDENCIES
