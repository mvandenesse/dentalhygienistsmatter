# Email → Posts ingestion

This repo supports a **community posts** section backed by markdown files in:

- `src/content/posts/*.md`

The ingest script reads an IMAP mailbox and:
- creates a post for each email whose subject starts with `POST:`
- removes the post if the originating email is deleted

## How it works
- Reads mailbox via IMAP
- Searches for messages with `Subject` containing `POST:`
- Extracts:
  - title: subject line after `POST:`
  - author: from email “From” display name (fallback to address)
  - date: email date header (fallback now)
  - body: plain text, stripped/sanitized
- Writes post file: `src/content/posts/<slug>.md`
- Tracks mapping in `.data/email-index.json` (not committed)

## Safety
Inbound content is treated as untrusted:
- HTML is stripped
- output is stored as plain markdown text
- post length is clipped

## Environment variables
Required:
- `IMAP_HOST`
- `IMAP_PORT`
- `IMAP_USER`
- `IMAP_PASS`
- `IMAP_SECURE` (`true` or `false`)
- `IMAP_MAILBOX` (e.g., `INBOX`)

## Run
```bash
npm run ingest:email
```

## Publishing + notifications
This script only updates files. A wrapper should:
- run the ingest
- commit + push changes
- notify the admin about created/removed posts
