import fs from 'node:fs/promises';
import path from 'node:path';

const OUT_PATH = path.resolve('src/data/site-metrics.json');

function env(name) {
  return process.env[name]?.toString().trim();
}

async function writeOut(obj) {
  await fs.mkdir(path.dirname(OUT_PATH), { recursive: true });
  await fs.writeFile(OUT_PATH, JSON.stringify(obj, null, 2) + '\n', 'utf8');
}

async function main() {
  const token = env('CF_API_TOKEN');
  let zoneTag = env('CF_ZONE_ID');

  // Launch date boundary (YYYY-MM-DD). Required for true “since launch”.
  const since = env('VIEWS_SINCE');
  const hostname = env('CF_HOSTNAME') || 'dentalhygienistsmatter.com';

  // If zone id isn't provided (or looks wrong), try to resolve it by hostname.
  const looksLikeZoneId = (v) => typeof v === 'string' && /^[a-f0-9]{32}$/i.test(v);
  if (token && (!looksLikeZoneId(zoneTag))) {
    try {
      console.warn('[cf-views] CF_ZONE_ID missing/invalid; attempting to resolve zone id by hostname');
      const url = `https://api.cloudflare.com/client/v4/zones?name=${encodeURIComponent(hostname)}&status=active&per_page=50`;
      const r = await fetch(url, {
        headers: { authorization: `Bearer ${token}` },
      });
      const j = await r.json().catch(() => null);
      const id = j?.result?.[0]?.id;
      if (looksLikeZoneId(id)) {
        zoneTag = id;
        console.log('[cf-views] resolved zone id', { zoneTag: `${zoneTag.slice(0, 6)}…${zoneTag.slice(-6)}` });
      } else {
        console.warn('[cf-views] could not resolve zone id', { apiSuccess: j?.success, errors: j?.errors });
      }
    } catch (e) {
      console.warn('[cf-views] zone id resolution failed', String(e?.stack || e));
    }
  }


  console.log('[cf-views] start', { hostname, since, zoneTag: zoneTag ? `${zoneTag.slice(0, 6)}…${zoneTag.slice(-6)}` : null });

  // Soft-fail by writing a sentinel file if not configured.
  if (!token || !zoneTag || !since) {
    console.warn('[cf-views] missing env var(s)', {
      hasToken: Boolean(token),
      hasZoneId: Boolean(zoneTag),
      hasSince: Boolean(since),
    });

    await writeOut({
      viewsSinceLaunch: null,
      asOf: new Date().toISOString(),
      note: 'Cloudflare views not configured. Set CF_API_TOKEN, CF_ZONE_ID, VIEWS_SINCE (YYYY-MM-DD).',
    });
    return;
  }

  const query = `
    query($zoneTag: String!, $since: String!, $until: String!) {
      viewer {
        zones(filter: { zoneTag: $zoneTag }) {
          httpRequests1dGroups(
            limit: 1000
            filter: { date_geq: $since, date_leq: $until }
          ) {
            sum {
              pageViews
            }
          }
        }
      }
    }
  `;

  const until = new Date().toISOString().slice(0, 10); // YYYY-MM-DD

  console.log('[cf-views] fetching', { since, until, hostname });

  const resp = await fetch('https://api.cloudflare.com/client/v4/graphql', {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      query,
      variables: { zoneTag, since, until },
    }),
  });

  if (!resp.ok) {
    const body = await resp.text().catch(() => '');
    console.error('[cf-views] http error', resp.status, body.slice(0, 400));
    throw new Error(`Cloudflare GraphQL error ${resp.status}: ${body.slice(0, 400)}`);
  }

  const json = await resp.json();
  if (json.errors?.length) {
    console.error('[cf-views] graphql errors', json.errors);
    throw new Error(`Cloudflare GraphQL returned errors: ${JSON.stringify(json.errors).slice(0, 600)}`);
  }

  const groups = json?.data?.viewer?.zones?.[0]?.httpRequests1dGroups || [];
  const views = groups.reduce((acc, g) => acc + (g?.sum?.pageViews ?? 0), 0);

  console.log('[cf-views] ok', { viewsSinceLaunch: views });

  await writeOut({
    viewsSinceLaunch: views,
    asOf: new Date().toISOString(),
    since,
    source: 'cloudflare:httpRequests1dGroups.sum.pageViews',
    hostname,
    note: 'Hostname filter not supported on httpRequests1dGroups for this zone; value reflects zone totals.',
  });
}

main().catch(async (err) => {
  console.error('[cf-views] failed', String(err?.stack || err));

  // Don’t break deploys; write a sentinel and exit 0.
  await writeOut({
    viewsSinceLaunch: null,
    asOf: new Date().toISOString(),
    error: String(err?.stack || err),
    note: 'Cloudflare views fetch failed; deploy continued. Check CF_API_TOKEN/CF_ZONE_ID/VIEWS_SINCE.',
  });
});
