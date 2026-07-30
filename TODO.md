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
- [ ] Step 1: Server infra — Debian install, Docker, Tailscale, Postgres container
- [ ] Step 1.1 Article retention/cleanup — periodic job (APScheduler) to delete old,
      unstarred articles so storage doesn't grow unbounded. Decide exact
      rule (age cutoff? per-feed cap?) when implementing.
- [ ] Step 1.2 Consider optional `image_url` column on `articles` if feeds provide
      a thumbnail/enclosure — not in original schema, decide if wanted.
- [ ] Step 2: Backend skeleton — SQLAlchemy models, Alembic, basic CRUD, containerize
- [ ] Step 3: Auth — password hashing, sessions table, login endpoint,
      `get_current_user` dependency, admin CLI for user creation
- [ ] Step 4: Feed fetching — feedparser + APScheduler
- [ ] Step 5: Subscriptions + `/sync` endpoint
- [ ] Step 6: OPML import
- [ ] Step 7: Desktop client (PySide6)
- [ ] Step 8: Android client (Kotlin + Compose) — skeleton started early,
      see below
- [ ] Step 9: Polish — full-text search, unread counts, favicons, push
      notifications (FCM)
