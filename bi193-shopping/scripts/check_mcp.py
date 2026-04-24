#!/usr/bin/env python3
"""
check_mcp.py — Kiểm tra trạng thái store4ai MCP server.

Usage:
    python scripts/check_mcp.py
    python scripts/check_mcp.py --url https://store4ai-mcp.bi193.com
"""

import argparse
import json
import sys
import time

try:
    import httpx
except ImportError:
    print("❌ Missing dependency: pip install httpx")
    sys.exit(1)

DEFAULT_URL = "https://store4ai-mcp.bi193.com"

MCP_INIT_PAYLOAD = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "check_mcp", "version": "1.0"},
    },
}


def check_health(base_url: str) -> dict:
    """Ping /health endpoint."""
    url = f"{base_url}/health"
    try:
        start = time.time()
        r = httpx.get(url, timeout=10)
        latency = round((time.time() - start) * 1000)
        if r.status_code == 200:
            return {"ok": True, "latency_ms": latency, "body": r.json()}
        return {"ok": False, "status_code": r.status_code, "body": r.text}
    except httpx.ConnectError:
        return {"ok": False, "error": "Connection refused — server không chạy hoặc sai URL"}
    except httpx.TimeoutException:
        return {"ok": False, "error": "Timeout — server không phản hồi sau 10s"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def check_mcp_endpoint(base_url: str) -> dict:
    """Gọi MCP initialize để kiểm tra endpoint /mcp."""
    url = f"{base_url}/mcp"
    try:
        r = httpx.post(
            url,
            json=MCP_INIT_PAYLOAD,
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        if r.status_code == 200:
            data = r.json()
            tools_hint = "serverInfo" in data.get("result", {})
            return {"ok": True, "status_code": 200, "has_server_info": tools_hint}
        elif r.status_code == 401:
            return {"ok": False, "status_code": 401, "error": "Unauthorized — thiếu X-Saleor-Auth-Token header"}
        elif r.status_code == 403:
            return {"ok": False, "status_code": 403, "error": "Forbidden — token không có quyền"}
        else:
            return {"ok": False, "status_code": r.status_code, "body": r.text[:200]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def check_ssl(base_url: str) -> dict:
    """Kiểm tra SSL cert."""
    try:
        import ssl, socket
        from urllib.parse import urlparse
        parsed = urlparse(base_url)
        hostname = parsed.hostname
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
            s.settimeout(5)
            s.connect((hostname, 443))
            cert = s.getpeercert()
            expiry = cert.get("notAfter", "unknown")
        return {"ok": True, "expires": expiry}
    except ssl.SSLCertVerificationError as e:
        return {"ok": False, "error": f"SSL cert lỗi: {e}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Check store4ai MCP server status")
    parser.add_argument("--url", default=DEFAULT_URL, help="MCP server base URL")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    results = {}

    print(f"\n🔍 Checking: {base_url}\n{'─' * 50}")

    # 1. Health check
    print("1. Health endpoint (/health)...")
    health = check_health(base_url)
    results["health"] = health
    if health["ok"]:
        print(f"   ✅ Healthy — {health['latency_ms']}ms")
    else:
        print(f"   ❌ {health.get('error', health.get('status_code', 'unknown'))}")

    # 2. MCP endpoint
    print("2. MCP endpoint (/mcp)...")
    mcp = check_mcp_endpoint(base_url)
    results["mcp"] = mcp
    if mcp["ok"]:
        print(f"   ✅ MCP endpoint responding (status 200)")
    else:
        status = mcp.get("status_code", "?")
        err = mcp.get("error", f"HTTP {status}")
        print(f"   ❌ {err}")

    # 3. SSL
    if base_url.startswith("https"):
        print("3. SSL certificate...")
        ssl_result = check_ssl(base_url)
        results["ssl"] = ssl_result
        if ssl_result["ok"]:
            print(f"   ✅ Valid — expires {ssl_result['expires']}")
        else:
            print(f"   ❌ {ssl_result['error']}")

    # Summary
    print(f"\n{'─' * 50}")
    all_ok = health["ok"] and mcp["ok"]
    if all_ok:
        print("✅ MCP server ONLINE — sẵn sàng sử dụng\n")
    else:
        print("❌ MCP server có vấn đề\n")
        print("💡 Gợi ý:")
        if not health["ok"]:
            print("   • Kiểm tra Docker container: docker ps | grep saleor-mcp")
            print("   • Kiểm tra logs: docker logs saleor-mcp --tail 50")
            print("   • Kiểm tra Nginx: sudo nginx -t")
        if not mcp["ok"] and mcp.get("status_code") == 401:
            print("   • Thêm X-Saleor-Auth-Token vào MCP client config")
        print()

    if args.json:
        print(json.dumps(results, indent=2))

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
