#!/usr/bin/env python3
"""
test_token.py — Validate Saleor Auth Token và API URL.

Gọi 1 GraphQL query nhỏ để xác minh token hợp lệ trước khi dùng.

Usage:
    python scripts/test_token.py --api-url URL --token TOKEN
    python scripts/test_token.py --api-url URL --token TOKEN --verbose
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

# Lightweight query — chỉ lấy shop name để test auth
PING_QUERY = """
query PingAuth {
  shop {
    name
    version
  }
}
"""

# Query test quyền MANAGE_PRODUCTS
PRODUCTS_QUERY = """
query TestProducts {
  products(first: 1, channel: "default-channel") {
    totalCount
  }
}
"""

# Query test quyền MANAGE_ORDERS
ORDERS_QUERY = """
query TestOrders {
  orders(first: 1) {
    totalCount
  }
}
"""


def run_query(api_url: str, token: str, query: str, label: str) -> dict:
    """Chạy GraphQL query và trả về kết quả."""
    try:
        start = time.time()
        r = httpx.post(
            api_url,
            json={"query": query},
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            timeout=15,
            follow_redirects=True,
        )
        latency = round((time.time() - start) * 1000)

        if r.status_code != 200:
            return {
                "ok": False,
                "label": label,
                "error": f"HTTP {r.status_code}",
                "latency_ms": latency,
            }

        data = r.json()

        # GraphQL errors
        if "errors" in data:
            errors = data["errors"]
            msgs = [e.get("message", str(e)) for e in errors]
            # Phân loại lỗi
            if any("permission" in m.lower() or "not autho" in m.lower() for m in msgs):
                return {
                    "ok": False,
                    "label": label,
                    "error": f"Permission denied: {'; '.join(msgs)}",
                    "latency_ms": latency,
                }
            return {
                "ok": False,
                "label": label,
                "error": "; ".join(msgs),
                "latency_ms": latency,
            }

        return {"ok": True, "label": label, "data": data.get("data", {}), "latency_ms": latency}

    except httpx.ConnectError:
        return {"ok": False, "label": label, "error": "Cannot connect — kiểm tra API URL"}
    except httpx.TimeoutException:
        return {"ok": False, "label": label, "error": "Timeout 15s"}
    except Exception as e:
        return {"ok": False, "label": label, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Validate Saleor Auth Token")
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
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    args = parser.parse_args()

    api_url = args.api_url.strip()
    # Đảm bảo kết thúc bằng /graphql/
    if not api_url.endswith("/graphql/"):
        if api_url.endswith("/graphql"):
            api_url = api_url + "/"
        elif "/graphql" not in api_url:
            api_url = api_url.rstrip("/") + "/graphql/"

    token = args.token.strip()
    masked = f"{token[:8]}{'*' * min(len(token) - 8, 20)}"

    print(f"\n🔑 Testing token: {masked}")
    print(f"   API URL: {api_url}\n{'─' * 55}")

    results = []

    # Test 1: Basic connectivity + auth
    print("1. Auth & connectivity...")
    r1 = run_query(api_url, token, PING_QUERY, "Auth")
    results.append(r1)
    if r1["ok"]:
        shop = r1["data"].get("shop", {})
        print(f"   ✅ Connected — Shop: {shop.get('name', '?')} (Saleor {shop.get('version', '?')}) [{r1['latency_ms']}ms]")
    else:
        print(f"   ❌ {r1['error']}")
        if not args.json:
            print("\n💡 Nguyên nhân thường gặp:")
            if "Cannot connect" in r1["error"]:
                print("   • API URL sai hoặc Saleor server không chạy")
            elif "401" in r1["error"] or "403" in r1["error"]:
                print("   • Token sai hoặc hết hạn → lấy token mới từ Saleor Dashboard")
            else:
                print("   • Kiểm tra lại API URL format: https://your-domain.com/graphql/")
            print()
        if args.json:
            print(json.dumps({"results": results, "valid": False}, indent=2))
        sys.exit(1)

    # Test 2: MANAGE_PRODUCTS permission
    print("2. Permission MANAGE_PRODUCTS...")
    r2 = run_query(api_url, token, PRODUCTS_QUERY, "MANAGE_PRODUCTS")
    results.append(r2)
    if r2["ok"]:
        count = r2["data"].get("products", {}).get("totalCount", "?")
        print(f"   ✅ OK — {count} products trong default-channel [{r2['latency_ms']}ms]")
    else:
        print(f"   ❌ {r2['error']}")
        print("   → Token cần quyền MANAGE_PRODUCTS")

    # Test 3: MANAGE_ORDERS permission
    print("3. Permission MANAGE_ORDERS...")
    r3 = run_query(api_url, token, ORDERS_QUERY, "MANAGE_ORDERS")
    results.append(r3)
    if r3["ok"]:
        count = r3["data"].get("orders", {}).get("totalCount", "?")
        print(f"   ✅ OK — {count} orders [{r3['latency_ms']}ms]")
    else:
        print(f"   ❌ {r3['error']}")
        print("   → Token cần quyền MANAGE_ORDERS")

    # Summary
    all_ok = all(r["ok"] for r in results)
    print(f"\n{'─' * 55}")
    if all_ok:
        print("✅ Token HỢP LỆ — sẵn sàng dùng với store4ai MCP\n")
        print("👉 Bước tiếp theo: chạy setup_config.py để tạo config cho AI client")
    else:
        failed = [r["label"] for r in results if not r["ok"]]
        print(f"⚠️  Token có vấn đề với: {', '.join(failed)}")
        print("   → Vào Saleor Dashboard → Settings → Staff → tạo token mới với đủ quyền\n")

    if args.verbose:
        print("\nChi tiết:")
        for r in results:
            print(f"  [{r['label']}] ok={r['ok']} latency={r.get('latency_ms')}ms")

    if args.json:
        print(json.dumps({
            "valid": all_ok,
            "api_url": api_url,
            "results": [
                {"label": r["label"], "ok": r["ok"],
                 "latency_ms": r.get("latency_ms"),
                 "error": r.get("error")}
                for r in results
            ],
        }, indent=2))

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
