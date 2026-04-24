#!/usr/bin/env python3
"""
setup_config.py — Tạo config JSON để kết nối store4ai MCP với AI client.

Usage:
    python scripts/setup_config.py --api-url URL --token TOKEN --client claude
    python scripts/setup_config.py --api-url URL --token TOKEN --client vscode
    python scripts/setup_config.py --api-url URL --token TOKEN --client cursor
    python scripts/setup_config.py --api-url URL --token TOKEN --client all
"""

import argparse
import json
import os
import sys
from pathlib import Path

MCP_URL = "https://store4ai-mcp.bi193.com/mcp"

CONFIGS = {
    "claude": {
        "label": "Claude Desktop",
        "file_path": {
            "darwin": "~/Library/Application Support/Claude/claude_desktop_config.json",
            "win32": "%APPDATA%\\Claude\\claude_desktop_config.json",
            "linux": "~/.config/Claude/claude_desktop_config.json",
        },
        "format": lambda url, token: {
            "mcpServers": {
                "store4ai-mcp": {
                    "type": "http",
                    "url": MCP_URL,
                    "headers": {
                        "X-Saleor-API-URL": url,
                        "X-Saleor-Auth-Token": token,
                    },
                }
            }
        },
        "note": "Paste vào mcpServers object trong file config. Restart Claude Desktop sau khi lưu.",
    },
    "vscode": {
        "label": "VSCode / GitHub Copilot",
        "file_path": {
            "all": ".vscode/mcp.json (trong project folder)",
        },
        "format": lambda url, token: {
            "servers": {
                "store4ai-mcp": {
                    "type": "http",
                    "url": MCP_URL,
                    "headers": {
                        "X-Saleor-API-URL": url,
                        "X-Saleor-Auth-Token": token,
                    },
                }
            }
        },
        "note": "Tạo file .vscode/mcp.json trong project folder. Reload VSCode window sau khi lưu.",
    },
    "cursor": {
        "label": "Cursor AI",
        "file_path": {
            "darwin": "~/.cursor/mcp.json",
            "win32": "%USERPROFILE%\\.cursor\\mcp.json",
            "linux": "~/.cursor/mcp.json",
        },
        "format": lambda url, token: {
            "mcpServers": {
                "store4ai-mcp": {
                    "type": "http",
                    "url": MCP_URL,
                    "headers": {
                        "X-Saleor-API-URL": url,
                        "X-Saleor-Auth-Token": token,
                    },
                }
            }
        },
        "note": "Paste vào mcpServers object trong file config. Restart Cursor sau khi lưu.",
    },
}


def get_file_path(client_cfg: dict) -> str:
    """Lấy đường dẫn file config theo OS."""
    paths = client_cfg.get("file_path", {})
    platform = sys.platform
    return paths.get(platform, paths.get("all", "Xem tài liệu của client"))


def print_config(client_key: str, api_url: str, token: str):
    cfg = CONFIGS[client_key]
    print(f"\n{'═' * 55}")
    print(f"  {cfg['label']}")
    print(f"{'═' * 55}")

    file_path = get_file_path(cfg)
    print(f"📁 File: {file_path}\n")

    config_json = cfg["format"](api_url, token)
    print(json.dumps(config_json, indent=2, ensure_ascii=False))

    print(f"\n💡 {cfg['note']}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate MCP config for AI clients"
    )
    parser.add_argument(
        "--api-url",
        required=True,
        help="Saleor GraphQL URL, e.g. https://api.bi193.com/graphql/",
    )
    parser.add_argument(
        "--token",
        required=True,
        help="Saleor Auth Token",
    )
    parser.add_argument(
        "--client",
        choices=["claude", "vscode", "cursor", "all"],
        default="claude",
        help="Target AI client (default: claude)",
    )
    parser.add_argument(
        "--mcp-url",
        default=MCP_URL,
        help=f"MCP server URL (default: {MCP_URL})",
    )
    args = parser.parse_args()

    # Validate inputs
    if not args.api_url.startswith("http"):
        print("❌ API URL phải bắt đầu bằng http:// hoặc https://")
        sys.exit(1)
    if not args.api_url.endswith("/graphql/"):
        print("⚠️  API URL thường kết thúc bằng /graphql/")

    print(f"\n🔧 Generating config cho: {args.client}")
    print(f"   API URL : {args.api_url}")
    print(f"   Token   : {args.token[:8]}{'*' * (len(args.token) - 8)}")
    print(f"   MCP URL : {args.mcp_url}")

    clients = list(CONFIGS.keys()) if args.client == "all" else [args.client]
    for client_key in clients:
        print_config(client_key, args.api_url, args.token)

    print(f"\n{'─' * 55}")
    print("✅ Done! Sau khi paste config, restart client và test bằng:")
    print("   python scripts/check_mcp.py")
    print()


if __name__ == "__main__":
    main()
