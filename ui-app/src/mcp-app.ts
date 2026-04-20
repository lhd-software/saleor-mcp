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
.toast { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: var(--success); color: white; padding: 8px 20px; border-radius: 20px; font-size: 13px; font-weight: 600; z-index: 200; animation: fadeInUp 0.3s ease-out; }
@keyframes fadeInUp { from { opacity: 0; transform: translateX(-50%) translateY(10px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }
`;
document.head.appendChild(style);

// ═══════════════════════════════════════════════════
// Types & State
// ═══════════════════════════════════════════════════
interface Product {
  id: string; name: string; slug?: string; description?: string;
  thumbnail?: { url: string }; pricing?: { amount: number; currency: string };
  variants?: { id: string; name: string }[];
}
interface CartItem {
  product: Product; variantId: string; variantName: string; quantity: number;
}

type ViewName = "products" | "cart" | "checkout" | "payment" | "order";

const cart: CartItem[] = [];
let currentView: ViewName = "products";
let selectedVariantId: string | null = null;
let currentCheckoutId: string | null = null;

// ═══════════════════════════════════════════════════
// DOM refs
// ═══════════════════════════════════════════════════
const statusBar = document.getElementById("status-bar")!;
const productGrid = document.getElementById("product-grid")!;
const detailOverlay = document.getElementById("detail-overlay")!;
const cartBadge = document.getElementById("cart-badge")!;
const breadcrumb = document.getElementById("breadcrumb")!;

// ═══════════════════════════════════════════════════
// Router
// ═══════════════════════════════════════════════════
function showView(name: ViewName) {
  currentView = name;
  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  document.getElementById(`view-${name}`)?.classList.add("active");
  updateBreadcrumb(name);
}

const CRUMB_ORDER: ViewName[] = ["products", "cart", "checkout", "payment", "order"];
const CRUMB_LABELS: Record<ViewName, string> = {
  products: "Products", cart: "Cart", checkout: "Checkout", payment: "Payment", order: "Order"
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
function showToast(msg: string, duration = 1500) {
  const t = document.createElement("div");
  t.className = "toast";
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

function addToCart(product: Product, variantId: string, variantName: string) {
  const existing = cart.find(i => i.variantId === variantId);
  if (existing) {
    existing.quantity++;
  } else {
    cart.push({ product, variantId, variantName, quantity: 1 });
  }
  updateCartBadge();
  showToast(`✓ ${product.name} added`);
}

// ═══════════════════════════════════════════════════
// MCP App
// ═══════════════════════════════════════════════════
const app = new App({ name: "BI193 Store", version: "2.0.0" });
app.onerror = console.error;

app.ontoolresult = (result: any) => {
  console.info("Tool result:", result);
  const sc = result.structuredContent;
  if (!sc) {
    processContentArray(result.content);
    return;
  }
  switch (sc.view) {
    case "products":
      showView("products");
      renderProducts(sc.products as Product[]);
      statusBar.textContent = `✅ ${sc.products?.length || 0} products loaded`;
      break;
    case "cart":
      showView("cart");
      renderCartView(sc.checkout);
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
      // Legacy: no view field — assume products
      if (sc.products && Array.isArray(sc.products)) {
        showView("products");
        renderProducts(sc.products as Product[]);
        statusBar.textContent = `✅ ${sc.products.length} products loaded`;
      }
  }
};

app.connect().then(() => {
  statusBar.textContent = "⏳ Loading products...";
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

    // Click Add to Cart button → quick add (first variant or product id)
    card.querySelector(".btn-cart-sm")!.addEventListener("click", (e) => {
      e.stopPropagation();
      const vid = p.variants?.[0]?.id || p.id;
      const vname = p.variants?.[0]?.name || "Default";
      addToCart(p, vid, vname);
    });

    productGrid.appendChild(card);
  }
}

// ═══════════════════════════════════════════════════
// Product Detail Modal
// ═══════════════════════════════════════════════════
function showDetail(product: Product) {
  document.getElementById("detail-name")!.textContent = product.name;

  let desc = product.description || "No description";
  try {
    const parsed = JSON.parse(desc);
    if (parsed.blocks) desc = parsed.blocks.map((b: any) => b.data?.text || "").join("\n");
  } catch { /* use as-is */ }
  document.getElementById("detail-desc")!.textContent = desc || "No description";

  const price = product.pricing ? `$${product.pricing.amount.toFixed(2)} ${product.pricing.currency}` : "N/A";
  document.getElementById("detail-price")!.textContent = price;

  const variantList = document.getElementById("variant-list")!;
  variantList.innerHTML = "";
  selectedVariantId = null;

  const variants = product.variants || [];
  if (variants.length > 0) {
    selectedVariantId = variants[0].id;
    for (let i = 0; i < variants.length; i++) {
      const v = variants[i];
      const btn = document.createElement("button");
      btn.className = "btn-secondary variant-btn" + (i === 0 ? " active" : "");
      btn.textContent = v.name || "Default";
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        selectedVariantId = v.id;
        variantList.querySelectorAll(".variant-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
      });
      variantList.appendChild(btn);
    }
  } else {
    selectedVariantId = product.id;
    variantList.innerHTML = '<span style="font-size:11px;color:var(--text-muted);">Default variant</span>';
  }

  const addBtn = document.getElementById("add-cart-btn")! as HTMLButtonElement;
  addBtn.textContent = "Add to Cart";
  addBtn.disabled = false;
  addBtn.className = "btn-primary";
  addBtn.onclick = () => {
    const vid = selectedVariantId || product.id;
    const vname = variants.find(v => v.id === vid)?.name || "Default";
    addToCart(product, vid, vname);
    addBtn.textContent = "✓ Added!";
    addBtn.className = "btn-success";
    setTimeout(() => { detailOverlay.style.display = "none"; }, 500);
  };

  detailOverlay.style.display = "flex";
}

// ═══════════════════════════════════════════════════
// Render: Cart View
// ═══════════════════════════════════════════════════
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
      updateCartBadge();
      renderCartFromLocal();
    });
    line.querySelector(".qty-minus")!.addEventListener("click", () => {
      item.quantity--;
      if (item.quantity <= 0) {
        const idx = cart.indexOf(item);
        if (idx >= 0) cart.splice(idx, 1);
      }
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
  document.getElementById("checkout-btn")!.addEventListener("click", async () => {
    const btn = document.getElementById("checkout-btn")! as HTMLButtonElement;
    btn.textContent = "Creating checkout...";
    btn.disabled = true;

    try {
      // Create Saleor checkout with local cart items
      const lines = cart.map(item => ({ variantId: item.variantId, quantity: item.quantity }));
      const result = await app.callServerTool({
        name: "create_cart",
        arguments: { channel: "default-channel", lines },
      });
      const sc = (result as any).structuredContent;
      const data = sc?.data || sc;
      if (data?.id) {
        currentCheckoutId = data.id;
        showView("checkout");
        renderCheckoutView(data);
        statusBar.textContent = "📋 Fill in your details";
      } else {
        btn.textContent = "Retry";
        btn.disabled = false;
        statusBar.textContent = "❌ Checkout creation failed";
      }
    } catch (err: any) {
      console.error("create_cart failed:", err);
      btn.textContent = "Retry";
      btn.disabled = false;
      statusBar.textContent = "❌ " + err.message;
    }
  });
}

function renderCartView(checkout?: any) {
  if (checkout) {
    // If Saleor checkout data provided, could render from that
    // For now, still use local cart
    if (checkout.id) currentCheckoutId = checkout.id;
  }
  renderCartFromLocal();
}

// ═══════════════════════════════════════════════════
// Render: Checkout View
// ═══════════════════════════════════════════════════
function renderCheckoutView(checkout?: any, prefillAddress?: any) {
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

  // Pre-fill address fields — priority: prefillAddress > existing shippingAddress > empty
  const addr = prefillAddress || checkout?.shippingAddress || {};
  const setVal = (id: string, val: string) => {
    const el = document.getElementById(id) as HTMLInputElement | HTMLSelectElement | null;
    if (el && val) el.value = val;
  };
  setVal("ship-firstName", addr.firstName || "");
  setVal("ship-lastName", addr.lastName || "");
  setVal("ship-street", addr.streetAddress1 || "");
  setVal("ship-city", addr.city || "");
  setVal("ship-postalCode", addr.postalCode || "");
  setVal("ship-country", addr.country || "VN");
  setVal("ship-phone", addr.phone || "");

  // Render shipping methods if available
  const methodList = document.getElementById("shipping-method-list")!;
  methodList.innerHTML = "";
  if (checkout?.shippingMethods && checkout.shippingMethods.length > 0) {
    for (const m of checkout.shippingMethods) {
      const label = document.createElement("label");
      label.innerHTML = `<input type="radio" name="shipping-method" value="${m.id}"> ${m.name} — $${m.price.toFixed(2)}`;
      methodList.appendChild(label);
    }
  } else {
    methodList.innerHTML = '<div style="font-size:12px;color:var(--text-muted);">Set shipping address first to see available methods</div>';
  }

  summary.innerHTML = `
    <div class="summary-row"><span>Items (${cart.reduce((s, i) => s + i.quantity, 0)})</span><span>$${subtotal.toFixed(2)} ${currency}</span></div>
    <div class="summary-row summary-total"><span>Total</span><span>$${subtotal.toFixed(2)} ${currency}</span></div>
  `;
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
  if (order) {
    el.innerHTML = `
      <div class="summary-box">
        <h3 style="margin-bottom:12px;">📦 Order ${order.number || order.id || ""}</h3>
        <div class="summary-row"><span>Status</span><span>${order.status || "—"}</span></div>
        <div class="summary-row"><span>Payment</span><span>${order.paymentStatus || "—"}</span></div>
        <div class="summary-row"><span>Created</span><span>${order.created || "—"}</span></div>
      </div>
    `;
  } else {
    el.innerHTML = '<div class="loading">No order data</div>';
  }
}

// ═══════════════════════════════════════════════════
// Event listeners
// ═══════════════════════════════════════════════════
document.getElementById("close-modal")!.addEventListener("click", () => {
  detailOverlay.style.display = "none";
});
document.getElementById("close-modal-2")!.addEventListener("click", () => {
  detailOverlay.style.display = "none";
});
detailOverlay.addEventListener("click", (e) => {
  if (e.target === detailOverlay) detailOverlay.style.display = "none";
});

// Cart badge → open cart view
cartBadge.addEventListener("click", () => {
  showView("cart");
  renderCartFromLocal();
  statusBar.textContent = `🛒 ${cart.reduce((s, i) => s + i.quantity, 0)} items in cart`;
});

// Billing toggle
document.getElementById("same-billing")?.addEventListener("change", (e) => {
  const billingFields = document.getElementById("billing-fields")!;
  billingFields.classList.toggle("hidden", (e.target as HTMLInputElement).checked);
});

// Checkout form submit → call Saleor APIs
document.getElementById("checkout-form")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!currentCheckoutId) {
    statusBar.textContent = "❌ No checkout ID";
    return;
  }

  const payBtn = document.getElementById("pay-now-btn")! as HTMLButtonElement;
  payBtn.textContent = "Processing...";
  payBtn.disabled = true;

  try {
    // 1. Set shipping address
    const shippingAddress = {
      firstName: (document.getElementById("ship-firstName") as HTMLInputElement).value,
      lastName: (document.getElementById("ship-lastName") as HTMLInputElement).value,
      streetAddress1: (document.getElementById("ship-street") as HTMLInputElement).value,
      city: (document.getElementById("ship-city") as HTMLInputElement).value,
      postalCode: (document.getElementById("ship-postalCode") as HTMLInputElement).value,
      country: (document.getElementById("ship-country") as HTMLSelectElement).value,
      phone: (document.getElementById("ship-phone") as HTMLInputElement).value || undefined,
    };

    await app.callServerTool({
      name: "set_shipping_address",
      arguments: { checkout_id: currentCheckoutId, shipping_address: shippingAddress },
    });

    // 2. Set billing address
    const sameBilling = (document.getElementById("same-billing") as HTMLInputElement).checked;
    const billingAddress = sameBilling ? shippingAddress : {
      firstName: (document.getElementById("bill-firstName") as HTMLInputElement).value,
      lastName: (document.getElementById("bill-lastName") as HTMLInputElement).value,
      streetAddress1: (document.getElementById("bill-street") as HTMLInputElement).value,
      city: (document.getElementById("bill-city") as HTMLInputElement).value,
      postalCode: (document.getElementById("bill-postalCode") as HTMLInputElement).value,
      country: (document.getElementById("bill-country") as HTMLSelectElement).value,
    };

    await app.callServerTool({
      name: "set_billing_address",
      arguments: { checkout_id: currentCheckoutId, billing_address: billingAddress },
    });

    // 3. Set shipping method if selected
    const selectedMethod = document.querySelector('input[name="shipping-method"]:checked') as HTMLInputElement | null;
    if (selectedMethod) {
      await app.callServerTool({
        name: "set_shipping_method",
        arguments: { checkout_id: currentCheckoutId, shipping_method_id: selectedMethod.value },
      });
    }

    // 4. Navigate to payment
    showView("payment");
    statusBar.textContent = "💳 Complete your payment";
    renderPaymentView();

  } catch (err: any) {
    console.error("Checkout submit failed:", err);
    payBtn.textContent = "Retry";
    payBtn.disabled = false;
    statusBar.textContent = "❌ " + err.message;
  }
});
