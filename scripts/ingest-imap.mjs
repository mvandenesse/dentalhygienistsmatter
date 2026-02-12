import 'dotenv/config';
import { ImapFlow } from 'imapflow';
import { simpleParser } from 'mailparser';
import slugify from 'slugify';
import sanitizeHtml from 'sanitize-html';
import fs from 'node:fs/promises';
import path from 'node:path';

const REQUIRED_ENV = [
  'IMAP_HOST',
  'IMAP_PORT',
  'IMAP_USER',
  'IMAP_PASS',
  'IMAP_SECURE',
  'IMAP_MAILBOX',
];

function getEnv(name) {
  const v = process.env[name];
  if (!v) throw new Error(`Missing env var: ${name}`);
  return v;
}

function safeTextToMarkdown(input) {
  // Treat inbound as untrusted. Strip any HTML, then keep plain text.
  const stripped = sanitizeHtml(input ?? '', { allowedTags: [], allowedAttributes: {} });
  // Normalize line endings
  const normalized = stripped.replace(/\r\n/g, '\n').trim();

  // Hard limit to prevent abuse / huge posts
  const MAX = 5000;
  const clipped = normalized.length > MAX ? normalized.slice(0, MAX) + '\n\n[Truncated]' : normalized;

  // Escape anything that might be interpreted as HTML when rendered.
  // Markdown is generally safe in Astro, but keep it conservative.
  return clipped;
}

function pickAuthor(parsed) {
  // Prefer display name from From: header; fallback to email address.
  const from = parsed?.from?.value?.[0];
  if (!from) return undefined;
  if (from.name && from.name.trim()) return from.name.trim();
  if (from.address) return from.address;
  return undefined;
}

function wantsAnonymous(text) {
  return /please\s+post\s+as\s+anonymous/i.test(text ?? '');
}

function deriveTitle(parsed) {
  const subject = (parsed?.subject ?? '').toString().trim();
  // Expect: POST: Title
  const m = subject.match(/^\s*POST\s*:\s*(.+?)\s*$/i);
  if (m?.[1]) return m[1];
  return subject || 'Community post';
}

function toFrontmatter({ title, dateISO, author }) {
  const esc = (s) => s.replace(/"/g, '\\"');
  const lines = [
    '---',
    `title: "${esc(title)}"`,
    `date: ${dateISO}`,
  ];
  if (author) lines.push(`author: "${esc(author)}"`);
  lines.push('published: true');
  lines.push('---');
  return lines.join('\n');
}

async function loadIndex(indexPath) {
  try {
    const raw = await fs.readFile(indexPath, 'utf8');
    return JSON.parse(raw);
  } catch {
    return { messageIdToSlug: {}, lastRunAt: null };
  }
}

async function saveIndex(indexPath, index) {
  await fs.mkdir(path.dirname(indexPath), { recursive: true });
  await fs.writeFile(indexPath, JSON.stringify(index, null, 2) + '\n', 'utf8');
}

async function main() {
  for (const k of REQUIRED_ENV) getEnv(k);

  const config = {
    host: getEnv('IMAP_HOST'),
    port: Number(getEnv('IMAP_PORT')),
    secure: getEnv('IMAP_SECURE').toLowerCase() === 'true',
    auth: {
      user: getEnv('IMAP_USER'),
      pass: getEnv('IMAP_PASS'),
    },
    logger: false,
  };

  const mailbox = getEnv('IMAP_MAILBOX');
  const indexPath = path.resolve('.data/email-index.json');
  const postsDir = path.resolve('src/content/posts');

  const index = await loadIndex(indexPath);

  const client = new ImapFlow(config);
  const created = [];
  const removed = [];

  await client.connect();
  try {
    await client.mailboxOpen(mailbox);

    // Gmail IMAP header search can be finicky; fetch recent mail and filter by subject.
    const allUids = await client.search({ all: true });
    const uids = allUids; // mailbox is typically small; can optimize later.

    const seenMessageIds = new Set();

    for await (const msg of client.fetch(uids, { uid: true, envelope: true, source: true })) {
      const parsed = await simpleParser(msg.source);
      const subject = (parsed.subject ?? '').toString();
      if (!/^\s*POST\s*:/i.test(subject)) continue;

      const messageId = (parsed.messageId ?? msg.envelope?.messageId ?? '').toString();
      if (!messageId) continue;

      seenMessageIds.add(messageId);

      if (index.messageIdToSlug[messageId]) {
        continue; // already ingested
      }

      const title = deriveTitle(parsed);
      const date = parsed.date ? new Date(parsed.date) : new Date();
      const dateISO = date.toISOString();

      // Prefer text; fallback to stripped html.
      const text = parsed.text ?? (parsed.html ? sanitizeHtml(parsed.html, { allowedTags: [], allowedAttributes: {} }) : '');
      const body = safeTextToMarkdown(text);

      const author = wantsAnonymous(body) ? 'Anonymous' : pickAuthor(parsed);

      const slugBase = slugify(title, { lower: true, strict: true, trim: true }) || 'post';
      const uniqueSuffix = Date.now().toString(36);
      const slug = `${slugBase}-${uniqueSuffix}`;

      const fm = toFrontmatter({ title, dateISO, author });
      const content = `${fm}\n\n${body}\n`;

      await fs.mkdir(postsDir, { recursive: true });
      await fs.writeFile(path.join(postsDir, `${slug}.md`), content, 'utf8');

      index.messageIdToSlug[messageId] = slug;
      created.push({ slug, title, author, date: dateISO, messageId });
    }

    // Deletion handling: if a previously ingested message-id is no longer present in the mailbox search results, remove its post.
    const existingMessageIds = new Set(Object.keys(index.messageIdToSlug || {}));

    for (const messageId of existingMessageIds) {
      if (!seenMessageIds.has(messageId)) {
        const slug = index.messageIdToSlug[messageId];
        const file = path.join(postsDir, `${slug}.md`);
        try {
          await fs.unlink(file);
          removed.push({ slug, messageId });
        } catch {
          // file might already be gone
        }
        delete index.messageIdToSlug[messageId];
      }
    }

    index.lastRunAt = new Date().toISOString();
    await saveIndex(indexPath, index);

    // Print machine-readable summary
    process.stdout.write(JSON.stringify({ created, removed, lastRunAt: index.lastRunAt }, null, 2));
  } finally {
    await client.logout().catch(() => {});
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
