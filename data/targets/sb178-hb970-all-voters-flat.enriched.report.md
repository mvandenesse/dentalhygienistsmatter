# SB178/HB970 all-voters list — additional public phone numbers enrichment (2026-02-14)

## Summary
- Input: `sb178-hb970-all-voters-flat.json` (140 people)
- Output JSON: `sb178-hb970-all-voters-flat.enriched.json`
- Added `additional_phones` array for each person (empty when none found)
- Filled missing `district_phone` for 4 Senators based on **official Virginia Senate member pages**.
- Added 2 additional *fax* numbers (publicly listed) to `additional_phones`.

## Coverage stats
- People total: **140**
- People with at least one new/updated phone value:
  - `district_phone` filled where previously null: **4** (member_id: S96, S82, S130, S132)
  - `additional_phones` entries added: **2** (fax numbers for S96, S82)
- People with campaign/extra public phone found beyond capitol/district: **0** reliably, except where campaign pages duplicated district office numbers (see notes).

## Changes made (details)
### S96 — Sen. Bill DeSteph
- `district_phone` set to **(757) 321-8180**
- `additional_phones`: Fax **(757) 631-6150**
- Source (official): https://apps.senate.virginia.gov/Senator/memberpage.php?id=S96
- Also observed on campaign contact page (same district office number): https://www.billdesteph.com/contact/

### S82 — Sen. William M. Stanley, Jr.
- `district_phone` set to **(540) 821-3066**
- `additional_phones`: Fax **(540) 721-6405**
- Source (official): https://apps.senate.virginia.gov/Senator/memberpage.php?id=S82

### S130 — Sen. Angelia Williams Graves
- `district_phone` set to **(757) 524-4941**
- Source (official): https://apps.senate.virginia.gov/Senator/memberpage.php?id=S130

### S132 — Sen. Luther H. Cifers III
- `district_phone` set to **(804) 372-0953**
- Source (official): https://apps.senate.virginia.gov/Senator/memberpage.php?id=S132
- Note: on the official page, this phone is listed alongside a Richmond mailing address; the labeling (capitol vs district) is not explicit in scraped text.

## Ambiguous / conflicts (not added as new phones)
1) **S82 (Stanley)**
   - Official Senate member page lists phone **(540) 821-3066**.
   - Campaign site landing page shows **540 821 3058** (different last two digits).
   - Campaign site URL (redirects): https://stanleyforsenate.com/  → https://senatorbillstanley.com/
   - Recommendation: treat the campaign-site number as *possibly outdated/typo* unless independently confirmed.

2) **S96 (DeSteph)**
   - Official Senate member page lists capitol phone **(804) 698-7520**.
   - Campaign contact page shows in-session office phone **(804) 698-7508** (conflicts; likely site typo/outdated).
   - Recommendation: trust official Senate directory number.

## Access limitations
- Some campaign sites appear protected by Cloudflare and returned HTTP 403 to `web_fetch` (notably `glensturtevant.com` and `taradurant.com`). Without a working browser automation environment, those could not be checked for public phone numbers.
- `rouseforsenate.com` was accessible but the homepage content fetched did not include a phone number.

