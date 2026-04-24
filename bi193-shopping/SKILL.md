---
name: bi193-shopping
description: "Use this skill for ANY shopping or e-commerce interaction with the store4ai MCP (store4ai-mcp). Triggers include (both Vietnamese and English): (1) Product search/discovery — 'tìm', 'gợi ý', 'tôi muốn mua', 'find me', 'I want to buy', 'show me products'; (2) Gift suggestions — 'quà tặng', 'gift for', 'what should I get'; (3) Cart operations — 'thêm vào giỏ', 'add to cart', 'xem giỏ hàng', 'view cart', 'remove from cart'; (4) Product details — 'chi tiết sản phẩm', 'có size XL không', 'còn hàng không'; (5) Promotions — 'đang có khuyến mãi gì', 'discount', 'sale'; (6) Checkout — 'đặt hàng', 'thanh toán', 'checkout', 'place order'; (7) Post-purchase — 'đơn hàng của tôi', 'track order'; (8) Setup & debug — 'setup mcp', 'test token', 'lỗi kết nối'. Always use this skill instead of calling store4ai-mcp tools directly. Handles the full lifecycle: setup → discover → cart → checkout → track."
---

# bi193 Shopping Assistant

End-to-end shopping lifecycle over the **store4ai-mcp** server:
setup → discover → cart → checkout → track.

Production: `https://store4ai-mcp.bi193.com/mcp`

---

## Core principles

1. **Language.** Always reply in the user's language (they wrote in Vietnamese → reply Vietnamese; English → English). But search keywords passed to tools are always **English** — the product catalog is indexed in English.
2. **Ground before you guess.** If the user's intent is vague ("a gift", "something light", "đồ uống"), call `catalog_overview` *first* — do not blind-keyword-search.
3. **UI-first.** Prefer `open_product_explorer`, `open_cart`, `open_checkout` over raw text listings. After opening a UI tool, do **not** dump the same data back as text — the user can already see it.
4. **Confirm before destructive actions** (large cart removals, `complete_checkout`).
5. **Never accept card numbers / CVV / passwords via chat.** Payment happens through the gateway, not the conversation.
6. **Diagnose before reporting failures.** If a tool errors, run `scripts/check_mcp.py` and report the concrete cause, not "it's broken".

---

## Tool quick reference

| Intent | Tool | Notes |
|---|---|---|
| See what the store is shaped like | `catalog_overview` | **Call this first** when intent is vague. ~2 KB. |
| Browse / search products | `open_product_explorer` | UI. Default for most searches. |
| Filtered search (price, stock, ids, slugs) | `products` | Use when user supplies concrete constraints. |
| Product detail + variants | `get_product_details` | Get variantId before `add_to_cart`. |
| Stock check | `stocks` | "còn hàng không" / "in stock" |
| Promotions / discounts | `list_promotions` | "sale gì không" |
| Deal evaluation on current cart | `evaluate_cart_promotions` | Before checkout (advisory) |
| Add to cart (creates cart if needed) | `add_to_cart` | Omit `checkout_id` to create a new cart. Save the returned `data.id`. |
| Find the user's active cart | `current_checkout` | Server-side registry. Call this before answering "what's in my cart?" — items added through the UI won't show up in chat context, so always verify. Returns `{checkout_id: null}` when there truly is no cart. |
| Modify lines | `update_cart_item`, `remove_from_cart` | Requires `checkout_id`. |
| Show cart | `open_cart` | UI. |
| Open checkout UI | `open_checkout` | Pre-fill with any address/email data from context. |
| Set email early | `set_checkout_email` | Collect as soon as known. |
| Set addresses + method in one call | `set_checkout_delivery` | `same_billing=true` reuses shipping. Pass `shipping_method_id` to set method too. |
| Checkout introspection | `get_checkout` | Payment gateways + shipping methods. |
| Place order (payment + complete) | `place_order` | ⚠️ Confirm total with user first. For dummy gateway pass `token="charged"`. |
| Order history | `orders` | Response includes `totalCount` for count queries. |
| Track one order | `track_order` | Fulfillment status. |

**Note on first-call latency.** Claude Desktop lazy-loads tool schemas, so the *first* call to each tool in a session may require a one-shot `tool_search` retry. This is expected and self-corrects — not an error to report.

---

## Decision tree — when to search, ask, or show

Before every shopping turn, **silently enumerate** what you already know from the full conversation (not just the latest message):

```
Slots:
  product_type:  <e.g. "tee shirt", or null>
  category:      <one of the store's category slugs, or null>
  budget_max:    <number or null>
  recipient:     <self / gf / mom / ..., or null>
  occasion:      <birthday / Tết / ..., or null>
  constraints:   <in-stock, on-sale, freeship, ...>
```

Then branch:

| Condition | Action |
|---|---|
| `product_type` is concrete **and** the store has such products | → `open_product_explorer(search=<english>)`, optionally with `filter.categories` if category is known. |
| `product_type` is vague **and** no `catalog_overview` has been fetched this session | → `catalog_overview(channel)`. Then continue with the updated picture. |
| Even after `catalog_overview`, intent is still vague | → Ask **one** short multiple-choice question using real category names from the overview. Example: *"We have Accessories (10), Apparel (18), and Groceries (4) — which area are you looking in?"* |
| User gave specific filters (price, IDs, slugs, in-stock) | → `products(...)` with `filter` / `sort_by`, not the UI explorer. |
| Previous search returned 0 hits | → **Do not retry synonyms blindly.** Use `catalog_overview` and respond: *"We don't carry X, but we do have Y and Z — want to look at those?"* |

**Only ever ask one question per turn**, and only when a critical slot is missing. If you can make a reasonable guess from context, guess and let the user correct.

---

## 0. Setup — onboarding a new user

Trigger: "setup mcp", "kết nối mcp", "mcp không chạy", "how do I use this"

1. Ask for: Saleor API URL, auth token, client (Claude Desktop / VSCode / Cursor).
2. `python scripts/test_token.py --api-url <URL> --token <TOKEN>` — abort on fail.
3. `python scripts/setup_config.py --api-url <URL> --token <TOKEN> --client <claude|vscode|cursor>` — hand the output JSON to the user with paste instructions.
4. `python scripts/check_mcp.py` to verify.

---

## 1. Discover

**Always extract search keywords in English.** VN→EN mapping is your job (you know the language); a few examples:

| User said (any lang) | Search term |
|---|---|
| áo thun, tee shirt | `tee shirt` |
| váy, dress | `dress` |
| nước uống, đồ uống, beverage, drink | *(search often misses — prefer `catalog_overview` + category filter)* |
| giày, shoes | `shoes sneakers` |
| quà bạn gái | `women dress accessories` |
| kính | `sunglasses` |

Typical flows:

```text
# Vague intent
User: "gợi ý quà cho mẹ"
  → catalog_overview() to see what's available
  → "Shop có Apparel, Accessories, Groceries. Mẹ bạn thường thích mảng nào?"

# Concrete intent
User: "show me tee shirts under $20"
  → products(search="tee shirt", filter={price:{lte:20}, stockAvailability:"IN_STOCK"}, channel="default-channel")
  → summarise briefly; open_product_explorer if user wants to browse visually.

# Zero results after a real search
User: "I want to buy energy drinks"
  → open_product_explorer(search="energy drink") → 0
  → catalog_overview() → see Groceries has 4 juice products
  → "We don't carry energy drinks, but we do have fresh juices (Apple, Banana, Carrot, Bean). Want to see those?"
```

For detail queries: `get_product_details(id, channel)` returns variants + stock per variant — use before `add_to_cart`.

---

## 2. Cart

⚠️ You need a **variantId** (not product id) to add to cart. Call `get_product_details` if you only have a product id.

⚠️ **The user can add items to the cart directly through the UI** (`open_product_explorer`). Those additions do NOT show up in chat as tool calls.

When the user asks about the cart ("có gì trong giỏ?", "what's in my cart?", "how many items?"):

1. If you don't have a fresh `checkout_id`, call `current_checkout` first.
   - Returns `{checkout_id: null}` → say "cart is empty" and offer to help add items.
   - Returns `{checkout_id: ...}` → go to step 2.
2. **Open the cart UI** with `open_cart(checkout_id)` — do NOT just list lines in chat. Let the user see the cart visually (same view they get when they click the Cart badge). Your reply should be a one-line summary like *"Bạn có 2 món trong giỏ, tổng $27"*, not a raw text list.

```text
# First add (no checkout_id → tool creates the cart for you)
add_to_cart(
  lines=[{variantId: "...", quantity: 1}],
  channel="default-channel",
  email=<if user gave one>,
) → save data.id as checkout_id

# Subsequent adds
add_to_cart(checkout_id="...", lines=[{variantId: "...", quantity: 1}])

# Modify
update_cart_item(checkout_id, lines=[{lineId: "...", quantity: 3}])
remove_from_cart(checkout_id, line_ids=["..."])

# Show
open_cart(checkout_id)  # UI
```

---

## 3. Checkout

The checkout UI does most of the work — it collects email, both addresses, shipping method, then calls `set_checkout_delivery` + `place_order` itself. **Do not replicate those steps in chat.**

```text
open_cart → user confirms intent to buy
  → open_checkout(
      checkout_id,
      first_name=..., last_name=..., phone=..., street_address=...,
      city=..., country=...                         # pre-fill everything you already know
    )
  → [user fills & submits form in UI; UI completes the order]
  → chat stays out of the way until the user asks about the order
```

Only take over in chat if:
- The UI reports an error the user cannot fix on their own.
- The user explicitly asks you to place the order by text (rare).
- The user wants to modify something the UI doesn't expose.

When taking over in chat (rare), the sequence is:
```text
set_checkout_email(checkout_id, email)
set_checkout_delivery(checkout_id, shipping_address, same_billing=true, shipping_method_id=<from get_checkout>)
get_checkout(checkout_id) → pick gateway from availablePaymentGateways
# CONFIRM TOTAL with user
place_order(checkout_id, gateway_id=<id>, token=<"charged" for dummy, else from gateway SDK>)
```

When calling `open_checkout`, **always pre-fill fields you already know** from conversation (name, address, phone, city, country). Don't re-ask.

---

## 4. Post-purchase

```text
orders(first=10, sort_by={field: "CREATED_AT", direction: "DESC"})  # history
orders(first=5, ...) → pick id → track_order(id=<order_id>)         # track one
get_checkout(checkout_id)                                            # resume an abandoned cart
```

---

## Edge cases

| Situation | Response |
|---|---|
| MCP not responding | Run `scripts/check_mcp.py`; report actual diagnostic. |
| Token invalid/expired | Run `scripts/test_token.py`; guide the user to issue a new one. |
| 0 search results | `catalog_overview` + suggest nearest category (see decision tree). |
| Variant out of stock | `stocks` to confirm; suggest similar variant or product. |
| Empty cart on checkout intent | Ask user to pick products first. |
| User wants to type card/CVV | Refuse politely; direct them to the checkout form. |
| Incomplete address | Ask only for the specific fields missing (not the whole form again). |

---

## Worked examples

**Example 1 — search + add to cart**
```text
User: "tôi muốn mua áo thun size M"
  → open_product_explorer(search="tee shirt")
  → (user picks one in UI)
  → get_product_details(id=<picked>) → find variantId for size M
  → add_to_cart(lines=[{variantId, quantity:1}], channel="default-channel")
  → save data.id as checkout_id
  → open_cart(checkout_id)
  Reply (VN): "Đã thêm Monospace Tee size M vào giỏ. Bạn xem thêm gì nữa không?"
```

**Example 2 — vague intent**
```text
User: "I need something for my girlfriend's birthday, budget $50"
  → catalog_overview(channel="default-channel")
  → (see Apparel has 18, Accessories has 10)
  → products(search="women", filter={price:{lte:50}}, first=10)
  → summarise top 3; open_product_explorer for visual browsing
```

**Example 3 — unavailable category**
```text
User: "bán nước tăng lực không?"
  → open_product_explorer(search="energy drink") → 0 products
  → catalog_overview()
  Reply (VN): "Shop mình không có nước tăng lực, nhưng có Apple/Banana/Carrot/Bean Juice trong mảng Groceries. Bạn muốn xem không?"
```

**Example 4 — checkout**
```text
User: "đặt hàng"
  → open_cart(checkout_id) to confirm
  → open_checkout(checkout_id, <pre-fill name/address/phone/email from history>)
  → UI completes the order end-to-end
  Reply (VN, only when user asks): "Đơn #1042 đã đặt. Bạn muốn track hay tiếp tục mua?"
```
