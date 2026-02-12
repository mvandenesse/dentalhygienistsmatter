# Cloudflare views counter (deploy-time)

This repo can display a **"Views since launch"** number in the footer.

It is fetched **at deploy/build time** from Cloudflare Analytics and baked into the static site.

## How it works
- `scripts/fetch-cf-views.mjs` runs automatically via `npm run prebuild`.
- It queries Cloudflare GraphQL:
  - `httpRequests1dGroups.sum.pageViews`
  - filtered by zone + hostname + date range.
- It writes `src/data/site-metrics.json`.
- `src/layouts/BaseLayout.astro` reads that file and shows the counter.

## Required env vars (Cloudflare Pages build settings)
- `CF_API_TOKEN` — Cloudflare API token (read-only analytics for the zone)
- `CF_ZONE_ID` — Zone ID for the domain
- `CF_HOSTNAME` — Optional (defaults to `dentalhygienistsmatter.com`)
- `VIEWS_SINCE` — Launch date boundary, `YYYY-MM-DD`

## Notes
- If env vars are missing or the API call fails, deploy will **not fail**; the footer counter will simply be hidden.
- The counter updates only when you deploy.
