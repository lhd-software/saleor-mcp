# PRD: MCP Client for Saleor-based Agentic E‑commerce

## Product context
Model Context Protocol (MCP) is used as the standard interface for AI agents to access catalog, cart, checkout and other structured commerce capabilities.[cite:192] In this product, Saleor is the core e‑commerce engine that exposes a GraphQL API for products, checkout, orders, promotions, shipping and payments, while the MCP client provides an AI‑first experience for shoppers on top of Saleor.[cite:184][cite:180][cite:179]

## Product goals
- Let shoppers describe what they want to buy in natural language and reliably find matching products from a Saleor catalog, across channels if needed.[cite:191][cite:184]
- Help shoppers select the **best** option according to their own criteria (budget, brand, size, delivery speed, reviews, bundled value), not just the cheapest SKU.[cite:193]
- Automatically combine promotions, vouchers and bundles from Saleor so the shopper gets the **best total value**, e.g. using bundles, free‑shipping thresholds or subscription discounts.[cite:179][cite:183][cite:187]
- Support add‑to‑cart, checkout creation, safe payment flows and post‑purchase flows such as tracking, returns and refunds via Saleor.

## Target users
### End customers
Consumers who want to shop via chat or embedded AI UI instead of manually browsing category pages. They expect the agent to search, compare, optimize promotions and complete the purchase with minimal friction.[cite:193]

### Merchants
Stores that run on Saleor and want to expose their catalog, prices, promotions and orders to AI agents through a standardized MCP layer, without duplicating commerce logic.[cite:198]

### Channels / AI hosts
Channels such as web chat widgets, Telegram bots + Mini Apps, Claude/ChatGPT style apps or custom assistants that need a ready‑made commerce client which maps user actions to safe MCP + Saleor calls.[cite:192]

## Functional scope
| Area | Description | Priority |
|---|---|---|
| Product discovery | Natural language search, filters, ranking, explanations | Must‑have |
| Value optimization | Promotions, vouchers, bundles, free‑shipping thresholds, substitution suggestions | Must‑have |
| Purchase interaction | Variant selection, quantity, add to cart, update cart | Must‑have |
| Checkout | Create/update/complete checkout, handoff to trusted payment UI | Must‑have |
| Order tracking | Track order / shipment / delivery status | Must‑have |
| Returns & refunds | Start a return/refund, check eligibility and status | Should‑have |
| UI layer | Product cards, images, cart summary, CTAs, safe fallbacks | Must‑have |
| Multichannel | Web, mobile, Telegram, AI hosts with or without rich UI | Should‑have |

## Core use cases
### 1. Search by intent
The shopper can type requests such as "cheap running shoes under 80 USD delivered this week" or "best low‑sugar milk for kids under 500k VND". The agent must translate this intent into Saleor product queries (channel‑aware, with filters) and return relevant results.[cite:191][cite:184]

### 2. Pick the best product for *this* shopper
The client must:
- Clarify missing preferences (size, color, budget, delivery deadline, brand affinity).
- Remember session‑level preferences when possible.
- Rank products by a score that reflects the shopper's stated objective (cheapest, best value, fastest delivery, premium brand, etc.).
- Explain **why** a given product is recommended and offer at least one alternative with a different trade‑off.

### 3. Optimize cart for value
Using Saleor promotions and vouchers, the client should:
- Compute final payable amount including catalogue promotions, cart rules, vouchers, and shipping discounts.[cite:179][cite:183]
- Suggest cart changes that improve value: add items to reach free‑shipping, switch to bundle, choose subscription, or replace a product by a promotional equivalent.[cite:187]
- Let the shopper choose the optimization objective: "lowest total", "best value", "fastest delivery" or similar.

### 4. Place order and pay
Once the shopper confirms their choices, the client must:
- Maintain a Saleor checkout instance per session (lines, shipping address, shipping method, channel).[cite:180]
- Support updates (add/remove/update lines, change shipping method, add voucher code).
- Trigger checkout completion, which converts the checkout to an order in Saleor, or hand off to a trusted payment UI if sensitive data entry is required.[cite:178][cite:190]

### 5. Post‑purchase support
The client must:
- Look up order and fulfillment status (packed, shipped, out for delivery, delivered, failed, returned).[cite:198]
- Answer "where is my order?" with natural‑language explanations based on Saleor order and fulfillment data.
- Start a return/refund where allowed and surface the current refund status using Saleor refunds/payments API.[cite:186][cite:178]

## Functional requirements
### 1. Search & discovery
- Support natural language and structured search mapped to Saleor `products` and related queries, including channel, price range, categories, attributes, availability, rating and delivery constraints.[cite:184][cite:194]
- Allow searching a single Saleor channel or multiple channels, depending on configuration.
- Return product cards with image, price, key attributes and primary CTA.

### 2. Recommendation & ranking
- Implement scoring per product using signals like price fit, promotion benefit, availability per channel, shipping ETA and brand preference.
- Use session preferences (budget, typical sizes, preferred brands) when available.
- Always provide a short explanation for the top recommendation and offer 1‑2 alternatives with different trade‑offs.

### 3. Promotion optimizer
- Integrate with Saleor's promotion engine and vouchers:
  - Catalogue promotions affecting product pricing.
  - Cart‑level promotions and rules.
  - Vouchers applied to the checkout.[cite:179][cite:183][cite:187]
- Compute and present both "raw" prices and "final" prices after promotions and vouchers.
- Suggest cart changes that increase value under the chosen objective (e.g. add a low‑price item to unlock free shipping).

### 4. Cart & checkout
- Map cart interactions to Saleor Checkout API:
  - Create checkout for the active channel (`checkoutCreate`).
  - Add, update and remove lines (`checkoutLinesAdd`, `checkoutLinesUpdate`, `checkoutLinesDelete`).
  - Set shipping address, billing address and shipping method.
  - Apply vouchers/promo codes at checkout level.[cite:180]
- Maintain checkout state per user/session in the orchestration layer.

### 5. Payments
- Use Saleor's payment/transaction abstraction and payment gateway integrations:
  - Support typical flows such as authorize + capture, charge, void, refund.
  - Keep payment and refund status in sync with Saleor via transactions API or webhooks.[cite:178][cite:190]
- Avoid collecting raw card or wallet data inside the AI chat; rely on hosted payment pages or PCI‑compliant UIs.

### 6. Order tracking
- Retrieve orders and fulfillment events from Saleor to answer tracking questions.
- Map Saleor fulfillment statuses into simple messages: e.g., "Processing", "Shipped", "Out for delivery", "Delivered", "Delivery failed".

### 7. Returns and refunds
- Check return/refund eligibility based on order state, configured policies and payment status.
- Call Saleor refund actions (e.g. `transactionRequestAction` with REFUND) to initiate refunds.[cite:186]
- Show current refund status (requested, in progress, completed, failed) and next steps to the shopper.

### 8. UI & interaction layer
- For rich hosts (web, apps, MCP Apps‑capable UIs): render product cards, image galleries, variant selectors, cart and checkout prompts via dedicated UI components.
- For limited hosts (plain chat, SMS, some messaging platforms): degrade gracefully to text + images + buttons/links, while keeping the same underlying MCP + Saleor flows.[cite:192]

## Minimum MCP capabilities (mapped to Saleor)
| MCP capability | Implementation on Saleor | Purpose |
|---|---|---|
| `search_products` | Proxy Saleor `products` query (with channel, filters, search text) | Find products by user intent using Saleor product and variant data.[cite:184] |
| `get_product` | Proxy `product` / `productVariant` queries | Fetch images, pricing, variants and availability from Saleor GraphQL.[cite:184] |
| `add_to_cart` / `update_cart` / `remove_cart` / `get_cart` | Wrap `checkoutCreate`, `checkoutLinesAdd`, `checkoutLinesUpdate`, `checkoutLinesDelete` | Manage cart state through Saleor Checkout API.[cite:180] |
| `create_checkout` / `update_checkout` / `complete_checkout` | Wrap `checkoutCreate`/`checkoutUpdate` and `checkoutComplete` | Convert a checkout into a Saleor order. |
| `apply_promotion` | Custom tool that evaluates Saleor promotions and vouchers for a checkout | Optimize order value using Saleor promotion engine.[cite:179][cite:183] |
| `create_payment` / `refund_payment` | Wrap Saleor payment/transaction actions | Take payments and issue refunds.[cite:178][cite:186][cite:190] |
| `track_order` | Proxy order + fulfillment queries | Track shipment and order status based on Saleor data. |

## High‑level architecture
### Layer 1: Channel client
Web chat, mobile app, Telegram bot + Mini App, or AI host (Claude, ChatGPT, etc.). This layer renders UI appropriate for the channel and sends user actions/intents to the orchestration layer.

### Layer 2: Commerce orchestration ("skill layer")
Keeps session state, user preferences, search context, ranking logic, promotion optimization, guardrails and maps user intents into concrete MCP tool calls.

### Layer 3: MCP gateway for Saleor
Translates MCP tool calls into Saleor GraphQL queries/mutations and back:
- Catalog/product queries.
- Checkout/cart operations.
- Promotion/voucher evaluation.
- Payment and refund actions.
- Order and fulfillment queries.[cite:192][cite:198]

### Layer 4: Saleor backend
Core Saleor instance with Products, Channels, Promotions, Checkout, Payments, Orders, Shipping and Refunds.[cite:198]

## Key user flows
### Flow 1: Discover and select product
1. Shopper describes what they need in natural language.
2. Orchestration layer normalizes intent and calls `search_products`.
3. MCP gateway queries Saleor `products` with appropriate filters and channel.
4. Client shows top results as product cards and asks clarifying questions if needed.
5. Shopper picks a recommended product or an alternative; orchestration layer stores this choice.

### Flow 2: Optimize cart with promotions
1. Orchestration layer inspects current checkout and applicable promotions/vouchers in Saleor.
2. `apply_promotion` tool computes total including promotions, vouchers and shipping discounts.
3. Client proposes cart modifications under different optimization objectives.
4. Shopper confirms one configuration; orchestration layer updates checkout in Saleor.

### Flow 3: Checkout and payment
1. Orchestration layer ensures checkout is complete (lines, addresses, shipping method, voucher).
2. `complete_checkout` triggers order creation in Saleor.
3. If payment requires external UI, the client opens a hosted payment page; otherwise, the payment is processed via Saleor payment gateway.
4. Client confirms success with order id and key details.

### Flow 4: Track order, returns and refunds
1. Shopper asks about an order or a potential return.
2. Orchestration layer calls `track_order` or refund tools.
3. Client explains status and next steps in natural language.

## Data requirements
### Product data (Saleor)
- Product/Variant ID, name, slug, collections, categories and short description.[cite:184]
- Current and undiscounted prices via Saleor pricing, including catalogue promotions when applied; currency and promotion labels.[cite:179][cite:183]
- Variant availability and channels; shipping zones and methods to compute fees and ETA; merchant return policy.
- Media assets (image URLs, galleries) for visual presentation.[cite:194]

### Session / customer data
- Search intent, budget range, preferences (size, color, brands), location.
- Checkout/cart state, applied vouchers, chosen shipping method.
- Optional customer profile and order history if consented and available in Saleor.[cite:198]

## Non‑functional requirements
### Reliability
- All checkout and payment operations must be idempotent and resilient to retries.
- Clear state machine for checkout and payment states to avoid duplicate orders or refunds.

### Security & privacy
- Sensitive payment details must not be collected directly inside the AI conversation; always rely on PCI‑compliant payment UIs.
- Respect merchant and legal data‑protection rules for customer profiles and order history.

### Performance
- Search and product queries must respond quickly; use GraphQL projections to fetch only required fields and leverage caching where appropriate.[cite:191][cite:193]
- Cart/checkout updates must return clear status and error messages to guide the conversation.

### Observability & metrics
- Log key steps: search, recommendations shown/accepted, cart changes, checkout started/completed, refunds requested/completed.
- Expose analytics for conversion and experience metrics.

## KPIs
- Search‑to‑cart rate.
- Recommendation acceptance rate (top suggestion chosen).
- Promotion uplift (conversion/AOV increase when optimization is used).
- Checkout completion rate.
- Average time to resolve post‑purchase requests.
- Customer effort score for finding and buying the right product.

## MVP scope
### Included in MVP
- Natural‑language product search backed by Saleor GraphQL.
- Product cards with images, prices and CTAs.
- Explainable recommendations (top choice + alternatives).
- Basic promotion optimization using Saleor promotions and vouchers.
- Cart + checkout handoff integrated with Saleor Checkout.
- Basic order tracking.

### Phase 2
- Automated returns and refunds using Saleor refund/payments flows.
- Cross‑channel or multi‑merchant optimization.
- Deeper personalization based on Saleor customer data.
- Full multichannel support (Telegram Mini App, MCP Apps, embedded storefront widgets).

## Risks and implementation notes
- Not all channels support the same level of interactive UI; design robust fallbacks between rich UI and text‑only UI.
- "Best product" is subjective; the system must force the user to choose an optimization objective instead of guessing.
- Promotion logic can be complex; encapsulate it in a dedicated tool/engine that queries Saleor promotions instead of hard‑coding rules in prompts.
- Checkout and payments must prioritize safety, auditability and compliance over minimal turn count.

