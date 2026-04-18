import json
import os

config_path = os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")

with open(config_path, "r") as f:
    config = json.load(f)

if "mcpServers" not in config:
    config["mcpServers"] = {}

config["mcpServers"]["saleor"] = {
    "command": "uv",
    "args": [
        "--directory",
        "/Users/nguyendat/Code/work/store4ai/saleor-mcp",
        "run",
        "saleor-mcp"
    ],
    "env": {
        "SALEOR_API_URL": "https://api.bi193.com/graphql/",
        "SALEOR_AUTH_TOKEN": "iim23V4z72d0Bg9BUS8PUGaDNQ671ha"
      }
}

with open(config_path, "w") as f:
    json.dump(config, f, indent=2)

print("Claude Desktop configuration updated successfully.")
