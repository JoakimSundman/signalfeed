# TODO

## CI / DevOps
- [ ] `docker-build.yml` — waiting on a `server/Dockerfile` to exist first
- [ ] `android.yml` — build check (`gradlew assembleDebug`) + `ktlint`,
      once Android skeleton exists
- [ ] Consider `detekt` for Kotlin static analysis (optional, security-focused)
- [ ] `dependabot.yml` for scheduled version-update PRs (not just security
      patches) — hold off until there are enough dependencies for this
      to matter

## Build order
- [x] Step 1: Server infra — Debian install, Docker, Tailscale, Postgres container (Debian, Tailscale install awaits for deployment)
- [ ] Step 1.1 Article retention/cleanup — periodic job (APScheduler) to delete old unstarred
      articles so disk usage doesn't grow without bound. Decide exact
      rule (age cutoff? per-feed cap?) when implementing.
- [x] Step 1.2 Consider optional `image_url` column on `articles` if feeds provide
      a thumbnail/enclosure — not in original schema, decide if wanted. Nullable `image_url` added directly to schema 
- [ ] Step 2: Backend skeleton — SQLAlchemy models, Alembic, basic CRUD, containerize
- [ ] Step 3: Auth — password hashing, sessions table, login endpoint,
      `get_current_user` dependency, admin CLI for user creation
  - [ ] Rate limiting on `/login` (brute-force protection) — consider `slowapi`
  - [ ] Review timing-attack surface on username lookup (low priority at
        current scale, but worth revisiting if the user base grows)
- [ ] Step 4: Feed fetching — feedparser + APScheduler
- [ ] Step 5: Subscriptions + `/sync` endpoint
- [ ] Step 6: OPML import
- [ ] Step 7: Desktop client (PySide6)
- [ ] Step 8: Android client (Kotlin + Compose) — skeleton started early,
      see below
- [ ] Step 9: Polish — full-text search, unread counts, favicons, push
      notifications (FCM)

## Infra (later)
- [ ] Set up HTTPS via `tailscale cert` once server is deployed on Tailscale
      (see decisions.md)
- [ ] Automate `tailscale cert` renewal (cron, ~90 day expiry)
