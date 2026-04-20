# Product Requirements Document: bi193 Account Connection for Agent MCP Access

## Overview

This PRD defines the feature that allows a customer to authenticate through bi193 using their Saleor customer account and then grant an AI agent delegated access to call MCP tools on their behalf. Saleor supports customer authentication through `tokenCreate`, which returns an access token and refresh token for authenticated API use, while MCP authorization patterns increasingly rely on delegated, scoped access rather than directly exposing downstream credentials to the agent.[cite:79][cite:93][cite:80][cite:95][cite:101]

The feature goal is to create a clean, safe handoff between customer authentication and agent execution. After the user signs in on bi193, the agent should receive a bi193-issued MCP token that represents the customer session and allowed actions, while the raw Saleor token remains stored securely on the bi193 backend.[cite:79][cite:80][cite:95][cite:100]

## Product Vision

Customers should be able to connect their commerce account to an AI shopping assistant in a way that feels simple and trustworthy. The user should authenticate once in bi193, explicitly authorize AI-assisted access, and then let the agent perform approved actions such as reading profile data, accessing cart state, updating checkout, reviewing orders, or canceling eligible orders.[cite:79][cite:83][cite:101]

The long-term vision is to make account-linked agentic commerce feel as safe and standard as “Sign in with X” plus “Authorize this app,” but adapted for MCP-based AI workflows.

## Problem Statement

The AI agent needs authenticated access to user-specific commerce functions, but directly sharing a raw Saleor customer token with the agent creates security and lifecycle problems. Saleor customer tokens are bearer credentials for authenticated API access, so they should be stored securely and refreshed or revoked in a controlled backend environment.[cite:79][cite:80]

At the same time, the user experience must remain simple. The user should not need to manually copy tokens, configure technical settings, or understand GraphQL authentication mechanics. Instead, bi193 should broker the connection and give the agent a delegated token that is scoped, revocable, auditable, and purpose-built for MCP calls.[cite:95][cite:97][cite:100]

## Product Goals

- Let a user connect their Saleor-backed customer account through a bi193 login flow.[cite:79][cite:93]
- Let the agent initiate an account-connection flow and wait for completion.
- Issue a bi193-scoped token for MCP access after authentication succeeds.
- Keep Saleor access and refresh tokens on the backend only.[cite:79][cite:80]
- Allow the MCP server to act on behalf of the customer using delegated authorization.
- Support revocation, expiration, session tracking, and auditability.[cite:95][cite:100]
- Minimize friction for users on mobile and desktop.

## Non-Goals

- Exposing raw Saleor access tokens directly to the AI agent or end user.
- Building a universal identity provider for all merchants in the first release.
- Supporting every external ecommerce backend in the MVP.
- Giving the AI unrestricted account access without explicit scope control.

## Target Users

### Primary Users

- Customers who want the AI agent to use their own account for cart, checkout, and order actions.
- Returning shoppers who need account-linked features such as order review or cancellation.
- Mobile users who are redirected from an AI chat or agent interface to bi193 for sign-in.

### Secondary Users

- Merchants who need customer-authorized agent activity to stay auditable.
- Product and support teams that need a clear way to inspect whether a user connected their account and what the agent could do.
- Backend engineers who need a safe delegation model between Saleor and MCP.

## Key Use Cases

- The user asks the agent to add products to their account-linked cart.
- The user asks the agent to review past orders.
- The user asks the agent to continue checkout using saved customer context.
- The user asks the agent to cancel an eligible order.
- The agent requires account access and prompts the user to authenticate in bi193 first.

## Product Principles

1. **Delegation, not credential sharing**: the user authorizes bi193 and the agent receives a delegated token, not the raw Saleor credential.[cite:79][cite:95]
2. **Explicit consent**: the user should understand what the AI can access or do.
3. **Least privilege**: tokens should be scoped to necessary actions only.[cite:97][cite:100]
4. **Backend as trust anchor**: Saleor token storage, refresh, and validation happen server-side.[cite:79][cite:80]
5. **Resumable UX**: once the user completes login, the agent can continue the workflow without forcing the user to restart.
6. **Auditable actions**: all agent actions should be attributable to a user and session.

## High-Level Solution

The feature is implemented as a delegated authentication and authorization flow spanning the agent, bi193 frontend, bi193 backend, Saleor, and the MCP server.

### Core pattern

1. Agent detects that account-linked access is required.
2. Agent starts an auth session with bi193 backend.
3. bi193 backend returns a one-time connection URL.
4. User opens the URL and signs in through bi193 using their Saleor customer credentials.[cite:79][cite:93]
5. bi193 backend calls Saleor `tokenCreate`, receives access and refresh tokens, and stores them securely.[cite:79][cite:80][cite:93]
6. bi193 backend marks the auth session as complete.
7. bi193 backend issues a short-lived bi193 MCP token with user identity and allowed scopes.
8. Agent receives or activates that MCP token and uses it to call MCP tools.
9. MCP server validates the token and performs Saleor API calls on behalf of that customer.

## Functional Scope

### 1. Auth Session Start

The system must let the agent initiate an account-link flow before any account-sensitive MCP operation. The backend creates an auth session with a status such as `pending`, `authenticated`, `expired`, or `revoked`.

Required output from auth-session creation:

- `authSessionId`
- `connectUrl`
- `expiresAt`
- optional `pollUrl`

### 2. bi193 Sign-In Experience

The connection URL must open a bi193-auth screen where the user can sign in using their Saleor customer credentials. Saleor’s authentication flow supports token creation for authenticated customers through GraphQL mutations.[cite:79][cite:93]

The screen must include:

- Merchant or store context if relevant.
- A short explanation that connecting allows the AI agent to act on behalf of the user.
- Email/password login or the chosen customer-auth method.
- Success and failure states.

### 3. Consent and Scope Display

Before finalizing the connection, the UI should show what the AI agent will be able to do. At minimum, the user should see the scopes that are being granted for the current connection.

Example scope groups:

- Read my profile.
- Read my cart.
- Update my cart.
- Create or update checkout.
- Read my orders.
- Cancel my eligible orders.
- Update my saved shipping details.

### 4. Saleor Token Brokerage

After successful login, bi193 backend must call Saleor authentication APIs and securely persist the resulting access token and refresh token server-side.[cite:79][cite:80][cite:93] The frontend and agent should not be given the raw Saleor credentials.

Token brokerage responsibilities:

- Obtain Saleor access token.
- Obtain Saleor refresh token.
- Associate tokens with the authenticated customer.
- Refresh Saleor access as needed.
- Revoke or delete stored credentials when the user disconnects.

### 5. bi193 MCP Token Issuance

Once the auth session is complete, bi193 backend must issue a bi193-specific MCP token for the agent. This token should be short-lived, scoped, and linked to the authenticated customer session.

Suggested claims:

- internal user/session ID
- Saleor user ID or mapped customer ID
- permitted scopes
- issued-at timestamp
- expiry timestamp
- audience or resource indicator for MCP

### 6. Agent Session Completion

The agent must be able to detect when authentication is complete and continue the original workflow. For the MVP, a polling model is acceptable.

The agent should be able to:

- Start an auth session.
- Poll session status.
- Receive completion signal or token activation after authentication.
- Resume the original requested action.

### 7. MCP Authorization Enforcement

The MCP server must validate the bi193 token and enforce scope and ownership checks for all user-specific tools. Remote MCP authorization guidance increasingly centers on scoped delegated access rather than implicit trust between components.[cite:95][cite:97][cite:100]

Examples:

- `get_my_orders` returns only the authenticated customer’s orders.
- `cancel_order` works only for that customer and only if the order is eligible.
- `update_checkout_address` works only for the user’s active checkout.

### 8. Disconnect and Revocation

The user must be able to disconnect the AI assistant from their account. Revocation should invalidate the MCP token/session and optionally remove or disable stored Saleor refresh credentials.

The system should support:

- Manual disconnect by user.
- Session expiry.
- Forced revocation by operator or security policy.
- Re-authentication when token or session expires.

## User Stories

- As a customer, I want to connect my account to the AI assistant so it can act for me without asking me to manually copy a token.
- As a customer, I want to see what the AI can access before I approve it.
- As a customer, I want to disconnect the AI assistant if I no longer trust or need it.
- As an agent, I want to pause a workflow, ask the user to authenticate, and resume after connection is complete.
- As a backend operator, I want every agent action to be traceable to a customer session.

## End-to-End User Flow

### Flow A: Connect Account from Agent

1. User asks the agent to perform an account-linked action.
2. Agent determines authentication is required.
3. Agent calls `start_auth_session` on bi193 backend.
4. Agent returns a connect link to the user.
5. User opens bi193 auth page.
6. User logs in.
7. bi193 backend authenticates against Saleor using `tokenCreate`.[cite:79][cite:93]
8. bi193 backend stores Saleor credentials securely.[cite:79][cite:80]
9. bi193 backend marks session as authenticated and issues MCP access.
10. Agent polls and detects completion.
11. Agent resumes the original user request.

### Flow B: Reconnect After Expiry

1. Agent MCP token expires.
2. Agent attempts a protected action.
3. Backend returns `reauth_required`.
4. Agent asks user to reconnect.
5. User reauthenticates through the same connect flow.

### Flow C: Disconnect

1. User visits account connections screen.
2. User selects disconnect.
3. bi193 invalidates the agent session and MCP token.
4. Future MCP calls fail until re-authentication.

## Screens and UX Requirements

### 1. Connect Account Prompt

Presented by the agent or a hosted bi193 surface.

Must include:

- Why connection is required.
- One primary CTA to open sign-in.
- Optional secondary CTA to cancel.

### 2. bi193 Login Screen

Must include:

- Email/password fields or chosen auth method.
- Store branding or merchant context.
- Short explanation of AI-assisted access.
- Error handling for invalid credentials.

### 3. Consent Screen

Must include:

- Scope summary.
- Confirmation CTA.
- Cancel CTA.
- Plain-language description of what the AI can do.

### 4. Success Screen

Must include:

- Confirmation that the account is connected.
- Message that the user can return to the agent.
- Optional auto-close or redirect behavior.

### 5. Connection Management Screen

Should include:

- Connected account identity.
- Active scopes.
- Last connected time.
- Disconnect action.

## API Requirements

### Required backend endpoints

- `POST /agent/auth/start`
- `GET /agent/auth/session/:id`
- `POST /auth/saleor/login`
- `POST /agent/auth/complete`
- `POST /agent/auth/revoke`
- `GET /agent/me`

### Sample logical responses

`POST /agent/auth/start`
- `authSessionId`
- `connectUrl`
- `expiresAt`

`GET /agent/auth/session/:id`
- `status`: `pending | authenticated | expired | revoked`
- optional `mcpToken` or `tokenReady`

`POST /agent/auth/revoke`
- `success`
- `revokedAt`

## Data Model Requirements

### Auth session

- `authSessionId`
- `userId` (nullable until login complete)
- `status`
- `requestedScopes`
- `createdAt`
- `expiresAt`
- `completedAt`
- `agentSessionId`

### Connected account

- `userId`
- `saleorUserId`
- `email`
- `storeId` or `channel`
- `isConnected`
- `connectedAt`
- `revokedAt`

### Credential record

- `credentialId`
- `userId`
- encrypted `saleorAccessToken`
- encrypted `saleorRefreshToken`
- token expiry metadata
- last refresh timestamp

### MCP delegation token/session

- `agentSessionId`
- `userId`
- `scopes`
- `issuedAt`
- `expiresAt`
- `revokedAt`
- `lastUsedAt`

## Security Requirements

- Saleor access and refresh tokens must be stored only on the backend, encrypted at rest where applicable.[cite:79][cite:80]
- Frontend clients must never receive raw Saleor refresh tokens.
- bi193-issued MCP tokens must be short-lived and scoped.
- All MCP calls must perform scope and ownership checks.
- The system must log authentication, token issuance, refresh, revocation, and sensitive user actions.
- Consent should be recorded for auditability.
- Reauthentication should be required after session expiry or suspicious activity.

## Reliability Requirements

- Auth session polling must tolerate slow completion.
- The agent should be able to resume original workflows after successful authentication.
- Page refresh during login should not corrupt the auth session.
- Expired or duplicate auth sessions should be handled gracefully.
- Token refresh failures should trigger clear reauthentication states.

## Non-Functional Requirements

### Performance

- Auth session creation should feel immediate.
- Login and consent screens should load quickly on mobile.
- Polling intervals should avoid excessive backend load while keeping UX responsive.

### Accessibility

- Keyboard-accessible auth and consent forms.
- Clear error text and labels.
- Mobile-friendly layout and CTA sizing.

### Observability

The system should log:

- auth session started
- login success/failure
- Saleor token issued/refresh failed
- consent granted/rejected
- MCP token issued/revoked
- agent action performed under delegated access

## Success Metrics

- Auth-session completion rate.
- Percentage of agent workflows resumed successfully after login.
- Time from auth prompt to authenticated state.
- Reauthentication rate.
- Connection revocation rate.
- Token refresh success rate.
- Support incidents related to account connection.

## MVP Acceptance Criteria

The MVP is complete when:

- An agent can start a user auth session.
- A user can authenticate in bi193 with their Saleor-backed account.[cite:79][cite:93]
- bi193 backend stores Saleor credentials securely and does not expose them to the agent.[cite:79][cite:80]
- bi193 can issue a delegated MCP token after successful authentication.[cite:95][cite:101]
- The agent can resume and perform account-scoped MCP actions.
- The user can revoke the connection.
- The system logs the session and delegated actions.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Raw Saleor token leaks to agent or frontend | High security risk | Keep Saleor credentials backend-only.[cite:79][cite:80] |
| Agent token has too much privilege | Unauthorized actions | Use scoped tokens and ownership checks.[cite:97][cite:100] |
| User does not understand what is being authorized | Trust issues | Add plain-language consent screen. |
| Session expires mid-flow | Workflow drop-off | Support reconnect and resume flow. |
| Polling-based completion feels slow | UX friction | Keep polling interval tight enough and support redirect/success signals. |

## Release Plan

### Phase 1: MVP Delegated Connection

- Start auth session
- bi193 login via Saleor credentials
- Secure token brokerage
- MCP token issuance
- Agent polling and resume

### Phase 2: Consent and Connection Management

- Scope display
- Connection dashboard
- Disconnect/revoke controls
- Better session history

### Phase 3: Standardized Authorization Expansion

- Stronger OAuth-style patterns for remote MCP use
- More merchant/store support
- Richer permission controls and approvals

## Open Questions

- Will bi193 support only one connected store per user in MVP or multiple store/account contexts?
- Should the delegated token be returned directly through polling or activated server-side and only referenced by session ID?
- What is the default token TTL for MCP access?
- Which scopes should require stronger confirmation, such as order cancellation?
- Should reconnect reuse prior consent or always ask again after revocation?

## Implementation Summary

This feature should be implemented as a delegated authentication broker where bi193 handles Saleor customer login, stores Saleor credentials securely, issues a separate short-lived MCP token for the AI agent, and lets the agent resume commerce actions after the user signs in. This aligns with Saleor’s customer token model and with emerging MCP authorization patterns that favor scoped delegated access over direct credential sharing.[cite:79][cite:93][cite:80][cite:95][cite:101]
