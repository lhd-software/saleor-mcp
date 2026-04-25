from unittest.mock import patch

import pytest
from fastmcp.exceptions import ToolError

from saleor_mcp.config import _extract_bearer, get_config_from_headers


def test_extract_bearer_valid():
    assert _extract_bearer("Bearer abc.def.ghi") == "abc.def.ghi"
    assert _extract_bearer("bearer abc") == "abc"  # case-insensitive


def test_extract_bearer_invalid():
    assert _extract_bearer(None) is None
    assert _extract_bearer("") is None
    assert _extract_bearer("Basic abc") is None
    assert _extract_bearer("abc") is None  # missing scheme


@patch("saleor_mcp.config.get_http_headers")
def test_authorization_bearer_takes_precedence(mock_headers, monkeypatch):
    monkeypatch.delenv("SALEOR_API_URL", raising=False)
    monkeypatch.delenv("SALEOR_AUTH_TOKEN", raising=False)
    mock_headers.return_value = {
        "x-saleor-api-url": "https://api.example.com/graphql/",
        "authorization": "Bearer jwt-token",
        "x-saleor-auth-token": "legacy-token",
    }
    cfg = get_config_from_headers()
    assert cfg.auth_token == "jwt-token"  # Bearer wins over legacy header


@patch("saleor_mcp.config.get_http_headers")
def test_legacy_header_still_works(mock_headers, monkeypatch):
    monkeypatch.delenv("SALEOR_API_URL", raising=False)
    monkeypatch.delenv("SALEOR_AUTH_TOKEN", raising=False)
    mock_headers.return_value = {
        "x-saleor-api-url": "https://api.example.com/graphql/",
        "x-saleor-auth-token": "legacy-token",
    }
    cfg = get_config_from_headers()
    assert cfg.auth_token == "legacy-token"


@patch("saleor_mcp.config.get_http_headers")
def test_env_fallback(mock_headers, monkeypatch):
    monkeypatch.setenv("SALEOR_API_URL", "https://env.example.com/graphql/")
    monkeypatch.setenv("SALEOR_AUTH_TOKEN", "env-token")
    mock_headers.return_value = {}
    cfg = get_config_from_headers()
    assert cfg.api_url == "https://env.example.com/graphql/"
    assert cfg.auth_token == "env-token"


@patch("saleor_mcp.config.get_http_headers")
def test_missing_token_raises(mock_headers, monkeypatch):
    monkeypatch.delenv("SALEOR_AUTH_TOKEN", raising=False)
    mock_headers.return_value = {"x-saleor-api-url": "https://x/graphql/"}
    with pytest.raises(ToolError, match="Missing Saleor Auth Token"):
        get_config_from_headers()
