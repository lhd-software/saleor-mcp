# Product Requirements Document: Agentic Ecommerce Platform with MCP, Skills, Smart Search, and Promotion Optimization

## Document Overview

This PRD defines an AI-first ecommerce platform designed for shoppers who interact through an AI agent rather than a traditional storefront. The platform uses Claude as the conversational layer, MCP as the standard tool interface, domain skills/rules for orchestration, and custom APIs for multilingual product search, promotion evaluation, cart optimization, and transaction flows.[cite:32][cite:36][cite:38]

The core product goal is to let a shopper express an intent in natural language, such as Vietnamese or English, and receive a fast, decision-ready purchase path that includes relevant products, applicable promotions, vouchers, bundle opportunities, and final recommended cart configurations.[cite:13][cite:25][cite:39][cite:40]

## Product Vision

The platform acts as an agentic commerce layer where the customer asks for an outcome, and the AI agent translates that request into structured commerce actions. Instead of only listing products, the system should search, compare, explain trade-offs, evaluate discount rules, optimize purchase combinations, and then assist with checkout, tracking, return, or post-purchase support.[cite:21][cite:27][cite:32]

The long-term vision is to create a commerce environment designed for AI agents and human-in-the-loop shoppers, where shopping decisions are faster, more personalized, and more price-efficient than in conventional ecommerce UX.[cite:21][cite:32]

## Problem Statement

Traditional ecommerce search and filtering are built for manual browsing and often perform poorly when users describe needs conversationally, especially across multiple languages. In multilingual markets such as Vietnam, users may search in Vietnamese while product catalogs are named or indexed in English, creating relevance gaps unless translation and synonym expansion are handled explicitly.[cite:13][cite:25]

A second problem is that even when relevant products are found, customers still need to manually understand promotions, voucher applicability, bundle eligibility, and trade-offs between simple purchase and optimized purchase paths. Modern commerce engines expose discounts and voucher capabilities, but they do not automatically turn these into a decision-ready assistant experience without an orchestration layer.[cite:39][cite:40][cite:44][cite:47]

## Product Goals

- Enable natural-language shopping in Vietnamese and English through one agentic interface.[cite:25][cite:36][cite:38]
- Return search results that are multilingual-aware and intent-aware, not just exact keyword matches.[cite:13][cite:25]
- Evaluate applicable promotions, vouchers, and bundle rules before the agent recommends products.[cite:39][cite:40][cite:44]
- Present 1 to 4 ranked purchase options that help the shopper decide quickly based on relevance, savings, and simplicity.
- Support end-to-end actions including product discovery, comparison, cart building, checkout creation, order tracking, and return initiation.[cite:21][cite:39][cite:51]
- Separate orchestration behavior from backend commerce logic by using skills for policy and MCP tools for capability exposure.[cite:27][cite:32][cite:36]

## Non-Goals

- Replacing the underlying ecommerce engine for catalog, inventory, pricing, or order management.[cite:39][cite:51]
- Implementing all discount logic only in prompts or inside the LLM.
- Building a generic chatbot without structured commerce capabilities.
- Guaranteeing every promotion can be stacked unless confirmed by backend rule evaluation.[cite:39][cite:40]

## Target Users

### Primary Users

- Shoppers who want to describe what they need conversationally instead of navigating category trees.
- Mobile-first users who want the fastest path to a good buying decision.
- Price-sensitive shoppers who care about vouchers, bundle savings, and promotion maximization.
- Vietnamese-market shoppers who may search in Vietnamese while catalog metadata is partially or fully in English.

### Secondary Users

- Merchants that want a higher-conversion AI shopping channel.
- Operations or marketing teams that need promotions surfaced intelligently.
- Developers building AI-agent commerce integrations on top of Saleor or similar commerce backends.[cite:16][cite:39]

## Core User Stories

- As a shopper, I want to describe what I need in natural language so that I do not need to learn category navigation.
- As a shopper, I want Vietnamese product intents to match English catalog products so that I can find relevant items even when the catalog language differs.[cite:13][cite:25]
- As a shopper, I want the agent to tell me which promotions or vouchers apply so that I can choose faster.
- As a shopper, I want the agent to suggest a better bundle if adding one more item unlocks a stronger discount.[cite:44][cite:47]
- As a shopper, I want the agent to compare options and explain why one option is best for my goals.
- As a merchant, I want the AI layer to follow structured rules and backend validations so that pricing and discounts remain trustworthy.[cite:27][cite:39][cite:40]

## Product Principles

1. **Conversation first**: Users start with intent, not menus.
2. **Tool-driven reliability**: The agent must use structured tools, not freeform guessing, for commerce operations.[cite:27][cite:38]
3. **Decision-ready output**: The system should recommend purchasable scenarios, not just raw product lists.
4. **Promotion-aware by default**: Search should be followed by promotion evaluation whenever relevant.[cite:39][cite:40]
5. **Backend truth**: Final eligibility, stock, price, and checkout state come from the commerce backend.[cite:39][cite:51]
6. **Multilingual by design**: Query understanding should not assume catalog language equals user language.[cite:13][cite:25]

## Functional Scope

### 1. Conversational Shopping Interface

The user can ask for products, bundles, recommendations, or best-value options in Vietnamese or English. Claude interprets the request, applies shopping skills/rules, and calls the appropriate MCP tools instead of relying on freeform answers.[cite:36][cite:38]

### 2. Smart Product Search

The platform must provide a `search_products_smart` capability that accepts raw user intent and handles language detection, synonym expansion, translation mapping, attribute extraction, and relevance ranking. This is necessary because multilingual search behavior is not automatically solved by MCP or by standard catalog translation support.[cite:13][cite:16][cite:25][cite:36]

Expected smart-search behaviors:

- Detect Vietnamese or English query language.
- Extract product type, attributes, audience, usage intent, and constraints.
- Expand terms using domain dictionaries, for example `áo thun` to `t-shirt` and related synonyms.
- Search across canonical fields, translated fields, tags, and optional semantic/vector indices.
- Return structured results with enough data for comparison and recommendation.

### 3. Product Comparison

The platform must support comparing products on attributes such as price, availability, promotion eligibility, style/use case, and delivery constraints. The comparison output should be optimized for natural-language explanation by the AI agent.

### 4. Promotion and Voucher Intelligence

The platform must evaluate automatic promotions, voucher codes, bundle rules, and cart-level discounts before final recommendation. Saleor distinguishes discounts, promotions, and vouchers, and vouchers can apply under specific constraints rather than acting as universal price overrides.[cite:39][cite:40][cite:42]

Expected supported promotion types:

- Automatic promotion on product or order scope.[cite:39]
- Voucher-code discount on eligible products or orders.[cite:40]
- Buy X get Y free or discounted.[cite:44][cite:47]
- Buy X and Y get Z percent discount.[cite:44][cite:47]
- Bundle or quantity-break logic.
- Merchant-defined marketing campaigns and custom rule sets.

### 5. Best-Cart Simulation

The system must generate and compare purchasable cart scenarios, not only show promotional labels. This is important because the best value may come from a slightly larger cart, a voucher path, or a qualifying cross-sell combination rather than the first product match.[cite:40][cite:44][cite:47]

The `simulate_best_offer` or `build_best_cart` capability should:

- Test candidate cart combinations.
- Apply backend-validated promotion logic.
- Calculate final totals, savings, and incremental spend.
- Rank options by business-configurable priorities such as savings, simplicity, or conversion probability.
- Return explanation-ready outputs to the agent.

### 6. Cart and Checkout Actions

The platform must support adding items to cart, creating checkout sessions, validating shipping/payment choices, and confirming order placement through the underlying ecommerce engine.[cite:39][cite:51]

### 7. Post-Purchase Support

The platform should support order lookup, shipment tracking, return guidance, and refund/return initiation where backend capabilities exist.[cite:51]

## Proposed Capability Model

| Layer | Responsibility |
|---|---|
| Claude client | Understand user intent, maintain dialogue, choose the next best tool flow.[cite:38] |
| Skills / rules | Define shopping policies, e.g. always run smart search before recommendation, always validate promotions before claiming savings.[cite:27] |
| MCP server | Expose agent-facing tools as structured capabilities.[cite:32][cite:36] |
| Search API | Handle multilingual retrieval, query rewriting, ranking, semantic matching. |
| Promotion API | Evaluate campaigns, vouchers, bundles, rule eligibility, stackability, and final totals. |
| Cart/checkout API | Persist purchasable state and complete transactional flows. |
| Commerce backend | Source of truth for catalog, stock, pricing, discounts, checkout, orders.[cite:39][cite:51] |

## Required MCP Tools

The MCP layer should expose business-oriented tools instead of raw backend endpoints. Anthropic’s guidance on tool design emphasizes clear, scoped tools that map to real tasks the agent can execute reliably.[cite:27][cite:38]

### Search and Discovery Tools

- `search_products_smart(query, locale?, filters?, user_context?)`
- `get_product_detail(product_id)`
- `compare_products(product_ids, comparison_goal?)`
- `get_product_recommendations(seed_products?, user_intent?, budget?)`

### Promotion and Decision Tools

- `get_applicable_promotions(product_ids?, cart_lines?, voucher_code?)`
- `simulate_best_offer(product_ids, constraints?, optimization_goal?)`
- `build_best_cart(user_goal, shortlisted_products?, max_items?, budget?)`
- `apply_voucher(checkout_id, voucher_code)`
- `compare_purchase_options(option_ids)`

### Transaction Tools

- `add_to_cart(checkout_id?, product_variant_id, quantity)`
- `remove_from_cart(checkout_id, line_id)`
- `create_checkout(cart_lines, customer_info?)`
- `update_checkout(checkout_id, shipping_method?, payment_method?)`
- `place_order(checkout_id)`

### Post-Purchase Tools

- `track_order(order_id)`
- `get_return_options(order_id)`
- `initiate_return(order_id, line_items)`

## Skill and Rule Design

Skills should be used to encode agent behavior and orchestration policy above the tools. The skill layer should tell Claude when to search, when to ask clarifying questions, when to evaluate promotions, and when to escalate to transactional actions.[cite:27][cite:38]

Recommended default shopping rules:

- For shopping intents, call `search_products_smart` before any recommendation.
- If the query is broad, ask at most one clarifying question before searching.
- Before recommending a product, evaluate applicable promotions or bundle opportunities.
- Never claim voucher or campaign savings until the backend or promotion service confirms eligibility.[cite:39][cite:40]
- If adding 1 or 2 products materially improves savings, present it as an alternative cart option.
- Rank options by user intent first, then value, then simplicity unless merchant rules say otherwise.
- Before checkout, revalidate stock, price, and discount state.[cite:39][cite:51]

## Search API Requirements

The Search API is the intelligence layer behind multilingual product discovery. It should accept the user’s original natural-language request and convert it into a structured product-retrieval process.

### Search API responsibilities

- Language detection.
- Query normalization.
- Product/entity/attribute extraction.
- Translation and synonym expansion.
- Multi-index search orchestration.
- Result merging and de-duplication.
- Relevance ranking.
- Search explanation metadata.

### Search API inputs

- `query`
- `locale`
- `currency`
- `channel`
- `filters`
- `customer_context`
- `history_context`
- `optimization_goal` such as cheapest, best value, premium, or fastest delivery

### Search API outputs

- Ranked products.
- Confidence score.
- Matched terms and translations used.
- Extracted filters and inferred intent.
- Promotion-check candidates.
- Suggested clarifying questions when confidence is low.

## Promotion API Requirements

The Promotion API should act as a decision engine rather than a raw discount lookup service. It should determine which promotions can apply, which combinations are mutually exclusive, which cart changes unlock better value, and which scenario should be recommended.[cite:39][cite:40][cite:44][cite:47]

### Promotion API responsibilities

- Evaluate automatic promotions.
- Validate voucher code applicability.
- Compute buy X get Y and cross-product discount rules.
- Simulate cart paths.
- Check stackability or exclusivity.
- Calculate final total, savings, incremental spend, and effective discount rate.
- Return explanation-friendly recommendation objects.

### Promotion API outputs

- Eligible rules.
- Ineligible rules with reasons.
- Ranked purchase scenarios.
- Savings summary.
- Required user action, for example enter voucher or add one more item.
- Backend validation status.

## Example End-to-End Flows

### Flow A: Simple Search

1. User asks: "Tôi cần áo thun trắng nam".
2. Claude calls `search_products_smart` with the original Vietnamese query.
3. Search API expands terms into English equivalents and returns relevant products.[cite:13][cite:25]
4. Claude calls `get_applicable_promotions` for shortlisted products.
5. Claude presents best single-product and best-value options.

### Flow B: Promotion Optimization

1. User asks for a product category and mentions wanting a good deal.
2. Search returns top products.
3. Promotion API evaluates quantity discount, voucher, and buy-X-get-Y opportunities.[cite:40][cite:44][cite:47]
4. Cart simulation builds 2 to 4 purchase paths.
5. Claude explains which path is cheapest, which is simplest, and which gives the best value.

### Flow C: Voucher Application

1. User shares a voucher code.
2. Claude calls `apply_voucher` or promotion-evaluation tools.
3. Backend validates whether the code is active and applicable.[cite:40]
4. Claude updates the recommendation and cart summary.

## User Experience Requirements

The conversation should produce a recommendation that is concise, structured, and actionable. The user should not need to interpret raw promotion rules or manually test combinations.

Each recommendation should include:

- Product or bundle name.
- Final estimated price.
- Promotion or voucher applied.
- What the user needs to do next.
- Why this option is recommended.
- One or more alternatives if trade-offs exist.

## Data Requirements

The platform should maintain or have access to:

- Canonical catalog data.
- Localized product names and descriptions.[cite:25]
- Product attributes and tags.
- Inventory and availability.
- Price by market or channel.
- Promotion and voucher definitions.[cite:39][cite:40]
- Order and checkout state.[cite:51]
- Search analytics and click/conversion feedback.

To improve multilingual search quality, the platform should also maintain curated synonym dictionaries, translation mappings, and optionally embeddings for semantic retrieval.

## Ranking and Optimization Logic

The system should rank recommendations using a configurable weighted policy. A typical default priority is:

1. Intent relevance.
2. Availability.
3. Promotion-adjusted value.
4. Simplicity of purchase path.
5. Merchant business rules such as margin or campaign priority.

The recommendation engine should support merchant-configurable objectives, for example maximizing conversion, savings, average order value, or campaign penetration.

## Trust, Validation, and Guardrails

Because promotions and checkout pricing are sensitive, the platform must not let the AI invent eligibility or prices. Anthropic’s tool design guidance and MCP best-practice thinking both support structured tool invocation and validation for high-stakes actions.[cite:27][cite:32][cite:38]

Guardrails:

- Never claim a discount is valid until backend evaluation confirms it.[cite:39][cite:40]
- Recheck cart totals before checkout confirmation.[cite:51]
- Distinguish estimated recommendation from confirmed transactional state.
- Use idempotent transaction operations where possible.
- Log every tool action for auditability.

## Success Metrics

### User Metrics

- Search-to-click rate.
- Recommendation acceptance rate.
- Time-to-decision.
- Checkout conversion rate.
- Voucher utilization rate.
- Average order value uplift from promotion-aware recommendations.

### System Metrics

- Search response latency.
- Promotion simulation latency.
- Recommendation accuracy as measured by click/purchase outcomes.
- Percentage of successful discount validations.
- Error rate in checkout or price mismatch cases.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Multilingual mismatch between user query and catalog language | Poor search relevance | Use translation expansion, localized fields, and synonym dictionaries.[cite:13][cite:25] |
| Agent claims invalid savings | Trust loss | Require backend validation before showing confirmed discounts.[cite:39][cite:40] |
| Too many options overwhelm user | Lower conversion | Limit recommendations to 1-4 ranked options. |
| Promotion logic becomes too complex inside prompts | Unreliable behavior | Move logic into APIs and MCP tools.[cite:27][cite:38] |
| Checkout totals change after recommendation | Friction and abandonment | Revalidate before checkout placement.[cite:51] |

## Release Approach

### Phase 1: Foundational Search and Recommendation

- Smart multilingual search.
- Product detail and comparison.
- Basic promotion lookup.
- Agent recommendation flow.

### Phase 2: Promotion Optimization

- Voucher validation.
- Buy X get Y evaluation.
- Bundle/cart simulation.
- Best-cart recommendation.

### Phase 3: Full Transaction and Post-Purchase

- Checkout creation and order placement.
- Order tracking.
- Return support.
- Analytics-driven search and ranking improvement.

## Open Questions

- Which search engine should back multilingual retrieval: native backend search, Algolia, Meilisearch, Elasticsearch, or hybrid vector search?
- Which promotions can stack by business policy versus backend capability?[cite:39][cite:40]
- Should the system optimize for lowest total, highest margin, or highest likelihood of conversion by default?
- How much autonomy should the agent have before asking the user for confirmation on cart modifications?
- Which merchant dashboards are needed to monitor AI-driven promotion recommendation performance?

## Acceptance Criteria

The MVP is successful when:

- A shopper can search in Vietnamese or English and retrieve relevant products from a multilingual or English-heavy catalog.[cite:13][cite:25]
- The agent can evaluate applicable promotions and vouchers for shortlisted products.[cite:39][cite:40]
- The system can present at least 2 ranked purchase scenarios with final estimated totals.
- The user can proceed from recommendation to checkout through structured tools.[cite:36][cite:51]
- The agent does not claim invalid discount eligibility without backend confirmation.[cite:39][cite:40]

## Implementation Summary

This product should be implemented as a layered agentic commerce architecture where Claude handles conversation, skills define decision policy, MCP exposes structured commerce tools, custom search and promotion APIs perform the heavy reasoning, and the ecommerce backend remains the source of truth for all transactional outcomes.[cite:27][cite:32][cite:36][cite:38]
