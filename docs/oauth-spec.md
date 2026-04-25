# OAuth 2.0 Spec for bi193.com — MCP Customer Auth

This document is the contract between **bi193.com** (Authorization Server) and **store4ai-mcp.bi193.com** (Resource Server / MCP). It describes everything the bi193 frontend/backend needs to implement so that any MCP client (Claude Desktop, OpenClaw, picoclaw, VS Code, etc.) can let a user log in and grant the agent customer-scoped access to call MCP tools.

The MCP side (this repo) is already done — see "What MCP advertises" below. This doc is for the bi193 dev team.

> Companion PRD: `docs/bi193-agent-auth-prd.md` covers the user-experience side. This doc is the **technical contract**.

---

## 1. The flow at a glance

```
1.  Agent calls MCP without a token              →  MCP returns 401 + RFC 9728 metadata pointer
2.  Agent fetches /.well-known/oauth-protected-resource/mcp on MCP
                                                 →  metadata says "auth server = https://bi193.com"
3.  Agent fetches https://bi193.com/.well-known/oauth-authorization-server
                                                 →  metadata lists /oauth/authorize, /oauth/token, etc.
4.  Agent (PKCE) opens browser → /oauth/authorize?…
5.  bi193.com checks session cookie:
      - logged in?     → render consent screen
      - not logged in? → /login?next=/oauth/authorize?…  →  back to authorize
6.  User clicks "Allow" → 302 redirect to redirect_uri?code=<short-lived>&state=<echo>
7.  Agent POST /oauth/token  { code, code_verifier, client_id, redirect_uri }
                                                 →  { access_token: <Saleor JWT>, refresh_token, expires_in, scope }
8.  Agent calls MCP with `Authorization: Bearer <access_token>` from now on
9.  When token expires → POST /oauth/token { grant_type: "refresh_token", refresh_token }
```

The access_token MUST be a Saleor-issued JWT (the same one returned by `tokenCreate` mutation). MCP forwards it verbatim to Saleor on every GraphQL call, so Saleor remains the source of truth for revocation, scope claims, and signature.

---

## 2. What MCP already advertises (no change needed on bi193 side)

When the MCP is started with these env vars:

```bash
OAUTH_AUTHORIZATION_SERVERS=https://bi193.com
MCP_PUBLIC_BASE_URL=https://store4ai-mcp.bi193.com
OAUTH_RESOURCE_NAME=BI193 Saleor MCP
```

it serves:

**`GET /.well-known/oauth-protected-resource/mcp`** (RFC 9728)
```json
{
  "resource": "https://store4ai-mcp.bi193.com/mcp",
  "authorization_servers": ["https://bi193.com/"],
  "scopes_supported": ["customer.read"],
  "bearer_methods_supported": ["header"],
  "resource_name": "BI193 Saleor MCP"
}
```

**`401 Unauthorized`** on any MCP call without/with-bad token, including:
```
WWW-Authenticate: Bearer error="invalid_token",
                  error_description="...",
                  resource_metadata="https://store4ai-mcp.bi193.com/.well-known/oauth-protected-resource/mcp"
```

MCP enforces tool-level scope on every call. A token with `scope: "customer.read"` cannot call `add_to_cart` (needs `customer.write`); calling `channels` (needs `admin`) is rejected.

---

## 3. What bi193.com MUST implement

### 3.1 Authorization Server Metadata (RFC 8414)

`GET https://bi193.com/.well-known/oauth-authorization-server`

```json
{
  "issuer": "https://bi193.com",
  "authorization_endpoint": "https://bi193.com/oauth/authorize",
  "token_endpoint":         "https://bi193.com/oauth/token",
  "registration_endpoint":  "https://bi193.com/oauth/register",
  "revocation_endpoint":    "https://bi193.com/oauth/revoke",
  "scopes_supported":       ["customer.read", "customer.write"],
  "response_types_supported": ["code"],
  "grant_types_supported":    ["authorization_code", "refresh_token"],
  "code_challenge_methods_supported": ["S256"],
  "token_endpoint_auth_methods_supported": ["none", "client_secret_post"]
}
```

Notes:
- `none` auth method is required for **public clients** (Claude Desktop, browser-launched agents) using PKCE.
- The MCP spec recommends supporting **Dynamic Client Registration** (RFC 7591) so clients can self-register; if you skip it for v1, hardcode a few client_ids (e.g., `openclaw`, `claude-desktop`) and document them.

### 3.2 `GET /oauth/authorize`

Query parameters (RFC 6749 §4.1.1 + RFC 7636 PKCE):

| Param | Required | Notes |
|---|---|---|
| `response_type` | yes | always `code` |
| `client_id` | yes | from registration |
| `redirect_uri` | yes | must match what was registered |
| `scope` | yes | space-separated, e.g. `"customer.read customer.write"` |
| `state` | yes | opaque, echo back unchanged |
| `code_challenge` | yes | PKCE — base64url(SHA-256(verifier)) |
| `code_challenge_method` | yes | always `S256` |
| `resource` | optional | RFC 8707 — should be `https://store4ai-mcp.bi193.com/mcp` |

Server-side logic:

```python
session = read_session_cookie(request)
if not session or not session.user_id:
    return redirect(f"/login?next={escape(full_authorize_url)}")

# user is logged in → show consent
return render("oauth_consent.html", {
    "client_id": client_id,        # show app name
    "scopes": parse_scopes(scope), # show the bullet list (see §3.3)
    "state": state,
    "code_challenge": code_challenge,
    "redirect_uri": redirect_uri,
})

# on POST with "Allow":
code = generate_random_code()  # 256-bit, URL-safe
store_in_redis(
    key=f"oauth:code:{code}",
    value={
        "user_id": session.user_id,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "code_challenge": code_challenge,
        "saleor_jwt": session.saleor_jwt,        # see §3.5
        "saleor_refresh": session.saleor_refresh,
    },
    ttl=600,  # 10 minutes per RFC 6749 §4.1.2
)
return redirect(f"{redirect_uri}?code={code}&state={state}")

# on POST with "Deny":
return redirect(f"{redirect_uri}?error=access_denied&state={state}")
```

### 3.3 Consent screen

Must list the **exact scopes being granted**, in plain language. Match the MCP scope mapping:

> **OpenClaw** wants permission to:
> - Browse products and categories *(customer.read)*
> - View your cart and order history *(customer.read)*
> - Modify your cart (add/update/remove items) *(customer.write)*
> - Set checkout details (email, shipping address) *(customer.write)*
> - Place orders on your behalf *(customer.write)*
>
> [ Deny ]   [ Allow ]
>
> You can revoke access anytime in Account → Connected Apps.

Implementation: derive the bullet list from the `scope` query param. Map:
- `customer.read` → "Browse products… / View your cart and orders"
- `customer.write` → "Modify cart / Set checkout details / Place orders"
- `admin` → **never grant via this consent screen.** Reject with `invalid_scope`.

### 3.4 `POST /oauth/token`

Two grant types.

**Authorization Code Exchange (RFC 6749 §4.1.3 + PKCE §4.5):**

Request (`Content-Type: application/x-www-form-urlencoded`):
```
grant_type=authorization_code
code=<from step 6>
redirect_uri=<must match step 4>
client_id=<must match step 4>
code_verifier=<plaintext PKCE verifier>
```

Server-side:
```python
record = redis.get(f"oauth:code:{code}")
if not record:                   return 400 invalid_grant
if record.client_id != client_id: return 400 invalid_grant
if record.redirect_uri != redirect_uri: return 400 invalid_grant
if base64url(sha256(code_verifier)) != record.code_challenge: return 400 invalid_grant
redis.delete(f"oauth:code:{code}")  # one-time use

# attach scope claim to a fresh Saleor JWT (re-mint or augment):
access_token = mint_or_attach_scope(record.saleor_jwt, record.scope)

return JSON({
    "access_token": access_token,
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": record.saleor_refresh,
    "scope": record.scope,
})
```

**Refresh Token Grant (RFC 6749 §6):**
```
grant_type=refresh_token
refresh_token=<value>
client_id=<value>
```
Returns a fresh `access_token` (and rotated `refresh_token` recommended). The refresh path should call Saleor's `tokenRefresh` mutation under the hood.

**Error responses** (RFC 6749 §5.2): use `invalid_grant`, `invalid_client`, `invalid_request`, `invalid_scope`. Return HTTP 400 (or 401 for `invalid_client`).

### 3.5 How to source the Saleor JWT

When a user logs in to bi193.com via the existing `/login` page, the backend already calls Saleor's `tokenCreate` mutation:

```graphql
mutation { tokenCreate(email: $email, password: $password) {
  token refreshToken csrfToken errors { code message }
}}
```

You currently store `token`/`refreshToken` somewhere (cookie, Redis session, etc.). For OAuth:
- Store them server-side keyed by session id (NOT in a cookie the agent can steal).
- When the user approves the consent (§3.2), copy `token` + `refreshToken` into the short-lived authorization-code record.
- On `/oauth/token`, return the Saleor JWT as `access_token`.

If you want to add a `scope` claim that wasn't in Saleor's original JWT, you have two options:

**Option A (preferred): re-sign with your own key.** bi193 mints its own JWT containing `{sub, email, scope, exp, saleor_token: <encrypted>}`. The MCP would need to validate against bi193's public key — change required on MCP side. *Skip for v1.*

**Option B (simpler): use Saleor JWT as-is, claim scope via convention.** Saleor JWTs already carry `is_staff`. The MCP verifier (`SaleorTokenVerifier`) treats:
- staff JWT (`is_staff: true`) → all scopes (`customer.read customer.write admin`)
- customer JWT (`is_staff: false`) — currently no scope claim → token is valid but `scope` is empty → all customer.* tools rejected.

**To fix Option B** without breaking Saleor: add a Saleor [JWT manager plugin](https://docs.saleor.io/developer/extending/plugins/manager) that injects a `scope` claim based on user permissions. Or, more pragmatic: **patch MCP** to default customer JWTs to `customer.read customer.write` when `scope` is missing. Choose with the MCP team.

### 3.6 Client registration

V1: hardcode a config table. Each entry:

```yaml
clients:
  - client_id: "openclaw"
    client_name: "OpenClaw Shopping Agent"
    redirect_uris:
      - "http://localhost:33418/oauth/callback"   # local agent
      - "https://openclaw.example.com/oauth/callback"
    grant_types: ["authorization_code", "refresh_token"]
    response_types: ["code"]
    token_endpoint_auth_method: "none"   # PKCE public client
  - client_id: "claude-desktop"
    client_name: "Claude Desktop"
    redirect_uris:
      - "http://127.0.0.1:*/callback"
      - "claude-desktop://oauth/callback"
    ...
```

V2: implement RFC 7591 Dynamic Client Registration so MCP clients we don't know about (picoclaw, goclaw, IDE plugins) can self-register.

### 3.7 `POST /oauth/revoke` (RFC 7009)

User clicks "Disconnect" in Account → Connected Apps:
```
token=<access_token or refresh_token>
client_id=<value>
```
- Mark token revoked in your store.
- Call Saleor `tokenRevoke` mutation with the underlying Saleor refresh token.
- Return HTTP 200 with empty body (per RFC).

---

## 4. Security checklist

- [ ] PKCE required (reject auth requests without `code_challenge`).
- [ ] Authorization codes are single-use, expire in ≤10 min, bound to `client_id` + `redirect_uri`.
- [ ] `redirect_uri` must be **exact-match** against the registered list (no wildcards in path; document any allowed schemes).
- [ ] `state` parameter must be present; client compares on callback (you don't need to validate, but document the requirement).
- [ ] Saleor JWT and refresh token NEVER appear in client-visible storage (cookies, localStorage, URL params). Only the consent record in Redis.
- [ ] CSRF protection on the consent POST (the form must carry a CSRF token bound to the session cookie).
- [ ] HTTPS-only on production; `Secure` + `HttpOnly` + `SameSite=Lax` on session cookie.
- [ ] Rate-limit `/oauth/token` (per client_id and per IP).
- [ ] Audit log: each `authorize` grant + each `token` exchange + each `revoke`.

---

## 5. Quick test plan once bi193 endpoints exist

```bash
# 1. Discovery
curl https://bi193.com/.well-known/oauth-authorization-server | jq
curl https://store4ai-mcp.bi193.com/.well-known/oauth-protected-resource/mcp | jq

# 2. PKCE pair
VERIFIER=$(openssl rand -base64 64 | tr -d '=+/' | head -c 64)
CHALLENGE=$(echo -n "$VERIFIER" | openssl dgst -sha256 -binary | base64 | tr '/+' '_-' | tr -d '=')

# 3. Open authorize URL in browser, log in, click Allow → callback gives ?code=…
open "https://bi193.com/oauth/authorize?response_type=code&client_id=openclaw&redirect_uri=http://localhost:8765/cb&scope=customer.read+customer.write&state=xyz&code_challenge=$CHALLENGE&code_challenge_method=S256"

CODE="<paste from callback>"

# 4. Exchange code → token
curl -X POST https://bi193.com/oauth/token \
  -d "grant_type=authorization_code&code=$CODE&client_id=openclaw&redirect_uri=http://localhost:8765/cb&code_verifier=$VERIFIER" | jq

# 5. Use the token against MCP
ACCESS=$(... .access_token from step 4 ...)
curl -X POST https://store4ai-mcp.bi193.com/mcp \
  -H "Authorization: Bearer $ACCESS" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"me","arguments":{}}}'
# expect: { user: { email, firstName, ... }, scopes: [...] }
```

---

## 6. MCP-side env vars (this repo) — for ops reference

| Var | Required | Example | Purpose |
|---|---|---|---|
| `OAUTH_AUTHORIZATION_SERVERS` | yes (to enable OAuth) | `https://bi193.com` | Comma-separated list of issuers MCP advertises in RFC 9728 metadata. |
| `MCP_PUBLIC_BASE_URL` | yes | `https://store4ai-mcp.bi193.com` | Public URL of MCP, used for the `resource` field. |
| `OAUTH_RESOURCE_NAME` | optional | `BI193 Saleor MCP` | Display name in metadata. |
| `SALEOR_REQUIRE_JWT_SHAPE` | optional | `true` (default) / `false` | If `false`, opaque (non-JWT) tokens are accepted with full staff scope — for app/staff tokens in dev. |
| `SALEOR_API_URL` | yes | `https://api.bi193.com/graphql/` | Saleor GraphQL endpoint MCP forwards to. |
| `ALLOWED_DOMAIN_PATTERN` | optional | `^https://api\.bi193\.com/graphql/$` | Regex restricting which `X-Saleor-API-URL` header values are accepted. |

When `OAUTH_AUTHORIZATION_SERVERS` is unset, MCP runs in legacy mode (header-token only, no scope enforcement). This is how the production server is currently configured — set the var to enable the OAuth flow once bi193 endpoints are live.

---

## 7. Out of scope for v1 (track for later)

- Dynamic Client Registration (RFC 7591) — V1 hardcodes clients.
- Pushed Authorization Requests (RFC 9126).
- DPoP (RFC 9449) — sender-constrained tokens.
- Token introspection endpoint (RFC 7662) — MCP currently decodes JWT inline.
- Multi-tenant client management UI.
