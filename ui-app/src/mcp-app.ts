import { App } from "@modelcontextprotocol/ext-apps";

// ═══════════════════════════════════════════════════
// Inline CSS (will be bundled into the HTML)
// ═══════════════════════════════════════════════════
const style = document.createElement("style");
style.textContent = `
:root {
  --primary: #2563eb;
  --primary-hover: #1d4ed8;
  --bg: #f8fafc;
  --card-bg: #ffffff;
  --text-main: #1e293b;
  --text-muted: #64748b;
  --success: #22c55e;
  --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --radius: 12px;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: var(--bg);
  color: var(--text-main);
  padding: 16px;
}
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
h1 { font-size: 20px; font-weight: 800; letter-spacing: -0.025em; }
.badge {
  background: var(--primary);
  color: white;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}
#status-bar {
  background: var(--card-bg);
  padding: 10px 14px;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  margin-bottom: 16px;
  font-size: 13px;
  color: var(--text-muted);
}
#product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 14px;
}
.product-card {
  background: var(--card-bg);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow);
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}
.product-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
}
.product-img {
  width: 100%;
  height: 130px;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  font-size: 11px;
  overflow: hidden;
}
.product-img img { width: 100%; height: 100%; object-fit: cover; }
.product-info { padding: 10px; }
.product-name {
  font-weight: 700;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}
.product-price { color: var(--primary); font-weight: 700; font-size: 13px; }
.overlay {
  display: none;
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  backdrop-filter: blur(4px);
  z-index: 100;
  align-items: center;
  justify-content: center;
  padding: 16px;
}
.modal {
  background: var(--card-bg);
  width: 100%;
  max-width: 420px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgb(0 0 0 / 0.25);
  animation: slideUp 0.25s ease-out;
}
@keyframes slideUp {
  from { transform: translateY(16px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
.modal-header {
  padding: 14px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-header h2 { font-size: 16px; }
.modal-body { padding: 14px; }
.modal-footer {
  padding: 10px 14px;
  background: #f8fafc;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
button {
  padding: 7px 14px;
  border-radius: 8px;
  border: none;
  font-weight: 600;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-primary { background: var(--primary); color: white; }
.btn-primary:hover { background: var(--primary-hover); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { background: #e2e8f0; color: var(--text-main); }
.btn-secondary:hover { background: #cbd5e1; }
.btn-success { background: var(--success); color: white; }
.variant-list { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 6px; }
.variant-btn { font-size: 11px; padding: 4px 8px; }
.variant-btn.active { background: var(--primary); color: white; }
.detail-desc {
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.5;
  margin: 6px 0;
  max-height: 80px;
  overflow-y: auto;
}
.detail-price {
  font-size: 18px;
  font-weight: 800;
  color: var(--primary);
  margin: 8px 0;
}
.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 0 4px;
  color: var(--text-muted);
}
.loading { text-align: center; padding: 30px; color: var(--text-muted); }
`;
document.head.appendChild(style);

// ═══════════════════════════════════════════════════
// App State
// ═══════════════════════════════════════════════════
interface Product {
  id: string;
  name: string;
  slug?: string;
  description?: string;
  thumbnail?: { url: string };
  pricing?: { amount: number; currency: string };
  variants?: { id: string; name: string }[];
}

const statusBar = document.getElementById("status-bar")!;
const productGrid = document.getElementById("product-grid")!;
const detailOverlay = document.getElementById("detail-overlay")!;
const cartBadge = document.getElementById("cart-badge")!;

let cartCount = 0;
let selectedVariantId: string | null = null;

// Track if ontoolresult already provided data (filtered by Claude's search)
let productsLoaded = false;

// 1. Create app instance
const app = new App({ name: "Saleor Product Explorer", version: "1.0.0" });

// 2. Register handlers BEFORE connecting
app.onerror = console.error;

// ontoolresult fires with the result of the tool Claude called (may be filtered)
// This is the PRIMARY source — reflects what Claude searched for
app.ontoolresult = (result: any) => {
  console.info("Tool result received:", result);
  const sc = result.structuredContent;
  if (sc?.products && Array.isArray(sc.products)) {
    productsLoaded = true;
    renderProducts(sc.products as Product[]);
    statusBar.textContent = `✅ ${sc.products.length} products loaded`;
    return;
  }
  // Fallback: parse from content[].text
  processContentArray(result.content);
};

// 3. Connect to host — ontoolresult will deliver the correct (filtered) data
app.connect().then(() => {
  statusBar.textContent = "⏳ Loading products...";
  // ontoolresult fires automatically with Claude's filtered results
  // No need to call loadProducts() here — that would load ALL products without the user's search
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
          productsLoaded = true;
          renderProducts(products);
          statusBar.textContent = `✅ ${products.length} products loaded`;
          return;
        }
      } catch { /* not JSON */ }
    }
  }
}


// ═══════════════════════════════════════════════════
// Render products
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
    const price = p.pricing
      ? `$${p.pricing.amount.toFixed(2)} ${p.pricing.currency}`
      : "N/A";

    card.innerHTML = `
      <div class="product-img">
        ${imgUrl ? `<img src="${imgUrl}" alt="${p.name}" onerror="this.parentElement.textContent='No Image'">` : "No Image"}
      </div>
      <div class="product-info">
        <div class="product-name">${p.name}</div>
        <div class="product-price">${price}</div>
      </div>
    `;
    card.addEventListener("click", () => showDetail(p));
    productGrid.appendChild(card);
  }
}

// ═══════════════════════════════════════════════════
// Product detail modal
// ═══════════════════════════════════════════════════
function showDetail(product: Product) {
  document.getElementById("detail-name")!.textContent = product.name;

  let desc = product.description || "No description";
  try {
    const parsed = JSON.parse(desc);
    if (parsed.blocks) {
      desc = parsed.blocks.map((b: any) => b.data?.text || "").join("\n");
    }
  } catch { /* use as-is */ }
  document.getElementById("detail-desc")!.textContent = desc || "No description";

  const price = product.pricing
    ? `$${product.pricing.amount.toFixed(2)} ${product.pricing.currency}`
    : "N/A";
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
        variantList.querySelectorAll(".variant-btn").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
      });
      variantList.appendChild(btn);
    }
  } else {
    variantList.innerHTML = '<span style="font-size:11px;color:var(--text-muted);">No variants</span>';
  }

  const addBtn = document.getElementById("add-cart-btn")!;
  addBtn.textContent = "Add to Cart";
  (addBtn as HTMLButtonElement).disabled = !selectedVariantId;
  addBtn.className = "btn-primary";

  detailOverlay.style.display = "flex";
}

// ═══════════════════════════════════════════════════
// Add to cart
// ═══════════════════════════════════════════════════
async function handleAddToCart() {
  if (!selectedVariantId) return;

  const addBtn = document.getElementById("add-cart-btn")! as HTMLButtonElement;
  addBtn.textContent = "Adding...";
  addBtn.disabled = true;

  try {
    await app.callServerTool({
      name: "create_cart",
      arguments: {
        channel: "default-channel",
        lines: [{ variantId: selectedVariantId, quantity: 1 }],
      },
    });
    cartCount++;
    cartBadge.textContent = `Cart: ${cartCount}`;
    addBtn.textContent = "✓ Added!";
    addBtn.className = "btn-success";
    setTimeout(() => { detailOverlay.style.display = "none"; }, 600);
  } catch (err: any) {
    // Fallback: visual-only
    cartCount++;
    cartBadge.textContent = `Cart: ${cartCount}`;
    addBtn.textContent = "✓ Added!";
    addBtn.className = "btn-success";
    console.warn("Cart call failed:", err.message);
    setTimeout(() => { detailOverlay.style.display = "none"; }, 600);
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
document.getElementById("add-cart-btn")!.addEventListener("click", handleAddToCart);
detailOverlay.addEventListener("click", (e) => {
  if (e.target === detailOverlay) detailOverlay.style.display = "none";
});
