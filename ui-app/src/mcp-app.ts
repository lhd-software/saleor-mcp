import { App } from "@modelcontextprotocol/ext-apps";

// ═══════════════════════════════════════════════════
// CSS
// ═══════════════════════════════════════════════════
const style = document.createElement("style");
style.textContent = `
:root {
  --primary: #2563eb; --primary-hover: #1d4ed8;
  --bg: #f8fafc; --card-bg: #fff; --text-main: #1e293b; --text-muted: #64748b;
  --success: #22c55e; --danger: #ef4444;
  --shadow: 0 4px 6px -1px rgb(0 0 0/0.1), 0 2px 4px -2px rgb(0 0 0/0.1);
  --radius: 12px;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text-main); padding: 16px; }
header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
h1 { font-size: 20px; font-weight: 800; letter-spacing: -0.025em; }
.badge { background: var(--primary); color: white; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; border: none; cursor: pointer; }
.breadcrumb { display: flex; gap: 6px; align-items: center; margin-bottom: 12px; font-size: 12px; color: var(--text-muted); flex-wrap: wrap; }
.crumb { cursor: pointer; padding: 3px 8px; border-radius: 6px; }
.crumb.active { background: var(--primary); color: white; font-weight: 600; }
.crumb::after { content: ' →'; margin-left: 4px; }
.crumb:last-child::after { content: ''; }
#status-bar { background: var(--card-bg); padding: 10px 14px; border-radius: var(--radius); box-shadow: var(--shadow); margin-bottom: 16px; font-size: 13px; color: var(--text-muted); }
.view { display: none; }
.view.active { display: block; }
#product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 14px; }
.product-card { background: var(--card-bg); border-radius: var(--radius); overflow: hidden; box-shadow: var(--shadow); transition: transform 0.2s, box-shadow 0.2s; cursor: pointer; }
.product-card:hover { transform: translateY(-3px); box-shadow: 0 10px 15px -3px rgb(0 0 0/0.1); }
.product-img { width: 100%; height: 130px; background: #f1f5f9; display: flex; align-items: center; justify-content: center; color: var(--text-muted); font-size: 11px; overflow: hidden; }
.product-img img { width: 100%; height: 100%; object-fit: cover; }
.product-info { padding: 10px; }
.product-name { font-weight: 700; font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 4px; }
.product-price { color: var(--primary); font-weight: 700; font-size: 13px; }
.product-actions { padding: 0 10px 10px; }
.btn-cart-sm { width: 100%; padding: 6px; border-radius: 8px; border: 1.5px solid var(--primary); background: transparent; color: var(--primary); font-size: 11px; font-weight: 700; cursor: pointer; transition: all 0.15s; }
.btn-cart-sm:hover { background: var(--primary); color: white; }
.overlay { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); backdrop-filter: blur(4px); z-index: 100; align-items: center; justify-content: center; padding: 16px; }
.modal { background: var(--card-bg); width: 100%; max-width: 420px; border-radius: 16px; overflow: hidden; box-shadow: 0 25px 50px -12px rgb(0 0 0/0.25); animation: slideUp 0.25s ease-out; }
@keyframes slideUp { from { transform: translateY(16px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
.modal-header { padding: 14px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
.modal-header h2 { font-size: 16px; }
.modal-body { padding: 14px; }
.modal-footer { padding: 10px 14px; background: #f8fafc; display: flex; justify-content: flex-end; gap: 8px; }
button { padding: 7px 14px; border-radius: 8px; border: none; font-weight: 600; font-size: 12px; cursor: pointer; transition: all 0.15s; }
.btn-primary { background: var(--primary); color: white; }
.btn-primary:hover { background: var(--primary-hover); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { background: #e2e8f0; color: var(--text-main); }
.btn-secondary:hover { background: #cbd5e1; }
.btn-success { background: var(--success); color: white; }
.btn-danger { background: var(--danger); color: white; }
.btn-full { width: 100%; padding: 12px; font-size: 14px; margin-top: 12px; }
.variant-list { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 6px; }
.variant-btn { font-size: 11px; padding: 4px 8px; }
.variant-btn.active { background: var(--primary); color: white; }
.detail-image-wrap { width: 100%; height: 260px; background: #f1f5f9; border-radius: 10px; overflow: hidden; margin-bottom: 10px; display: flex; align-items: center; justify-content: center; }
.detail-image-wrap img { width: 100%; height: 100%; object-fit: cover; }
.detail-desc { color: var(--text-muted); font-size: 12px; line-height: 1.5; margin: 6px 0; max-height: 80px; overflow-y: auto; }
.detail-price { font-size: 18px; font-weight: 800; color: var(--primary); margin: 8px 0; }
.close-btn { background: none; border: none; font-size: 18px; cursor: pointer; padding: 0 4px; color: var(--text-muted); }
.loading { text-align: center; padding: 30px; color: var(--text-muted); }
.hidden { display: none !important; }
.cart-line { display: flex; align-items: center; gap: 12px; padding: 12px; background: var(--card-bg); border-radius: var(--radius); box-shadow: var(--shadow); margin-bottom: 10px; }
.cart-line-img { width: 56px; height: 56px; border-radius: 8px; object-fit: cover; background: #f1f5f9; flex-shrink: 0; }
.cart-line-info { flex: 1; min-width: 0; }
.cart-line-name { font-weight: 700; font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cart-line-variant { font-size: 11px; color: var(--text-muted); }
.cart-line-price { font-weight: 700; color: var(--primary); font-size: 13px; }
.qty-controls { display: flex; align-items: center; gap: 6px; }
.qty-btn { width: 26px; height: 26px; border-radius: 6px; display: flex; align-items: center; justify-content: center; padding: 0; font-size: 14px; }
.qty-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.qty-val { font-weight: 700; font-size: 13px; min-width: 20px; text-align: center; }
.summary-box { background: var(--card-bg); border-radius: var(--radius); box-shadow: var(--shadow); padding: 14px; margin-top: 14px; }
.summary-row { display: flex; justify-content: space-between; padding: 4px 0; font-size: 13px; }
.summary-total { font-weight: 800; font-size: 16px; border-top: 2px solid #e2e8f0; padding-top: 8px; margin-top: 4px; }
fieldset { border: 1px solid #e2e8f0; border-radius: var(--radius); padding: 14px; margin-bottom: 12px; }
legend { font-weight: 700; font-size: 13px; padding: 0 6px; }
.form-row { display: flex; gap: 8px; }
input, select { width: 100%; padding: 8px 10px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 13px; margin-bottom: 8px; }
.toggle-label { display: flex; align-items: center; gap: 8px; font-size: 13px; margin-bottom: 12px; cursor: pointer; }
.toggle-label input { width: auto; margin: 0; }
.radio-group label { display: flex; align-items: center; gap: 8px; padding: 8px; border: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: 6px; cursor: pointer; font-size: 13px; }
.radio-group input { width: auto; margin: 0; }
.toast { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: var(--success); color: white; padding: 8px 20px; border-radius: 20px; font-size: 13px; font-weight: 600; z-index: 200; animation: fadeInUp 0.3s ease-out; max-width: 90vw; text-align: center; }
.toast.error { background: var(--danger); }
@keyframes fadeInUp { from { opacity: 0; transform: translateX(-50%) translateY(10px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }
`;
document.head.appendChild(style);

// ═══════════════════════════════════════════════════
// Types & State
// ═══════════════════════════════════════════════════
interface Variant {
  id: string;
  name: string;
  sku?: string;
  pricing?: { amount: number; currency: string };
}
interface Product {
  id: string; name: string; slug?: string; description?: string;
  thumbnail?: { url: string }; pricing?: { amount: number; currency: string };
  variants?: Variant[];
}
interface CartItem {
  product: Product; variantId: string; variantName: string; quantity: number;
}

type ViewName = "products" | "detail" | "cart" | "checkout" | "payment" | "order";

const cart: CartItem[] = JSON.parse(localStorage.getItem("mcp_cart") || "[]");
let selectedVariantId: string | null = null;
let currentCheckoutId: string | null = localStorage.getItem("mcp_checkout_id");
const currentChannel = "default-channel";

function saveCart() {
  localStorage.setItem("mcp_cart", JSON.stringify(cart));
}

function saveCheckoutId(id: string | null) {
  currentCheckoutId = id;
  if (id) localStorage.setItem("mcp_checkout_id", id);
  else localStorage.removeItem("mcp_checkout_id");
}

// ═══════════════════════════════════════════════════
// DOM refs
// ═══════════════════════════════════════════════════
const statusBar = document.getElementById("status-bar")!;
const productGrid = document.getElementById("product-grid")!;
const cartBadge = document.getElementById("cart-badge")!;
const breadcrumb = document.getElementById("breadcrumb")!;

// ═══════════════════════════════════════════════════
// Router
// ═══════════════════════════════════════════════════
function showView(name: ViewName) {
  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  document.getElementById(`view-${name}`)?.classList.add("active");
  updateBreadcrumb(name);
}

const CRUMB_ORDER: ViewName[] = ["products", "detail", "cart", "checkout", "payment", "order"];
const CRUMB_LABELS: Record<ViewName, string> = {
  products: "Products", detail: "Detail", cart: "Cart", checkout: "Checkout", payment: "Payment", order: "Order"
};

function updateBreadcrumb(active: ViewName) {
  const idx = CRUMB_ORDER.indexOf(active);
  breadcrumb.innerHTML = "";
  for (let i = 0; i <= idx; i++) {
    const span = document.createElement("span");
    span.className = "crumb" + (i === idx ? " active" : "");
    span.textContent = CRUMB_LABELS[CRUMB_ORDER[i]];
    span.dataset.view = CRUMB_ORDER[i];
    if (i < idx) {
      span.addEventListener("click", () => showView(CRUMB_ORDER[i]));
    }
    breadcrumb.appendChild(span);
  }
}

// ═══════════════════════════════════════════════════
// Toast notification
// ═══════════════════════════════════════════════════
function showToast(msg: string, duration = 1500, isError = false) {
  const t = document.createElement("div");
  t.className = "toast" + (isError ? " error" : "");
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), duration);
}

// ═══════════════════════════════════════════════════
// Cart helpers
// ═══════════════════════════════════════════════════
function updateCartBadge() {
  const total = cart.reduce((s, i) => s + i.quantity, 0);
  cartBadge.textContent = `Cart: ${total}`;
}

// ═══════════════════════════════════════════════════
// MCP App
// ═══════════════════════════════════════════════════
const app = new App({ name: "BI193 Store", version: "2.1.0" });
app.onerror = console.error;

async function callTool(name: string, args: Record<string, any>): Promise<any> {
  const res: any = await app.callServerTool({ name, arguments: args });
  return res.structuredContent ?? res;
}

// Saleor/MCP errors often carry a `field` (e.g. "postalCode"). Surface that
// so the user knows *which* field was rejected instead of "invalid".
const FIELD_LABELS: Record<string, string> = {
  firstName: "First name",
  lastName: "Last name",
  streetAddress1: "Street address",
  streetAddress2: "Street address (line 2)",
  city: "City",
  cityArea: "District/area",
  postalCode: "Postal code",
  country: "Country",
  countryArea: "State/province",
  phone: "Phone",
  email: "Email",
};

function extractErrors(resData: any): string | null {
  if (!resData) return null;
  const errs = resData.errors || resData.data?.errors;
  if (errs && errs.length > 0) {
    const e = errs[0];
    const label = e.field ? (FIELD_LABELS[e.field] || e.field) : null;
    const msg = e.message || e.code || "Server error";
    return label ? `${label}: ${msg}` : msg;
  }
  if (resData.error) return resData.error;
  return null;
}

function fieldFromErrors(resData: any): string | null {
  if (!resData) return null;
  const errs = resData.errors || resData.data?.errors;
  return errs && errs.length > 0 ? (errs[0].field || null) : null;
}

const FIELD_TO_INPUT_ID: Record<string, string> = {
  firstName: "ship-firstName",
  lastName: "ship-lastName",
  streetAddress1: "ship-street",
  city: "ship-city",
  postalCode: "ship-postalCode",
  country: "ship-country",
  phone: "ship-phone",
  email: "ship-email",
};

function highlightField(fieldName: string | null) {
  // Clear previous highlights
  for (const id of Object.values(FIELD_TO_INPUT_ID)) {
    const el = document.getElementById(id) as HTMLInputElement | HTMLSelectElement | null;
    if (el) el.style.borderColor = "";
  }
  if (!fieldName) return;
  const id = FIELD_TO_INPUT_ID[fieldName];
  if (!id) return;
  const el = document.getElementById(id) as HTMLInputElement | HTMLSelectElement | null;
  if (el) {
    el.style.borderColor = "var(--danger)";
    el.focus();
  }
}

// ═══════════════════════════════════════════════════
// Cart sync (UI → Saleor server tools)
// ═══════════════════════════════════════════════════
async function serverAddToCart(variantId: string, quantity: number): Promise<void> {
  const args: Record<string, any> = { lines: [{ variantId, quantity }] };
  if (currentCheckoutId) {
    args.checkout_id = currentCheckoutId;
  } else {
    args.channel = currentChannel;
  }
  const res = await callTool("add_to_cart", args);
  const err = extractErrors(res);
  if (err) throw new Error(err);
  const id = res.data?.id;
  if (id && !currentCheckoutId) saveCheckoutId(id);
  // Fire-and-forget: keep Claude's context in sync with the UI cart.
  void syncCartToModelContext();
}

async function serverUpdateCartItem(lineId: string, quantity: number): Promise<void> {
  if (!currentCheckoutId) return;
  const res = await callTool("update_cart_item", {
    checkout_id: currentCheckoutId,
    lines: [{ lineId, quantity }],
  });
  const err = extractErrors(res);
  if (err) throw new Error(err);
}

async function serverRemoveCartLine(lineId: string): Promise<void> {
  if (!currentCheckoutId) return;
  const res = await callTool("remove_from_cart", {
    checkout_id: currentCheckoutId,
    line_ids: [lineId],
  });
  const err = extractErrors(res);
  if (err) throw new Error(err);
}

async function fetchServerCart(): Promise<any | null> {
  if (!currentCheckoutId) return null;
  const res = await callTool("open_cart", { checkout_id: currentCheckoutId });
  if (res.error) throw new Error(res.error);
  return res.checkout || null;
}

// Push the current cart state into Claude's model context so the chat knows
// about items added via the UI without polluting the conversation with tool
// calls. Each call overwrites the previous snapshot (spec-guaranteed).
//
// IMPORTANT: we only push when this iframe actually holds a checkout_id.
// Fresh iframes (one spawns per tool call, each in its own blob origin
// without shared localStorage) would otherwise wipe the context set by an
// earlier iframe to "no cart" just because they themselves haven't seen
// the user add anything. The `current_checkout` server tool is the canonical
// fallback Claude uses when context is missing.
async function syncCartToModelContext(
  opts: { force?: boolean } = {},
): Promise<void> {
  try {
    if (!currentCheckoutId) {
      if (!opts.force) return;
      await app.updateModelContext({
        content: [{
          type: "text",
          text: "UI cart state: no active checkout (last cart was completed or cleared).",
        }],
      });
      return;
    }
    const co = await fetchServerCart();
    if (!co) return;
    const lines = (co.lines || []) as Array<{
      quantity: number; productName: string; variantName?: string;
    }>;
    const lineList = lines.length
      ? lines.map(l =>
          `- ${l.quantity}× ${l.productName}${l.variantName ? ` (${l.variantName})` : ""}`
        ).join("\n")
      : "(empty)";
    const total = co.total
      ? `${co.total.amount.toFixed(2)} ${co.total.currency}`
      : "—";
    const md = [
      "---",
      `checkout_id: ${currentCheckoutId}`,
      `line_count: ${lines.length}`,
      `total: ${total}`,
      "---",
      "",
      "UI cart state (user's active Saleor checkout, maintained by the mcp-app UI):",
      "",
      lineList,
      "",
      "To inspect or modify this cart from chat, use `open_cart` / `update_cart_item` / ",
      "`remove_from_cart` with the `checkout_id` above.",
    ].join("\n");
    await app.updateModelContext({
      content: [{ type: "text", text: md }],
    });
  } catch (e) {
    console.error("syncCartToModelContext failed:", e);
  }
}

function addToCart(product: Product, variantId: string, variantName: string) {
  // Optimistic local update (for badge responsiveness)
  const existing = cart.find(i => i.variantId === variantId);
  if (existing) existing.quantity++;
  else cart.push({ product, variantId, variantName, quantity: 1 });
  saveCart();
  updateCartBadge();
  showToast(`✓ ${product.name} added`);

  // Sync to Saleor server tool
  serverAddToCart(variantId, 1).catch((err: Error) => {
    console.error("serverAddToCart failed:", err);
    showToast(`❌ ${err.message || "Add to cart failed"}`, 3000, true);
    // Revert optimistic change
    const item = cart.find(i => i.variantId === variantId);
    if (item) {
      item.quantity--;
      if (item.quantity <= 0) {
        const idx = cart.indexOf(item);
        if (idx >= 0) cart.splice(idx, 1);
      }
      saveCart();
      updateCartBadge();
    }
  });
}

// ═══════════════════════════════════════════════════
// Host → UI callbacks
// ═══════════════════════════════════════════════════
// This UI does not register any host-callable tools, so we only listen for
// server tool results and mirror them into the appropriate view.
app.ontoolresult = (result: any) => {
  console.info("Tool result:", result);
  // Reset visibility on each result — a prior empty-products render may have hidden us.
  document.body.style.display = "";

  const sc = result.structuredContent;
  if (!sc) {
    processContentArray(result.content);
    return;
  }

  // Capture checkout_id whenever server-side tools return it
  if (sc.checkout?.id) saveCheckoutId(sc.checkout.id);
  if (sc.data?.id && sc.data.lines !== undefined) saveCheckoutId(sc.data.id);

  switch (sc.view) {
    case "products":
      // If the tool returned no products, collapse the iframe so the chat
      // doesn't show an empty BI193 Store card. The LLM's text summary
      // handles the "no results" messaging on its own.
      if (!sc.products || sc.products.length === 0) {
        document.body.style.display = "none";
        return;
      }
      showView("products");
      renderProducts(sc.products as Product[]);
      statusBar.textContent = `✅ ${sc.products.length} products loaded`;
      break;
    case "cart":
      showView("cart");
      renderCartView(sc.checkout);
      break;
    case "detail":
      // Open the detail modal on top of the products view.
      showView("products");
      if (sc.product) showDetail(sc.product as Product);
      break;
    case "checkout":
      showView("checkout");
      renderCheckoutView(sc.checkout, sc.prefillAddress);
      break;
    case "payment":
      showView("payment");
      renderPaymentView(sc.payment);
      break;
    case "order":
      showView("order");
      renderOrderView(sc.order);
      break;
    default:
      if (sc.products && Array.isArray(sc.products)) {
        if (sc.products.length === 0) {
          document.body.style.display = "none";
          return;
        }
        showView("products");
        renderProducts(sc.products as Product[]);
        statusBar.textContent = `✅ ${sc.products.length} products loaded`;
      }
  }
};

app.connect().then(() => {
  statusBar.textContent = "⏳ Loading products...";
  updateCartBadge();
  // On connect, push whatever cart state persists across UI reloads into
  // Claude's context so a fresh chat turn still knows about the user's cart.
  void syncCartToModelContext();
}).catch((err: any) => {
  console.error("Connect failed:", err);
  statusBar.textContent = "❌ Connect failed: " + err.message;
});

function processContentArray(content: any[]) {
  if (!content || !Array.isArray(content)) return;
  for (const item of content) {
    if (item.type === "text" && item.text) {
      try {
        const parsed = JSON.parse(item.text);
        const products: Product[] = parsed.products || parsed.data?.products || [];
        if (products.length > 0) {
          showView("products");
          renderProducts(products);
          statusBar.textContent = `✅ ${products.length} products loaded`;
          return;
        }
      } catch { /* not JSON */ }
    }
  }
}

// ═══════════════════════════════════════════════════
// Render: Products
// ═══════════════════════════════════════════════════
function renderProducts(products: Product[]) {
  productGrid.innerHTML = "";
  if (products.length === 0) {
    productGrid.innerHTML = '<div class="loading">No products found.</div>';
    return;
  }
  for (const p of products) {
    const card = document.createElement("div");
    card.className = "product-card";
    const imgUrl = p.thumbnail?.url;
    const price = p.pricing ? `$${p.pricing.amount.toFixed(2)} ${p.pricing.currency}` : "N/A";

    card.innerHTML = `
      <div class="product-img">
        ${imgUrl ? `<img src="${imgUrl}" alt="${p.name}" onerror="this.parentElement.textContent='No Image'">` : "No Image"}
      </div>
      <div class="product-info">
        <div class="product-name">${p.name}</div>
        <div class="product-price">${price}</div>
      </div>
      <div class="product-actions">
        <button class="btn-cart-sm">🛒 Add to Cart</button>
      </div>
    `;

    // Click card body → detail modal
    card.querySelector(".product-img")!.addEventListener("click", () => showDetail(p));
    card.querySelector(".product-info")!.addEventListener("click", () => showDetail(p));

    // Click Add to Cart button:
    //  - if the product has multiple variants, user MUST pick one → open detail modal
    //  - if one (or none), add directly
    card.querySelector(".btn-cart-sm")!.addEventListener("click", (e) => {
      e.stopPropagation();
      const variants = p.variants || [];
      if (variants.length > 1) {
        showDetail(p);
        return;
      }
      const only = variants[0];
      const vid = only?.id || p.id;
      const vname = only?.name || "Default";
      addToCart(p, vid, vname);
    });

    productGrid.appendChild(card);
  }
}

// ═══════════════════════════════════════════════════
// Product Detail Modal
// ═══════════════════════════════════════════════════
function formatPrice(pricing?: { amount: number; currency: string }): string {
  if (!pricing) return "N/A";
  return `$${pricing.amount.toFixed(2)} ${pricing.currency}`;
}

function showDetail(product: Product) {
  document.getElementById("detail-name")!.textContent = product.name;

  // Image (if product has a thumbnail)
  const imgWrap = document.getElementById("detail-image-wrap")!;
  const imgEl = document.getElementById("detail-image") as HTMLImageElement;
  if (product.thumbnail?.url) {
    imgEl.src = product.thumbnail.url;
    imgEl.alt = product.name;
    imgWrap.style.display = "flex";
  } else {
    imgEl.removeAttribute("src");
    imgWrap.style.display = "none";
  }

  // Description may be EditorJS JSON, or a raw HTML string, or plain text.
  // Strip HTML tags (Saleor often inlines <b>/<i> in paragraph text).
  const htmlToPlain = (s: string) => {
    const tmp = document.createElement("div");
    tmp.innerHTML = s;
    return (tmp.textContent || "").trim();
  };
  let desc = product.description || "";
  try {
    const parsed = JSON.parse(desc);
    if (parsed?.blocks) {
      desc = parsed.blocks.map((b: any) => b?.data?.text || "").join("\n");
    }
  } catch { /* not JSON — treat as HTML/text */ }
  desc = htmlToPlain(desc);
  document.getElementById("detail-desc")!.textContent = desc || "No description";

  const priceEl = document.getElementById("detail-price")!;
  const skuEl = document.getElementById("detail-sku")!;

  const variants = product.variants || [];

  // Update price + SKU display based on the currently selected variant.
  // Falls back to the product's price range when no variant is picked.
  const refreshForVariant = (v: Variant | null) => {
    if (v) {
      priceEl.textContent = formatPrice(v.pricing || product.pricing);
      skuEl.textContent = v.sku ? `SKU: ${v.sku}` : "";
    } else {
      priceEl.textContent = formatPrice(product.pricing);
      skuEl.textContent = "";
    }
  };

  const variantList = document.getElementById("variant-list")!;
  variantList.innerHTML = "";
  selectedVariantId = null;

  if (variants.length > 0) {
    selectedVariantId = variants[0].id;
    for (let i = 0; i < variants.length; i++) {
      const v = variants[i];
      const btn = document.createElement("button");
      btn.className = "btn-secondary variant-btn" + (i === 0 ? " active" : "");
      // Show variant name + its own price if distinct from product display
      const priceTxt = v.pricing ? ` · $${v.pricing.amount.toFixed(2)}` : "";
      btn.textContent = `${v.name || "Default"}${priceTxt}`;
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        selectedVariantId = v.id;
        variantList.querySelectorAll(".variant-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        refreshForVariant(v);
      });
      variantList.appendChild(btn);
    }
    refreshForVariant(variants[0]);
  } else {
    selectedVariantId = product.id;
    variantList.innerHTML = '<span style="font-size:11px;color:var(--text-muted);">Default variant</span>';
    refreshForVariant(null);
  }

  const addBtn = document.getElementById("add-cart-btn")! as HTMLButtonElement;
  addBtn.textContent = "Add to Cart";
  addBtn.disabled = false;
  addBtn.className = "btn-primary btn-full";
  addBtn.onclick = () => {
    const vid = selectedVariantId || product.id;
    const vname = variants.find(v => v.id === vid)?.name || "Default";
    // Sync the product's pricing to the picked variant's price for the local
    // cart line so the subtotal reflects the actual variant.
    const pickedVariant = variants.find(v => v.id === vid);
    const productForCart: Product = pickedVariant?.pricing
      ? { ...product, pricing: pickedVariant.pricing }
      : product;
    addToCart(productForCart, vid, vname);
    addBtn.textContent = "✓ Added!";
    addBtn.className = "btn-success";
    setTimeout(() => {
      addBtn.textContent = "Add to Cart";
      addBtn.className = "btn-primary btn-full";
    }, 800);
  };

  showView("detail");
}

// ═══════════════════════════════════════════════════
// Render: Cart View
// ═══════════════════════════════════════════════════
function renderCartView(checkout?: any) {
  if (checkout) {
    if (checkout.id) saveCheckoutId(checkout.id);
    // Reset local cart to mirror server (so badge + fallback stay accurate)
    if (Array.isArray(checkout.lines)) {
      cart.length = 0;
      for (const line of checkout.lines) {
        cart.push({
          product: { id: "", name: line.productName || "Product" },
          variantId: "",
          variantName: line.variantName || "",
          quantity: line.quantity || 0,
        });
      }
      saveCart();
      updateCartBadge();
    }
    renderCartFromCheckout(checkout);
    return;
  }
  renderCartFromLocal();
}

function renderCartFromLocal() {
  const cartLines = document.getElementById("cart-lines")!;
  const cartSummary = document.getElementById("cart-summary")!;
  cartLines.innerHTML = "";

  if (cart.length === 0) {
    cartLines.innerHTML = '<div class="loading">Your cart is empty.</div>';
    cartSummary.innerHTML = "";
    return;
  }

  let subtotal = 0;
  let currency = "USD";

  for (const item of cart) {
    const p = item.product;
    const unitPrice = p.pricing?.amount || 0;
    currency = p.pricing?.currency || "USD";
    const lineTotal = unitPrice * item.quantity;
    subtotal += lineTotal;

    const line = document.createElement("div");
    line.className = "cart-line";
    const imgUrl = p.thumbnail?.url;
    line.innerHTML = `
      ${imgUrl ? `<img class="cart-line-img" src="${imgUrl}" alt="${p.name}">` : '<div class="cart-line-img" style="display:flex;align-items:center;justify-content:center;font-size:10px;color:var(--text-muted);">No img</div>'}
      <div class="cart-line-info">
        <div class="cart-line-name">${p.name}</div>
        <div class="cart-line-variant">${item.variantName}</div>
        <div class="cart-line-price">$${unitPrice.toFixed(2)} × ${item.quantity} = $${lineTotal.toFixed(2)}</div>
      </div>
      <div class="qty-controls">
        <button class="btn-secondary qty-btn qty-minus">−</button>
        <span class="qty-val">${item.quantity}</span>
        <button class="btn-secondary qty-btn qty-plus">+</button>
      </div>
    `;

    line.querySelector(".qty-plus")!.addEventListener("click", () => {
      item.quantity++;
      saveCart();
      updateCartBadge();
      renderCartFromLocal();
    });
    line.querySelector(".qty-minus")!.addEventListener("click", () => {
      item.quantity--;
      if (item.quantity <= 0) {
        const idx = cart.indexOf(item);
        if (idx >= 0) cart.splice(idx, 1);
      }
      saveCart();
      updateCartBadge();
      renderCartFromLocal();
    });

    cartLines.appendChild(line);
  }

  cartSummary.innerHTML = `
    <div class="summary-row"><span>Subtotal</span><span>$${subtotal.toFixed(2)} ${currency}</span></div>
    <div class="summary-row summary-total"><span>Total</span><span>$${subtotal.toFixed(2)} ${currency}</span></div>
    <button class="btn-primary btn-full" id="checkout-btn">Proceed to Checkout</button>
  `;
  document.getElementById("checkout-btn")!.addEventListener("click", () => goToCheckout());
}

function renderCartFromCheckout(checkout: any) {
  const cartLines = document.getElementById("cart-lines")!;
  const cartSummary = document.getElementById("cart-summary")!;
  cartLines.innerHTML = "";

  if (!checkout.lines || checkout.lines.length === 0) {
    cartLines.innerHTML = '<div class="loading">Your cart is empty.</div>';
    cartSummary.innerHTML = "";
    return;
  }

  for (const line of checkout.lines) {
    const el = document.createElement("div");
    el.className = "cart-line";
    const imgUrl = line.thumbnail;
    el.innerHTML = `
      ${imgUrl ? `<img class="cart-line-img" src="${imgUrl}" alt="${line.productName}">` : '<div class="cart-line-img" style="display:flex;align-items:center;justify-content:center;font-size:10px;color:var(--text-muted);">No img</div>'}
      <div class="cart-line-info">
        <div class="cart-line-name">${line.productName}</div>
        <div class="cart-line-variant">${line.variantName || ""}</div>
      </div>
      <div class="qty-controls">
        <button class="btn-secondary qty-btn qty-minus">−</button>
        <span class="qty-val">${line.quantity}</span>
        <button class="btn-secondary qty-btn qty-plus">+</button>
      </div>
    `;
    const plusBtn = el.querySelector(".qty-plus") as HTMLButtonElement;
    const minusBtn = el.querySelector(".qty-minus") as HTMLButtonElement;
    plusBtn.addEventListener("click", () => changeQty(line.id, line.quantity + 1, [plusBtn, minusBtn]));
    minusBtn.addEventListener("click", () => changeQty(line.id, line.quantity - 1, [plusBtn, minusBtn]));
    cartLines.appendChild(el);
  }

  const total = checkout.total || { amount: 0, currency: "USD" };
  cartSummary.innerHTML = `
    <div class="summary-row summary-total"><span>Total</span><span>$${total.amount.toFixed(2)} ${total.currency}</span></div>
    <button class="btn-primary btn-full" id="checkout-btn">Proceed to Checkout</button>
  `;
  document.getElementById("checkout-btn")!.addEventListener("click", () => goToCheckout());
}

async function changeQty(lineId: string, newQty: number, buttons: HTMLButtonElement[]) {
  buttons.forEach(b => b.disabled = true);
  statusBar.textContent = "🔄 Updating cart...";
  try {
    if (newQty <= 0) {
      await serverRemoveCartLine(lineId);
    } else {
      await serverUpdateCartItem(lineId, newQty);
    }
    const checkout = await fetchServerCart();
    if (checkout) {
      renderCartView(checkout);
      statusBar.textContent = "🛒 Cart updated";
    } else {
      renderCartFromLocal();
    }
    void syncCartToModelContext();
  } catch (err: any) {
    console.error("changeQty failed:", err);
    showToast(`❌ ${err.message || "Update failed"}`, 3000, true);
    statusBar.textContent = "❌ Update failed";
    buttons.forEach(b => b.disabled = false);
  }
}

async function goToCheckout() {
  if (!currentCheckoutId) {
    // No server checkout yet → ask Claude to create one from local cart
    statusBar.textContent = "🔄 Requesting checkout from Claude...";
    await app.sendMessage({
      role: "user",
      content: [{
        type: "text",
        text: `Tôi muốn thanh toán các sản phẩm trong giỏ hàng: ${cart.map(i => `${i.quantity}x ${i.variantName || i.product.name}`).join(", ")}. Hãy tạo checkout.`,
      }],
    });
    return;
  }
  showView("checkout");
  statusBar.textContent = "📋 Loading checkout...";
  try {
    const res = await callTool("open_checkout", { checkout_id: currentCheckoutId });
    const checkout = res.checkout;
    const lastAddr = JSON.parse(localStorage.getItem("mcp_last_address") || "null");
    renderCheckoutView(checkout, lastAddr);
    statusBar.textContent = "📋 Enter shipping details";
  } catch (err: any) {
    console.error("goToCheckout failed:", err);
    showToast(`❌ ${err.message || "Load checkout failed"}`, 3000, true);
    statusBar.textContent = "❌ Load checkout failed";
  }
}

// ═══════════════════════════════════════════════════
// Render: Checkout View
// ═══════════════════════════════════════════════════
function renderCheckoutView(checkout?: any, prefillAddress?: any) {
  if (checkout?.id) saveCheckoutId(checkout.id);
  const summary = document.getElementById("checkout-summary")!;
  let subtotal = 0;
  let currency = "USD";

  if (checkout?.total) {
    subtotal = checkout.total.amount || 0;
    currency = checkout.total.currency || "USD";
  } else {
    for (const item of cart) {
      subtotal += (item.product.pricing?.amount || 0) * item.quantity;
      currency = item.product.pricing?.currency || currency;
    }
  }

  // Priority: explicit prefill from tool > existing shippingAddress > last saved > empty
  const lastSaved = JSON.parse(localStorage.getItem("mcp_last_address") || "null");
  const addr = prefillAddress || checkout?.shippingAddress || lastSaved || {};
  const setVal = (id: string, val: string) => {
    const el = document.getElementById(id) as HTMLInputElement | HTMLSelectElement | null;
    if (el && val) el.value = val;
  };
  // Email priority: server checkout.email > last used > empty
  const savedEmail = localStorage.getItem("mcp_last_email") || "";
  setVal("ship-email", checkout?.email || savedEmail || "");
  setVal("ship-firstName", addr.firstName || "");
  setVal("ship-lastName", addr.lastName || "");
  setVal("ship-street", addr.streetAddress1 || "");
  setVal("ship-city", addr.city || "");
  setVal("ship-postalCode", addr.postalCode || "");
  setVal("ship-country", addr.country || "VN");
  setVal("ship-phone", addr.phone || "");

  // Render shipping methods — auto-select previously chosen, else the first one
  const methodList = document.getElementById("shipping-method-list")!;
  methodList.innerHTML = "";
  const methods = checkout?.shippingMethods || [];
  const preselected = checkout?.selectedShippingMethodId
    || (methods.length > 0 ? methods[0].id : null);
  if (methods.length > 0) {
    for (const m of methods) {
      const checked = m.id === preselected ? "checked" : "";
      const label = document.createElement("label");
      label.innerHTML = `<input type="radio" name="shipping-method" value="${m.id}" ${checked}> ${m.name} — $${m.price.toFixed(2)}`;
      methodList.appendChild(label);
    }
  } else {
    methodList.innerHTML = '<div style="font-size:12px;color:var(--text-muted);">Save address first to see shipping options</div>';
  }

  summary.innerHTML = `
    <div class="summary-row"><span>Items (${cart.reduce((s, i) => s + i.quantity, 0)})</span><span>$${subtotal.toFixed(2)} ${currency}</span></div>
    <div class="summary-row summary-total"><span>Total</span><span>$${subtotal.toFixed(2)} ${currency}</span></div>
  `;

  // Dynamic button label: first click saves address; second click (with method chosen) pays.
  const payBtn = document.getElementById("pay-now-btn") as HTMLButtonElement;
  payBtn.disabled = false;
  payBtn.textContent = methods.length > 0 ? "Confirm & Pay" : "Save Address";
}

// ═══════════════════════════════════════════════════
// Render: Payment View (placeholder for Phase 4)
// ═══════════════════════════════════════════════════
function renderPaymentView(payment?: any) {
  const el = document.getElementById("payment-content")!;
  if (payment) {
    el.innerHTML = `
      <div class="summary-box">
        <h3 style="margin-bottom:12px;">💳 Payment</h3>
        <div class="summary-row"><span>Order</span><span>${payment.orderId || currentCheckoutId || "—"}</span></div>
        <div class="summary-row"><span>Amount</span><span>${payment.amount || "—"}</span></div>
        <div class="summary-row"><span>Status</span><span>${payment.status || "Awaiting payment"}</span></div>
        <div style="text-align:center;padding:20px;color:var(--text-muted);">SePay QR integration — coming in Phase 4</div>
      </div>
    `;
  } else {
    el.innerHTML = `
      <div class="summary-box">
        <h3 style="margin-bottom:12px;">💳 Payment</h3>
        <div style="text-align:center;padding:20px;color:var(--text-muted);">
          <p>Checkout ID: ${currentCheckoutId || "—"}</p>
          <p style="margin-top:8px;">SePay QR integration — coming in Phase 4</p>
        </div>
      </div>
    `;
  }
}

// ═══════════════════════════════════════════════════
// Render: Order View (placeholder for Phase 5)
// ═══════════════════════════════════════════════════
function renderOrderView(order?: any) {
  const el = document.getElementById("order-content")!;
  if (!order) {
    el.innerHTML = '<div class="loading">No order data</div>';
    return;
  }
  const total = order.total?.gross
    ? `$${order.total.gross.amount.toFixed(2)} ${order.total.gross.currency}`
    : "—";
  const created = order.created ? new Date(order.created).toLocaleString() : "—";
  el.innerHTML = `
    <div class="summary-box" style="text-align:center;padding:24px 14px;">
      <div style="font-size:44px;margin-bottom:8px;">🎉</div>
      <h3 style="margin-bottom:4px;">Order placed!</h3>
      <div style="color:var(--text-muted);font-size:12px;margin-bottom:16px;">Thank you for shopping with BI193 Store</div>
      <div class="summary-row" style="text-align:left;"><span>Order #</span><span><b>${order.number || order.id || "—"}</b></span></div>
      <div class="summary-row" style="text-align:left;"><span>Status</span><span>${order.status || "—"}</span></div>
      <div class="summary-row" style="text-align:left;"><span>Payment</span><span>${order.paymentStatus || "—"}</span></div>
      <div class="summary-row" style="text-align:left;"><span>Total</span><span><b>${total}</b></span></div>
      <div class="summary-row" style="text-align:left;"><span>Created</span><span>${created}</span></div>
    </div>
  `;
}

// ═══════════════════════════════════════════════════
// Event listeners
// ═══════════════════════════════════════════════════
// Cart badge → open cart view (always sync from server first)
cartBadge.addEventListener("click", async () => {
  showView("cart");
  if (currentCheckoutId) {
    statusBar.textContent = "🛒 Loading cart...";
    try {
      const checkout = await fetchServerCart();
      if (checkout) {
        renderCartView(checkout);
        statusBar.textContent = `🛒 ${checkout.lines?.length || 0} lines`;
        return;
      }
    } catch (err: any) {
      console.error("fetchServerCart failed:", err);
      showToast(`❌ ${err.message || "Load cart failed"}`, 3000, true);
    }
  }
  renderCartFromLocal();
  statusBar.textContent = `🛒 ${cart.reduce((s, i) => s + i.quantity, 0)} items in cart`;
});

// Billing toggle
document.getElementById("same-billing")?.addEventListener("change", (e) => {
  const billingFields = document.getElementById("billing-fields")!;
  billingFields.classList.toggle("hidden", (e.target as HTMLInputElement).checked);
});

// Checkout form submit → call Saleor server tools directly (no natural language)
document.getElementById("checkout-form")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!currentCheckoutId) {
    statusBar.textContent = "❌ No checkout ID";
    showToast("❌ Không có checkout. Hãy thêm sản phẩm vào giỏ trước.", 3000, true);
    return;
  }

  highlightField(null); // clear any previous error highlighting

  const email = (document.getElementById("ship-email") as HTMLInputElement).value.trim();
  const shippingAddress: Record<string, any> = {
    firstName: (document.getElementById("ship-firstName") as HTMLInputElement).value,
    lastName: (document.getElementById("ship-lastName") as HTMLInputElement).value,
    streetAddress1: (document.getElementById("ship-street") as HTMLInputElement).value,
    city: (document.getElementById("ship-city") as HTMLInputElement).value,
    postalCode: (document.getElementById("ship-postalCode") as HTMLInputElement).value,
    country: (document.getElementById("ship-country") as HTMLSelectElement).value,
  };
  const phone = (document.getElementById("ship-phone") as HTMLInputElement).value;
  if (phone) shippingAddress.phone = phone;

  // Persist for next checkout (survives session)
  localStorage.setItem("mcp_last_address", JSON.stringify(shippingAddress));
  if (email) localStorage.setItem("mcp_last_email", email);

  const sameBilling = (document.getElementById("same-billing") as HTMLInputElement).checked;
  const billingAddress: Record<string, any> = sameBilling ? { ...shippingAddress } : {
    firstName: (document.getElementById("bill-firstName") as HTMLInputElement).value,
    lastName: (document.getElementById("bill-lastName") as HTMLInputElement).value,
    streetAddress1: (document.getElementById("bill-street") as HTMLInputElement).value,
    city: (document.getElementById("bill-city") as HTMLInputElement).value,
    postalCode: (document.getElementById("bill-postalCode") as HTMLInputElement).value,
    country: (document.getElementById("bill-country") as HTMLSelectElement).value,
  };

  const selectedMethod = (document.querySelector('input[name="shipping-method"]:checked') as HTMLInputElement | null)?.value;
  const payBtn = document.getElementById("pay-now-btn") as HTMLButtonElement;
  payBtn.disabled = true;

  const runStep = async (
    stepLabel: string,
    name: string,
    args: Record<string, any>,
  ) => {
    statusBar.textContent = `🔄 ${stepLabel}...`;
    const res = await callTool(name, args);
    const errMsg = extractErrors(res);
    if (errMsg) {
      highlightField(fieldFromErrors(res));
      throw new Error(errMsg);
    }
    return res;
  };

  try {
    if (email) {
      await runStep("Saving email", "set_checkout_email", {
        checkout_id: currentCheckoutId,
        email,
      });
    }

    // Step 1: set shipping + billing + (optionally) shipping method in one call
    if (!selectedMethod) {
      await runStep("Saving delivery info", "set_checkout_delivery", {
        checkout_id: currentCheckoutId,
        shipping_address: shippingAddress,
        billing_address: sameBilling ? undefined : billingAddress,
        same_billing: sameBilling,
      });
      // Shipping methods become available only after an address is set.
      statusBar.textContent = "🔄 Loading shipping methods...";
      const r3 = await callTool("open_checkout", { checkout_id: currentCheckoutId });
      renderCheckoutView(r3.checkout);
      statusBar.textContent = "📋 Confirm shipping method and click Pay Now";
      payBtn.disabled = false;
      return;
    }

    await runStep("Saving delivery info", "set_checkout_delivery", {
      checkout_id: currentCheckoutId,
      shipping_address: shippingAddress,
      billing_address: sameBilling ? undefined : billingAddress,
      same_billing: sameBilling,
      shipping_method_id: selectedMethod,
    });

    // Fetch latest checkout to read available payment gateways
    statusBar.textContent = "🔄 Checking payment options...";
    const coRes = await callTool("open_checkout", { checkout_id: currentCheckoutId });
    const gateways = coRes.checkout?.paymentGateways || [];
    if (gateways.length === 0) {
      throw new Error("No payment gateways available — contact store admin");
    }
    const gateway = gateways[0];

    // Step 2: create payment + complete order in one call.
    // Saleor's built-in dummy gateway needs a status token ('charged' = success).
    statusBar.textContent = `🔄 Placing order via ${gateway.name}...`;
    const placeRes = await callTool("place_order", {
      checkout_id: currentCheckoutId,
      gateway_id: gateway.id,
      token: gateway.id === "mirumee.payments.dummy" ? "charged" : undefined,
    });
    const placeErr = extractErrors(placeRes);
    if (placeErr) throw new Error(placeErr);
    const order = placeRes.data;
    if (!order?.id) throw new Error("Order could not be created");

    // Checkout has become an order — reset local cart/checkout state
    const orderId = String(order.number || order.id);
    saveCheckoutId(null);
    cart.length = 0;
    saveCart();
    updateCartBadge();
    // Tell Claude the cart is now empty (checkout was converted to an order).
    void syncCartToModelContext({ force: true });

    showView("order");
    renderOrderView(order);
    statusBar.textContent = `✅ Order #${orderId} placed`;
  } catch (err: any) {
    console.error("Checkout flow failed:", err);
    showToast(`❌ ${err.message || "Checkout failed"}`, 4000, true);
    statusBar.textContent = "❌ " + (err.message || "Failed");
    payBtn.disabled = false;
  }
});
