# Product Requirements Document: MCP App (Vite) for Cart, Checkout, Address, SePay QR Payment, Order Review, and Cancellation

## Overview

This PRD defines the frontend product requirements for an `mcp-app` built with Vite as the customer-facing application layer for agentic ecommerce. Vite is a fast frontend build tool with a development server and production build pipeline suitable for modern web apps, making it an appropriate foundation for a lightweight MCP-driven commerce client.[cite:63][cite:64]

The application is intended to operate as the transactional screen for the AI commerce experience. It should let users review cart state, edit quantities, proceed through checkout, use shipping information where billing address defaults to the same value, pay by QR code through SePay, review order status, and cancel an order if needed.[cite:68][cite:69][cite:71][cite:75]

## Product Vision

The MCP app should act as the execution surface for shopping decisions made through an AI-assisted flow. The AI agent can search, compare, and recommend, while the app gives the customer a reliable place to confirm line items, manage addresses, complete payment, and track order outcomes.[cite:36][cite:38][cite:69]

The app should feel simple and operationally trustworthy. It is not meant to duplicate the full conversational intelligence layer; instead, it should expose the critical transaction states cleanly and connect them to backend tools and services.

## Problem Statement

Agentic commerce needs a clear handoff point between recommendation and transaction. If the user cannot easily inspect the cart, confirm shipping details, pay with a trusted local payment method, and review order state afterward, the AI experience feels incomplete even when product recommendation is strong.[cite:69][cite:71]

For the Vietnam market, QR-code bank transfer is a practical payment path. SePay provides QR generation and webhook-based payment confirmation flows that support a process where a payment code is embedded in the transfer description and incoming transfers are matched back to the corresponding order.[cite:68][cite:71][cite:74]

## Product Goals

- Provide a simple Vite-based app shell for commerce actions and state transitions.[cite:63][cite:64]
- Let users review and update cart items before checkout.
- Support checkout with shipping address and billing address defaulted to the same value.
- Support QR-code payment via SePay and show clear payment status progression.[cite:68][cite:71][cite:74]
- Let users review order details and order status after checkout.[cite:72]
- Let users cancel orders when allowed by backend policy and order state.[cite:69][cite:75]
- Keep the app aligned with MCP-driven workflows so the AI agent and app operate on the same commerce state.[cite:36][cite:38]

## Non-Goals

- Building the entire catalog browsing and recommendation experience inside the Vite app.
- Replacing the ecommerce backend as the source of truth for checkout, order, or payment state.[cite:69][cite:72]
- Implementing payment confirmation only on the frontend without backend webhook validation.[cite:68][cite:71]
- Supporting every payment method in the first release.

## Target Users

### Primary Users

- Customers who arrive at the transactional screen from an AI-assisted shopping flow.
- Mobile-first shoppers who want a short path from decision to payment.
- Users in Vietnam who are comfortable paying via bank-transfer QR code.

### Secondary Users

- Merchants and operations teams who need payment and order states to remain auditable.
- Support teams that need order review and cancellation to behave consistently with backend logic.

## Product Scope

The Vite app should contain the following main screens or views:

- Cart
- Checkout
- Payment
- Order detail/status
- Order cancellation confirmation

The app may be built as a single-page application using Vite with client-side routing, but final implementation details can be chosen later. Vite supports rapid frontend development and optimized production builds for this type of web application.[cite:63][cite:64]

## Core User Stories

- As a user, I want to review the products the AI agent added to my cart so I can confirm the correct items and quantities.
- As a user, I want to edit or remove items before checkout so I stay in control of the order.
- As a user, I want shipping address entry to be simple and have billing address default to the same information unless I explicitly change it.
- As a user, I want to pay by scanning a QR code so I can complete payment with my banking app.[cite:68][cite:71][cite:74]
- As a user, I want to see whether my order is pending, awaiting payment, paid, processing, canceled, or completed so I understand what is happening.[cite:68][cite:72]
- As a user, I want to cancel my order when it is still eligible for cancellation.

## Product Principles

1. **One clear next step**: every screen should tell the user what to do next.
2. **Backend truth**: totals, order status, and cancelability come from backend systems, not guessed UI state.[cite:69][cite:72][cite:75]
3. **Payment clarity**: QR payment instructions and payment confirmation states must be unambiguous.[cite:68][cite:71]
4. **Minimal friction**: shipping and billing flow should be short and optimized for mobile.
5. **MCP alignment**: the UI should reflect the same commerce objects used by the agent and tools.[cite:36][cite:38]

## Functional Requirements

## Cart

The cart view must display:

- Product image, name, variant, unit price, quantity, line subtotal.
- Promotion or discount indicator if relevant.
- Cart subtotal and estimated total.
- Primary CTA to continue to checkout.

The cart view must support:

- Increase quantity.
- Decrease quantity.
- Remove item.
- Refresh cart from backend state.
- Recover gracefully if a product becomes unavailable or price changes.

If the cart is created or updated by the AI agent, the UI must still show the user the resulting state clearly before checkout.

## Checkout

The checkout view must support:

- Contact information entry if required.
- Shipping address entry.
- Billing address defaulted to shipping address via a checked toggle such as “Billing address is the same as shipping address.”
- Optional manual entry of a separate billing address when the toggle is unchecked.
- Shipping method selection if backend shipping options are available.
- Order summary with final payable amount.

Saleor’s checkout lifecycle documentation indicates that checkout is a stateful process and that payment/transaction actions must stay coordinated with backend state.[cite:69] The app should therefore fetch current checkout data before final payment presentation.

### Shipping and Billing Address Rules

- By default, billing address must mirror shipping address.
- If the user edits shipping while the “same as billing” toggle is enabled, billing updates automatically in UI state.
- If the user disables the toggle, billing becomes independently editable.
- Validation must ensure required fields are present before payment step.

## Payment by SePay QR Code

The payment view must support QR-code payment using SePay. SePay documentation describes a flow where the merchant system creates a unique payment code per order, generates a QR code that includes amount and transfer description, and then receives webhook notifications to confirm payment once the matching transfer arrives.[cite:68][cite:71][cite:74]

### Required payment flow

1. User reaches payment step.
2. Backend creates or exposes an order/payment code unique to the order.[cite:68]
3. App requests QR payment payload from backend.
4. App displays:
   - QR image
   - bank name
   - bank account number
   - amount
   - transfer content / payment code
5. User scans the QR code in their banking app and completes transfer.
6. Backend receives SePay webhook and validates the incoming transaction against the order code and amount.[cite:68][cite:71]
7. App polls or subscribes to payment status updates until payment is confirmed, failed, expired, or canceled.

### Payment screen requirements

The payment screen must show:

- Current order ID.
- Amount due.
- Countdown or validity message if payment expires.
- QR code image.
- Raw bank transfer details for manual fallback.
- Payment status label.
- CTA to refresh payment status.

### Payment states

The app should support these customer-visible payment states:

- Awaiting payment
- Payment detected
- Payment confirmed
- Payment failed
- Payment expired
- Payment canceled

The system must not mark an order as paid based only on frontend scan action. Payment confirmation must come from backend status after SePay webhook processing.[cite:68][cite:71]

## Order Review and Status

After checkout creation and payment attempt, the app must provide an order detail/status screen. Saleor’s order object includes cancellation-related totals and order state data, making backend order status the source of truth for what the user should see.[cite:72]

The order screen should show:

- Order ID
- Created date/time
- Current order status
- Payment status
- Purchased items
- Shipping address
- Billing address
- Shipping method
- Total amount
- Cancellation availability

Suggested order statuses for UI display:

- Draft / pending
- Awaiting payment
- Paid
- Confirmed / processing
- Shipped
- Completed
- Canceled
- Refund in progress or refunded, if applicable

## Order Cancellation

The app must provide cancellation only when the order is eligible. Saleor exposes `orderCancel` as a mutation for order cancellation, and the backend should determine whether the order can still be canceled based on permissions and order state.[cite:75]

### Cancellation requirements

- Show cancel action only when backend marks order as cancelable.
- Ask user for confirmation before cancellation.
- Display clear result state: cancellation requested, canceled, or cancellation failed.
- Refresh order status after cancellation attempt.
- Prevent duplicate cancellation submission.

If transaction or payment release logic is involved, the app should simply reflect backend status rather than trying to manage the financial reversal logic on the client.[cite:69][cite:72][cite:75]

## Integration Requirements

## MCP integration

The app should work with the same commerce actions exposed to the AI agent through MCP. The frontend does not need to speak MCP directly if a backend gateway is used, but the domain model and action boundaries should align with MCP tool capabilities.[cite:36][cite:38]

Recommended aligned actions:

- `add_to_cart`
- `remove_from_cart`
- `update_cart_line`
- `create_checkout`
- `update_addresses`
- `select_shipping_method`
- `create_qr_payment`
- `get_payment_status`
- `get_order`
- `cancel_order`

## Backend APIs

The app will need backend endpoints or service methods for at least:

- Get cart
- Update cart lines
- Create/update checkout
- Save shipping and billing addresses
- Get shipping methods
- Create SePay QR payload
- Get payment status
- Get order detail
- Cancel order

## Data Model Requirements

### Cart object

- cartId
- lines[]
- currency
- subtotal
- discounts
- total

### Checkout object

- checkoutId
- cart lines
- shippingAddress
- billingAddress
- sameAsBilling boolean
- shippingMethod
- total

### Payment object

- paymentId or orderPaymentId
- orderId
- amount
- qrUrl
- bankName
- bankAccountNumber
- transferContent
- status
- expiresAt

### Order object

- orderId
- status
- paymentStatus
- items[]
- shippingAddress
- billingAddress
- totals
- createdAt
- cancelable boolean

## UX Requirements

### Cart UX

- Editable quantities with clear feedback.
- Remove-item confirmation only when needed.
- Sticky summary CTA on mobile.

### Checkout UX

- Short form with progressive sections.
- Billing address toggle enabled by default.
- Validation errors shown inline.
- Final summary always visible before payment.

### Payment UX

- QR image large enough for mobile and desktop scanning.
- Copy buttons for account number and transfer content.
- Clear instruction text for bank transfer.
- Status refresh and automatic refresh behavior.
- Fallback text when webhook confirmation is delayed.[cite:68][cite:71]

### Order UX

- Order status visible immediately on load.
- Timeline or status badge pattern for clarity.
- Cancel button hidden when unavailable.

## State Transitions

The app should support the following simplified flow:

1. Cart updated
2. Checkout created
3. Shipping/billing address saved
4. Shipping method selected
5. Payment QR generated
6. Payment awaiting confirmation
7. Payment confirmed
8. Order processing
9. Order completed or canceled

Error states must also be handled, including invalid cart, unavailable shipping method, QR generation failure, payment timeout, payment mismatch, order not found, and cancellation rejection.

## Security and Trust Requirements

- Sensitive payment confirmation must happen on the backend via SePay webhook or backend status sync, not solely in the browser.[cite:68][cite:71]
- The app must avoid presenting paid status until confirmed by backend.
- Order cancellation must require explicit user confirmation.
- Frontend should not expose secrets such as SePay credentials.
- All mutation actions should be idempotent or guarded against duplicate submission where possible.

## Non-Functional Requirements

### Performance

- Cart and checkout views should load quickly on mobile connections.
- Payment-status refresh should not excessively poll the backend.
- UI should remain responsive while awaiting webhook confirmation.

### Reliability

- App must tolerate delayed payment confirmation.
- App must recover after page refresh by reloading order/payment state from backend.
- Cart, checkout, and order state should remain consistent with backend source of truth.

### Accessibility

- Keyboard navigable forms and actions.
- Sufficient contrast for status badges and action buttons.
- Text instructions should accompany the QR image.
- Error messages should be readable and associated with form fields.

## Success Metrics

- Cart-to-checkout conversion rate.
- Checkout-to-payment-start rate.
- Payment confirmation rate for SePay QR flow.
- Payment drop-off rate at QR screen.
- Order cancellation success rate for eligible orders.
- Time from order creation to payment confirmation.
- User support incidents related to address entry or payment confusion.

## MVP Acceptance Criteria

The MVP is complete when:

- User can review, update, and remove cart items.
- User can proceed to checkout and enter shipping address.
- Billing address defaults to shipping address and can be edited separately when needed.
- User can generate and view a SePay QR payment screen with transfer details.[cite:68][cite:74]
- App reflects payment confirmation only after backend confirms payment status.[cite:68][cite:71]
- User can review order status after checkout.[cite:72]
- User can cancel an eligible order through the app.[cite:75]

## Proposed Milestones

### Phase 1

- Vite app scaffold
- Cart screen
- Checkout form with address handling
- Basic order summary

### Phase 2

- SePay QR payment integration
- Payment status polling
- Order review screen

### Phase 3

- Cancellation flow
- Better status timeline
- Error handling and mobile polish

## Open Questions

- Should the app be embedded inside a broader AI commerce shell or run as a standalone transactional client?
- Will the frontend call Saleor directly through a BFF or through a separate commerce gateway?
- What is the polling interval and timeout policy for SePay payment confirmation?[cite:68][cite:71]
- Which order states are cancelable by business rule versus backend rule?
- Should guest checkout and authenticated checkout both be supported in the MVP?

## Implementation Summary

The `mcp-app` should be a focused Vite-based transaction interface that handles the operational steps after an AI-assisted recommendation: cart review, checkout, same-as-billing address flow, SePay QR payment, order review, and cancellation. Vite provides an appropriate frontend foundation, SePay supports QR and webhook-driven bank-transfer confirmation, and Saleor should remain the source of truth for checkout lifecycle, order status, and cancellation behavior.[cite:63][cite:68][cite:69][cite:71][cite:75]
