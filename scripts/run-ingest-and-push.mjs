import 'dotenv/config';
import { execSync } from 'node:child_process';

function sh(cmd) {
  return execSync(cmd, { stdio: ['ignore', 'pipe', 'pipe'], encoding: 'utf8' });
}

function trySh(cmd) {
  try {
    return { ok: true, out: sh(cmd) };
  } catch (e) {
    return { ok: false, out: e.stdout?.toString?.() ?? '', err: e.stderr?.toString?.() ?? String(e) };
  }
}

function main() {
  const summaryRaw = sh('node scripts/ingest-imap.mjs');
  const summary = JSON.parse(summaryRaw);

  const status = sh('git status --porcelain');
  const changed = status.trim().length > 0;

  if (changed) {
    sh('git add -A');
    const msgParts = [];
    if (summary.created?.length) msgParts.push(`+${summary.created.length} post(s)`);
    if (summary.removed?.length) msgParts.push(`-${summary.removed.length} post(s)`);
    const msg = msgParts.length ? `Ingest email posts (${msgParts.join(', ')})` : 'Ingest email posts';
    sh(`git commit -m "${msg.replace(/\"/g, '\\"')}"`);
    sh('git push');
  }

  process.stdout.write(JSON.stringify({ ...summary, changed }, null, 2));
}

main();
