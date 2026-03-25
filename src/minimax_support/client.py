"""MiniMax Token Plan API client."""
from __future__ import annotations

import os
import base64
import requests
from pathlib import Path
from typing import Any

# API endpoints
ENDPOINT_SEARCH = "/v1/coding_plan/search"
ENDPOINT_VLM = "/v1/coding_plan/vlm"


class MinimaxSupportError(Exception):
    """Base exception."""
    pass


class MinimaxAPIError(MinimaxSupportError):
    """API returned an error."""
    def __init__(self, code: int, message: str):
        self.code = code
        super().__init__(f"[{code}] {message}")


def _load_creds() -> tuple[str, str]:
    """Load API key and host from config file or environment."""
    key = os.environ.get("MINIMAX_API_KEY", "")
    host = os.environ.get("MINIMAX_API_HOST", "")

    if not key or not host:
        creds_file = Path.home() / ".config" / "minimax" / "creds.toml"
        if creds_file.exists():
            content = creds_file.read_text()
            for line in content.splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    v = v.strip().strip('"').strip("'")
                    if k == "MINIMAX_API_KEY" and not key:
                        key = v
                    elif k == "MINIMAX_API_HOST" and not host:
                        host = v

    if not key:
        raise MinimaxSupportError(
            "MINIMAX_API_KEY not set. Run: export MINIMAX_API_KEY=your_key"
        )
    if not host:
        host = "https://api.minimax.io"  # default global

    return key, host


def _process_image(image_source: str) -> str:
    """
    Process image source into base64 data URL.
    Handles: HTTP URLs, local file paths, already-base64 data URLs.
    """
    # Strip @ prefix if present (MCP convention)
    if image_source.startswith("@"):
        image_source = image_source[1:]

    # Already a data URL
    if image_source.startswith("data:"):
        return image_source

    # HTTP/HTTPS URL — download and encode
    if image_source.startswith(("http://", "https://")):
        resp = requests.get(image_source, timeout=30)
        resp.raise_for_status()
        data = resp.content
        content_type = resp.headers.get("content-type", "").lower()
        if "jpeg" in content_type or "jpg" in content_type:
            fmt = "jpeg"
        elif "png" in content_type:
            fmt = "png"
        elif "webp" in content_type:
            fmt = "webp"
        else:
            fmt = "jpeg"
        b64 = base64.b64encode(data).decode("utf-8")
        return f"data:image/{fmt};base64,{b64}"

    # Local file
    path = Path(image_source)
    if not path.exists():
        raise MinimaxSupportError(f"Image file not found: {image_source}")
    data = path.read_bytes()
    fmt = "jpeg"
    if path.suffix.lower() in (".png",):
        fmt = "png"
    elif path.suffix.lower() in (".webp",):
        fmt = "webp"
    elif path.suffix.lower() in (".jpg", ".jpeg"):
        fmt = "jpeg"
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:image/{fmt};base64,{b64}"


def _do_request(endpoint: str, payload: dict[str, Any], key: str, host: str) -> dict:
    """Make a POST request and handle errors."""
    url = f"{host}{endpoint}"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    data = resp.json()

    base_resp = data.get("base_resp", {})
    code = base_resp.get("status_code", 0)
    if code != 0:
        raise MinimaxAPIError(code, base_resp.get("status_msg", "Unknown error"))

    return data


def web_search(query: str) -> dict:
    """Perform a web search and return raw result dict."""
    key, host = _load_creds()
    return _do_request(ENDPOINT_SEARCH, {"q": query}, key, host)


def understand_image(prompt: str, image_source: str) -> str:
    """Analyze an image and return the text result."""
    key, host = _load_creds()
    image_url = _process_image(image_source)
    data = _do_request(ENDPOINT_VLM, {"prompt": prompt, "image_url": image_url}, key, host)
    content = data.get("content", "")
    if not content:
        raise MinimaxSupportError("No content returned from VLM API")
    return content
