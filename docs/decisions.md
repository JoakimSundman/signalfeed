# Architecture Decisions

Short log of non-trivial technical decisions for signalfeed, with context
and reasoning. Newest first. 

Note: this log was started on 2026-09-30. Earlier entries below were
written retroactively on that date and reflect decisions made over the
preceding development sessions, not necessarily made on the date shown.

---

## HTTPS via `tailscale cert`, layered on top of WireGuard

**Date:** 2026-09-30
**Context:** Server is only reachable via Tailscale (no open ports to the
internet). WireGuard already encrypts all tailnet traffic end-to-end, so
plain HTTP between Tailscale nodes is not transmitted in cleartext over
the physical network. However, if a client ever connects via the server's
raw LAN IP instead of its Tailscale address, traffic would be unencrypted
and sniffable on that network segment.
**Decision:** Use `tailscale cert` to issue a real, publicly-trusted TLS
certificate for the server's MagicDNS name, and serve the API over HTTPS
via uvicorn's built-in TLS support. This is defense-in-depth on top of
WireGuard, not a replacement for it.
**Alternatives considered:** Plain HTTP relying solely on WireGuard
(rejected: fragile if a client ever bypasses the tailnet address);
self-signed certificates (rejected: requires manual trust-store
distribution to every client, more operational overhead than
`tailscale cert` for no real benefit).
**Consequences:** Certificate must be renewed periodically (~90 days,
Let's Encrypt default). No extra trust configuration needed on clients
since the cert is publicly trusted.

---

## No public user registration

**Date:** 2026-09-30
**Context:** signalfeed is for private use — one admin (the person who
deploys it) plus up to ~5 trusted accounts. No need to support strangers
signing up.
**Decision:** No `POST /register` endpoint. The only way to create a user
is `create_user.py`, an interactive CLI script run locally on the server
by whoever has terminal access. It is gated by a separate
`ADMIN_CLI_PASSWORD` (not the same as the password pepper).
**Consequences:** Simpler API surface (one less public endpoint to secure).
Adding a new user always requires server access — acceptable for this
project's scale, would not scale to a multi-tenant product.

---

## Password pepper in addition to per-user salt

**Date:** 2026-09-30
**Context:** bcrypt already generates a unique salt per password
automatically, which protects against rainbow tables and cross-user
batch cracking. A pepper is an additional, application-wide secret that
protects against a database-only leak (e.g. a SQL dump or backup leak)
where the server's environment variables are not also compromised.
**Decision:** Add a single, application-wide pepper stored in
`PASSWORD_PEPPER` (`.env`, never committed), concatenated with the
password before hashing. Pepper is 16 bytes (`secrets.token_hex(16)`,
32 hex characters), chosen to leave headroom under bcrypt's 72-byte
input limit alongside a reasonably long password (≤ 40 bytes after the
pepper is accounted for).
**Alternatives considered:** Per-user pepper (rejected: requires separate
secret storage/rotation per user, complexity not justified at this
scale); no pepper at all (rejected: cheap to add before any real user
data exists, expensive to retrofit later since it would invalidate every
existing hash).
**Consequences:** If the pepper is ever lost or changed, all existing
password hashes become unverifiable — this is permanent, unlike rotating
a token secret. Must be documented clearly in `CONTRIBUTING.md` for
anyone self-hosting.

---

## bcrypt directly, not passlib

**Date:** 2026-09-30
**Context:** Originally planned to use `passlib[bcrypt]` per common
FastAPI tutorials. Passlib has not been released since 2020 and has a
known compatibility break with bcrypt >= 4.1 (`AttributeError:
module 'bcrypt' has no attribute '__about__'`), which is unresolved
upstream.
**Decision:** Use the `bcrypt` package directly. No abstraction layer.
**Alternatives considered:** `pwdlib` (a maintained passlib-style
successor supporting argon2 and bcrypt) — reasonable alternative, not
chosen only because direct `bcrypt` was simpler for a project with no
existing hashes to migrate.
**Consequences:** Slightly more code in `security.py` (manual
encode/decode, explicit salt generation) compared to passlib's
`CryptContext`, in exchange for no dependency on an unmaintained library.

## SQLAlchemy 2.0 style (`Mapped`/`mapped_column`), not SQLModel

**Date:** 2026-09-30
**Context:** Needed an ORM approach for the six models. SQLModel
(Pydantic + SQLAlchemy combined) is a popular choice for FastAPI
projects and reduces boilerplate by unifying the database model and the
API schema into one class.
**Decision:** Use plain SQLAlchemy 2.0 with `Mapped`/`mapped_column`
type-annotated models, kept separate from any Pydantic request/response
schemas.
**Alternatives considered:** SQLModel (rejected: couples the database
schema to the API schema, which becomes awkward once they need to
diverge — e.g. a response should never expose `password_hash`, even
though it's a real column on `User`); legacy SQLAlchemy Core/declarative
style without type annotations (rejected: 2.0 style is the current
recommended approach and plays better with static type checkers).
**Consequences:** Slightly more code up front (separate Pydantic schemas
for request/response bodies, not auto-generated from the model), in
exchange for a cleaner separation between "what's in the database" and
"what the API exposes".