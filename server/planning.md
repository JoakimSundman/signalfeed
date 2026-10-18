# API planning

Working notes for the backend CRUD phase. Not a spec: things that are
cheap to change later are left open on purpose.

## Concepts

- **Feed**: a source (e.g. Krebs on Security). One row per feed URL,
  shared between all users.
- **Article**: one post from a feed. Shared. Only a summary is stored,
  plus a link to the original.
- **Subscription**: links a user to a feed (with an optional folder).
- **ArticleState**: per-user read/starred state for an article.
- The server is the source of truth. "Offline" means the server is
  unreachable (e.g. Tailscale down); the device may still have internet
  and can open articles on the original site.

## Resources and operations

| Resource | Create | Read | Update | Delete |
|---|---|---|---|---|
| Feed (shared) | via subscribe | via subscription | fetcher only | never by users |
| Subscription | POST | GET (own) | PATCH (folder) | DELETE (unsubscribe) |
| Article (shared) | fetcher only | GET (visible to user) | no | retention job |
| ArticleState | upsert on first change | included in article reads | upsert (read/starred) | with user |

## Decided

- **Unread:** lazy. No `ArticleState` row means unread. "Mark unread"
  sets `is_read = false`; the row is never deleted, so the change
  propagates through `updated_at`.
- **Read is sticky:** only an explicit unread operation changes read to
  unread. Sync never flips it implicitly.
- **Time:** the server's clock only. `updated_at` is set on receipt;
  client timestamps are not used.
- **Conflicts:** last received change wins. Known edge case: an old
  offline "read" arriving after a newer "unread" from another device
  wins. Accepted.
- **Visibility:** an article is visible to a user if their feed
  subscription exists and `published_at >= added_at - 24h`, plus any
  article the user has starred (even after unsubscribing).
  `published_at` falls back to fetch time when the feed gives no date.
- **Starred:** never deleted while starred. Retention only deletes
  articles that no user has starred. Feed rows are never deleted by
  users; the fetcher skips feeds with no subscribers.
- **Pagination:** cursor on `(published_at, id)`.
- **Folders:** one level, user-named, stored as a string in
  `folder_or_tag` (trimmed). One folder per feed per user.
- **Authorization:** user id always comes from the token, never from the
  request. Every query on per-user data filters on it. Other users' rows
  return 404, not 403. Every endpoint gets a test where user A tries to
  reach user B's data.
- **Constraints:** unique `(user_id, feed_id)` on subscriptions, unique
  `(user_id, article_id)` on article_state, unique `(feed_id, guid)` on
  articles (`guid` and `url` are no longer globally unique).
- **ON DELETE:** deleting a user removes only that user's rows
  (sessions, subscriptions, article_state). `articles.feed_id` and
  `subscriptions.feed_id` are RESTRICT. `article_state.article_id`
  cascades.
- **Schema policy:** after the constraints migration, existing fields are
  not renamed or retyped. Missing data gets a new field instead. Known
  debt, accepted for this passion project.

## Sync

- One idempotent `POST /sync`. Up: an ordered list of operations
  (`read`, `unread`, `star`, `unstar`, each with an `article_id`). Down:
  new articles, changed states, the full subscription list.
- New articles: `id > last_seen_id`. Changed states: `updated_at >
  cursor`, with a few seconds of overlap; clients apply idempotently.
  The server returns both cursors.
- Subscriptions are sent in full each time (no tombstones). Clients
  remove expired articles with the retention rule; starred articles are
  never removed unless unstarred.
- Responses are paginated with a cursor and `has_more`. A new device's
  first sync is large and is looped until `has_more` is false; after
  that only changes are sent.
- `POST /articles/{article_id}/unread` has no body and is idempotent.
  It shares its implementation with the `unread` operation in `/sync`.
- Clients queue operations while the server is unreachable and replay
  them in order.

## Open

- "Mark all as read": scope (feed or folder) and an upper bound (up to
  article id X) so articles arriving meanwhile are not marked.
- Article list filters and default sort (unread, starred, per feed).
- Retention numbers and fetch interval (no schema impact; decide when
  implementing).
- **Retention:** a config value (default to be chosen, longer than a day,
  at least as long as the subscribe backfill window). Never deletes
  starred articles. The fetcher skips feed items older than the
  retention window so deleted articles do not come back. Items without a
  date need handling when the fetcher is built.

## Views and what they need from the API

(One table per view: shows / actions / endpoints. Might make sketches in docs/.)

## After v1

- User deletion (CLI) and password change
- Full-text search over articles
- Push notifications
- Favicons
- Feed discovery: URL autodiscovery and a bundled starter list in v1,
  name search over the web later
- Admin view with manual feed refresh

## Notes found while building the client

...