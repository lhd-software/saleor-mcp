# Lessons Learned — Saleor MCP Product Explorer

## Bối cảnh

Xây dựng MCP App UI (Product Explorer) cho Saleor MCP Server, hiển thị trong Claude Desktop qua iframe sandbox. Dự án trải qua ~10 lần lặp debug trước khi hoạt động đúng.

---

## 1. Hiểu đúng kiến trúc trước khi code

**Sai lầm:** Nhảy vào implement ngay mà chưa hiểu rõ data flow giữa 3 layers:

```
Claude Desktop (Host) → FastMCP Server (Python) → Saleor GraphQL API
         ↕                        ↕
    iframe (UI)            Tool/Resource handlers
```

**Bài học:** Vẽ ra data flow diagram trước. Xác định rõ:

- Ai gọi ai?
- Data format ở mỗi điểm chuyển giao là gì?
- Ai kiểm soát lifecycle?

---

## 2. Đọc spec chính thức, đừng đoán

**Sai lầm:** Giả định `_meta.ui.csp` hoạt động khi đặt trong `@mcp.resource(meta=...)` mà không verify FastMCP có serialize nó đúng không.

**Bài học:**

- Spec nói CSP phải ở `contents[0]._meta` → nhưng FastMCP không expose `contents[]` format
- Phải đọc source code của framework (FastMCP) để biết nó thực sự làm gì, không chỉ đọc spec của protocol

> **Rule:** Khi dùng framework wrap protocol, verify framework thực sự implement đúng spec.

---

## 3. Debug từng layer, không debug cả stack

**Sai lầm:** Khi hình không hiện, liên tục thay đổi cả server lẫn UI cùng lúc → không biết fix nào có tác dụng.

**Bài học:** Isolate từng layer:

1. Server trả về data đúng không? → `python3 -c "..."` test trực tiếp
2. Thumbnail URL fetch được không? → `httpx.get()` test riêng
3. Base64 encode đúng không? → kiểm tra output size
4. UI nhận data đúng format không? → log `ontoolresult`

---

## 4. Những bug "ngớ ngẩn" tốn nhiều thời gian nhất

### Bug 1: UI gọi sai tool name

```typescript
// Sai — gọi tool "products" (raw GraphQL, không có base64)
callServerTool({ name: "products" })

// Đúng — gọi tool có base64 thumbnails
callServerTool({ name: "open_product_explorer" })
```

**Tốn:** ~3 iterations để phát hiện.
**Bài học:** Khi có nhiều tools cùng làm việc tương tự, đặt tên rõ ràng và document sự khác biệt.

### Bug 2: httpx không follow redirect

```python
# Sai — mặc định httpx KHÔNG follow redirect
httpx.AsyncClient()

# Đúng
httpx.AsyncClient(follow_redirects=True)
```

**Triệu chứng:** 1/3 ảnh hiện, 2/3 không → ảnh đầu có cache sẵn (200 OK), các ảnh khác trả 302.
**Bài học:** Khi "một số hoạt động, một số không" → kiểm tra HTTP status code, đừng giả định tất cả đều 200.

### Bug 3: Race condition — ontoolresult bị ghi đè

```
ontoolresult(3 filtered) → render 3 ✓
loadProducts()            → fetch ALL 20 → render 20 → GHI ĐÈ!
```

**Bài học:** Trong event-driven architecture, xác định rõ **nguồn dữ liệu chính** (source of truth). Nếu `ontoolresult` là chính, thì `loadProducts()` không nên tự chạy.

### Bug 4: Hardcoded fallback logic

```typescript
// loadProducts() luôn gọi {first: 20} không search → override filtered results
arguments: { first: 20, channel: "default-channel" }
```

**Bài học:** Fallback logic phải **aware** context hiện tại. Hoặc tốt hơn: **không có fallback** nếu primary path đã reliable.

---

## 5. Claude Desktop sandbox là constraint đặc biệt

| Constraint                   | Impact                                      | Giải pháp               |
| :--------------------------- | :------------------------------------------ | :----------------------- |
| CSP chặn external images     | `<img src="https://...">` bị block          | Base64 data URI          |
| Không có DevTools/console    | Không thể debug JS trong iframe             | Test ngoài iframe trước  |
| MCP host kiểm soát lifecycle | UI không tự quyết khi nào load data         | Dùng `ontoolresult`      |
| Response size limit          | Ảnh 256px (~45KB×20) có thể vượt limit      | Dùng thumbnail 128px     |

**Bài học tổng quát:** Khi build cho **sandboxed environment**, liệt kê TẤT CẢ constraints trước khi design. Đừng giả định nó hoạt động như browser bình thường.

---

## 6. Framework gap: FastMCP vs MCP Protocol

| MCP Spec nói                         | FastMCP thực tế                                   |
| :----------------------------------- | :------------------------------------------------ |
| `contents[0]._meta.ui.csp`          | Không expose `_meta` trong resource return         |
| Resource handler trả `ReadResourceResult` | Chỉ cho return `str` hoặc `bytes`             |
| Tool `structuredContent`             | Hoạt động đúng khi return `dict`                   |

**Bài học:** FastMCP là abstraction layer — nó giấu đi complexity nhưng cũng giấu đi flexibility. Khi cần low-level control (CSP, `_meta`), có thể phải bypass decorator hoặc dùng raw handler.

---

## 7. Process improvements

### Nên làm từ đầu:

- [ ] Kiểm tra HTTP response codes khi fetch external resources
- [ ] Test data flow end-to-end trước khi build UI fancy
- [ ] Liệt kê sandbox constraints trước khi chọn approach
- [ ] Verify framework behavior bằng cách đọc source, không chỉ docs

### Red flags cần dừng lại suy nghĩ:

- "Một số hoạt động, một số không" → khác biệt ở input/response, không phải code
- "Lần đầu đúng, lần sau sai" → race condition hoặc caching
- "Theo spec mà không work" → framework có thể không implement đúng spec

---

## 8. Tổng kết timeline

| Iteration | Vấn đề                               | Root cause                                  |
| :-------- | :------------------------------------ | :------------------------------------------ |
| 1-3       | UI không load sản phẩm               | Sai data flow, chưa hiểu MCP Apps lifecycle |
| 4-5       | Sản phẩm load nhưng không hình       | CSP block external images                   |
| 6         | Thử CSP config, không work           | FastMCP không serialize `_meta` đúng        |
| 7         | Base64 approach, 1/3 có hình         | httpx không follow 302 redirect             |
| 8         | Tất cả có hình nhưng load 20 sp      | `loadProducts()` hardcode ghi đè            |
| 9         | Fix race, vẫn flash 20→3             | `loadProducts()` function còn tồn tại       |
| 10        | Xoá loadProducts hoàn toàn           | ✅ Hoạt động đúng                           |

> **10 iterations cho 1 feature "hiển thị sản phẩm có hình".**
> Phần lớn thời gian không phải code mà là **debug assumptions sai**.
