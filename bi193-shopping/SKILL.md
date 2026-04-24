---
name: bi193-shopping
description: "Use this skill for ANY shopping or e-commerce interaction with the store4ai MCP (store4ai-mcp), in Vietnamese or English. Triggers include: (1) Product search/discovery — 'tìm', 'gợi ý', 'tôi muốn mua', 'find me', 'I want to buy', 'show me products'; (2) Gift suggestions — 'quà tặng', 'gift for', 'what should I get'; (3) Cart operations — 'thêm vào giỏ', 'add to cart', 'bớt 1 cái', 'xóa khỏi giỏ', 'xem giỏ hàng', 'view cart'; (4) Product details — 'chi tiết sản phẩm', 'có size XL không', 'còn hàng không', 'product details'; (5) Promotions — 'đang có khuyến mãi gì', 'discount', 'sale'; (6) Checkout — 'đặt hàng', 'thanh toán', 'checkout', 'place order'; (7) Post-purchase — 'đơn hàng của tôi', 'kiểm tra đơn', 'track order', 'lịch sử mua'; (8) Setup & debug — 'setup mcp', 'kết nối mcp', 'test token', 'mcp không chạy', 'lỗi kết nối'. Always use this skill instead of calling store4ai-mcp tools directly. Handles the full lifecycle: setup → discover → cart → checkout → track."
---

# bi193 Shopping Assistant

Skill hướng dẫn Claude xử lý toàn bộ vòng đời mua sắm qua **store4ai-mcp**
(`https://store4ai-mcp.bi193.com/mcp`): setup → tìm kiếm → giỏ hàng → thanh toán → theo dõi.

## Scripts có sẵn

| Script | Mục đích | Chạy khi nào |
|--------|----------|-------------|
| `scripts/check_mcp.py` | Kiểm tra MCP server còn sống | User báo lỗi / trước session quan trọng |
| `scripts/setup_config.py` | Tạo config JSON cho Claude Desktop / VSCode / Cursor | User mới cần onboard |
| `scripts/test_token.py` | Validate token + API URL trước khi dùng | User cung cấp token mới |

---

## 0. SETUP — Onboard user mới

### Khi nào dùng
Trigger: "setup mcp", "kết nối mcp", "mcp không chạy", "làm sao dùng được"

### Bước 1 — Hỏi thông tin
Hỏi user:
- Saleor API URL (ví dụ: `https://api.bi193.com/graphql/`)
- Auth Token
- Client đang dùng: Claude Desktop / VSCode / Cursor

### Bước 2 — Validate token
```bash
python scripts/test_token.py \
  --api-url "https://api.bi193.com/graphql/" \
  --token "USER_TOKEN"
```
Nếu fail → báo lỗi cụ thể, đừng tiếp tục setup.

### Bước 3 — Tạo config
```bash
python scripts/setup_config.py \
  --api-url "https://api.bi193.com/graphql/" \
  --token "USER_TOKEN" \
  --client claude  # hoặc vscode / cursor
```
Copy output JSON → hướng dẫn user paste vào đúng file.

### Bước 4 — Kiểm tra kết nối
```bash
python scripts/check_mcp.py
```

---

## Nguyên tắc chung

1. **Ngôn ngữ**: Phản hồi bằng ngôn ngữ user đang dùng (VN/EN). Keyword search LUÔN dùng **tiếng Anh**.
2. **UI-first**: Ưu tiên tools có UI (`open_product_explorer`, `open_cart`, `open_checkout`).
3. **Không liệt kê lại**: Sau khi gọi UI tool, KHÔNG dump lại danh sách bằng text — UI đã hiển thị.
4. **Xác nhận trước hành động phá hủy**: Trước `complete_checkout`, `remove_from_cart` lớn.
5. **Bảo mật**: KHÔNG nhận số thẻ, CVV, password qua chat. Gateway từ server, không hardcode.
6. **Khi MCP lỗi**: Chạy `scripts/check_mcp.py` để chẩn đoán trước khi báo user.

---

## Quick reference — Tool nào dùng khi nào

| Intent | Tool | Note |
|---|---|---|
| Tìm sản phẩm (khám phá) | `open_product_explorer` | UI, dùng cho đa số search |
| Tìm sản phẩm (filter mạnh) | `products` | Giá, stock, sort, **ids**, **slugs** |
| Chi tiết sản phẩm + variants | `get_product_details` | Size / variant / stock |
| Kiểm tra tồn kho | `stocks` | "còn hàng không" |
| Xem khuyến mãi | `list_promotions` | "có sale gì không" |
| Tạo giỏ mới | `create_cart` | Lần đầu add to cart |
| Thêm vào giỏ | `add_to_cart` | Đã có `checkout_id` |
| Sửa số lượng | `update_cart_item` | Tăng/giảm quantity |
| Xóa khỏi giỏ | `remove_from_cart` | Xóa line items |
| Xem giỏ | `open_cart` | UI review |
| Đánh giá deal | `evaluate_cart_promotions` | Trước checkout (advisory) |
| Mở form checkout | `open_checkout` | UI, pre-fill nếu có data |
| Set địa chỉ giao | `set_shipping_address` | Nếu không dùng UI |
| Set địa chỉ thanh toán | `set_billing_address` | Nếu không dùng UI |
| Chọn shipping | `set_shipping_method` | Sau khi có địa chỉ |
| Xem checkout | `get_checkout` | Lấy shipping methods + gateways |
| Tạo payment | `create_payment` | Gateway từ `get_checkout` |
| Hoàn tất đơn | `complete_checkout` | ⚠️ Cần user xác nhận |
| Danh sách đơn | `orders` | Lịch sử mua |
| Track đơn | `track_order` | Trạng thái fulfillment |

---

## 1. DISCOVER — Tìm kiếm sản phẩm

### Slot extraction từ message + chat history

| Slot | Ví dụ |
|------|-------|
| `recipient` | bạn gái, mẹ, sếp, girlfriend, mom |
| `occasion` | sinh nhật, Valentine, Tết, birthday |
| `budget` | dưới 500k, khoảng 1tr, under $50 |
| `product_type` | áo, váy, giày, shirt, shoes |
| `style/color` | nữ tính, đỏ, sporty, elegant |
| `constraints` | còn hàng, đang sale, freeship |

Chỉ hỏi lại khi KHÔNG thể suy ra loại sản phẩm. Tối đa **1 câu**.

### Keyword expansion (→ English)

| VN/EN | Search string |
|---|---|
| áo thun, tee | `tee shirt` |
| váy, dress | `dress` |
| hoodie | `hoodie` |
| giày, shoes | `shoes sneakers` |
| phụ kiện | `accessories` |
| quà bạn gái | `women dress accessories` |
| quà sinh nhật | `gift` |
| nữ tính | `women elegant` |
| sporty | `sport` |
| kính | `sunglasses` |

### Search: 2 đường

**Default — `open_product_explorer`** (UI):
```
store4ai-mcp:open_product_explorer(search="dress women", first=20)
```

**Filter mạnh — `products`**:
```
store4ai-mcp:products(
  channel="default-channel",
  search="dress",
  filter={stockAvailability: "IN_STOCK"},
  sort_by={field: "PRICE", direction: "ASC"},
  ids=["..."], slugs=["..."],
  first=20
)
```
**Ưu tiên dùng `ids` hoặc `slugs`** khi user cung cấp danh sách cụ thể hoặc muốn so sánh các sản phẩm nhất định.
Sau khi có kết quả text, TÓM TẮT ngắn gọn — không dump raw JSON.

### Fallback khi 0 kết quả
1. Bỏ modifier: `"red elegant dress"` → `"dress"`
2. Thử synonym: `"shirt"` → `"tee polo"`
3. Vẫn 0 → báo user + hỏi tinh chỉnh

### Chi tiết & tồn kho
```
store4ai-mcp:get_product_details(id=<product_id>, channel="default-channel")
store4ai-mcp:stocks(filter={search: "<variant name>"})
store4ai-mcp:list_promotions(first=10)
```

---

## 2. CART — Quản lý giỏ hàng

⚠️ **PHẢI có `variantId`** trước khi add to cart. Gọi `get_product_details` nếu chỉ có `productId`.

```
# Tạo giỏ lần đầu
store4ai-mcp:create_cart(
  channel="default-channel",
  email=<nếu có>,
  lines=[{variantId: "...", quantity: 1}]
)
# → Lưu checkout_id từ response

# Thêm vào giỏ đã có
store4ai-mcp:add_to_cart(checkout_id="...", lines=[{variantId: "...", quantity: 1}])

# Sửa số lượng
store4ai-mcp:update_cart_item(checkout_id="...", lines=[{lineId: "...", quantity: 3}])

# Xóa
store4ai-mcp:remove_from_cart(checkout_id="...", line_ids=["..."])

# Xem giỏ (UI)
store4ai-mcp:open_cart(checkout_id="...")
```

---

## 3. CHECKOUT — Thanh toán

```
open_cart → xác nhận user muốn đặt
    ↓
open_checkout (UI, pre-fill từ chat history)
    ↓
[User điền form]
    ↓
evaluate_cart_promotions → gợi ý nếu có deal tốt hơn
    ↓
get_checkout → lấy availablePaymentGateways
    ↓
create_payment (gateway từ get_checkout, KHÔNG hardcode)
    ↓
⚠️ HỎI XÁC NHẬN: "Xác nhận đặt hàng? Tổng X"
    ↓
complete_checkout (chỉ khi user nói: yes/ok/xác nhận/confirm)
    ↓
Thông báo mã đơn + tổng + dự kiến giao
```

### Mở checkout UI (ưu tiên)
```
store4ai-mcp:open_checkout(
  checkout_id="...",
  first_name=<từ chat>, last_name=<từ chat>,
  phone=<từ chat>, street_address=<từ chat>,
  city=<từ chat>, country="VN"
)
```

### Set địa chỉ qua API (khi không dùng UI)
```
store4ai-mcp:set_shipping_address(checkout_id="...", shipping_address={
  firstName, lastName, phone, streetAddress1, city, country: "VN"
})
→ store4ai-mcp:get_checkout(checkout_id="...")
→ store4ai-mcp:set_shipping_method(checkout_id="...", shipping_method_id="...")
→ store4ai-mcp:set_billing_address(checkout_id="...", billing_address={...})
```

### Payment & Complete
```
store4ai-mcp:create_payment(
  checkout_id="...",
  payment_input={gateway: <get_checkout.availablePaymentGateways[0].id>}
)
store4ai-mcp:complete_checkout(checkout_id="...")
```

---

## 4. POST-PURCHASE

```
# Danh sách đơn
store4ai-mcp:orders(first=10, sort_by={field: "CREATED_AT", direction: "DESC"})

# Track đơn cụ thể
store4ai-mcp:orders(first=5, sort_by=...) → lấy id
store4ai-mcp:track_order(id=<order_id>)

# Tiếp tục checkout dở
store4ai-mcp:get_checkout(checkout_id="...")
```

---

## Edge cases

| Tình huống | Xử lý |
|---|---|
| MCP lỗi / không phản hồi | Chạy `scripts/check_mcp.py` → báo kết quả |
| Token hết hạn / sai | Chạy `scripts/test_token.py` → hướng dẫn lấy token mới |
| 0 kết quả search | Fallback keyword (xem Mục 1) |
| Variant hết hàng | Báo user, gợi ý variant/sản phẩm tương tự |
| Giỏ trống khi checkout | Báo user, quay lại tìm sản phẩm |
| User đòi nhập thẻ qua chat | Từ chối lịch sự, hướng dẫn dùng form checkout |
| Địa chỉ không đủ | Hỏi bổ sung: tên, SĐT, đường, thành phố |

---

## Ví dụ đầy đủ

### Ex 1 — Search + Add to cart
**User**: "tôi muốn mua áo thun size M"
→ `store4ai-mcp:open_product_explorer(search="tee shirt")`
→ "Đây là các áo thun! Bạn thích mẫu nào?"
→ User chọn → `get_product_details(id=...)` → lấy variantId size M
→ `create_cart(...)` → `open_cart(checkout_id="...")`

### Ex 2 — Checkout
**User**: "đặt hàng đi"
→ `open_cart` review → xác nhận
→ `open_checkout(checkout_id, country="VN")`
→ `evaluate_cart_promotions` → `get_checkout` → `create_payment`
→ "Xác nhận $55?" → user ok → `complete_checkout`
→ "Đặt thành công! Mã #1042 🎉"

### Ex 3 — MCP không chạy
**User**: "sao tìm sản phẩm bị lỗi?"
→ `python scripts/check_mcp.py`
→ Báo kết quả: server down / CORS / auth error
→ Hướng dẫn fix cụ thể
