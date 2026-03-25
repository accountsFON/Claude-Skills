---
name: wp-local-landings
description: >
  Workflow for auditing and creating WordPress Local Landing Pages (custom post type: `local`)
  for SEO purposes across multiple sites managed via ManageWP. Use this skill whenever the user
  mentions creating local pages, local landing pages, local SEO pages, or filling in missing
  service/location combos on a WordPress site. Also trigger when the user says "let's do [site name]"
  in the context of this workflow, asks to find gaps in local landing pages, wants to add new
  service or geo keywords to a WP site, or references ManageWP + WordPress local pages in any way.
  This skill covers: logging into WP via ManageWP, auditing all existing local pages, identifying
  missing service × location combos, suggesting new keyword opportunities, duplicating existing
  pages as templates, updating ACF fields (keyword, location, main_image), setting Yoast SEO
  focus keyphrases, updating titles/slugs, and publishing or saving as draft.
---

# WordPress Local Landing Pages Workflow

You are helping manage SEO-focused Local Landing Pages on WordPress sites. These are a custom
post type (`local`) where each page targets one service + one location (e.g., "Deck Construction
in Oak Hill, FL"). The goal is to fill gaps in service × location coverage and expand into new
keyword opportunities.

---

## Step 1: Log In via ManageWP

1. Navigate to `https://orion.managewp.com/dashboard/websites?type=thumbnail`
2. Find the target site's domain in the link list:
   ```javascript
   Array.from(document.querySelectorAll('a[href]'))
     .filter(a => a.href.startsWith('http') && !a.href.includes('managewp'))
     .map(a => a.href)
   ```
3. Find the `site-admin/XXXXXX` link that appears **just before** the target domain link — that ID belongs to the site.
4. Navigate to `https://orion.managewp.com/site-admin/XXXXXX` — ManageWP will auto-login.
5. Once logged in, navigate directly to the local post type list:
   `https://[domain]/wp-admin/edit.php?post_type=local`
   - If it redirects to dashboard, the post type slug may differ — check the admin menu:
     ```javascript
     Array.from(document.querySelectorAll('#adminmenu a'))
       .filter(a => a.href.includes('post_type'))
       .map(a => ({text: a.textContent.trim(), href: a.href}))
     ```

---

## Step 2: Audit Existing Pages

Scan all pages (paginate if needed) and build a service × location matrix.

```javascript
// Get all titles and post IDs from the list
Array.from(document.querySelectorAll('tr.type-local')).map(row => ({
  title: row.querySelector('.row-title')?.textContent?.trim(),
  postId: Array.from(row.querySelectorAll('a'))
    .find(a => a.textContent.trim() === 'Edit')?.href?.match(/post=(\d+)/)?.[1],
  status: row.classList.contains('status-draft') ? 'draft' : 'published'
})).filter(r => r.title);
```

Check the total count:
```javascript
document.querySelector('.subsubsub')?.textContent?.trim();
```

Navigate page 2+ with `&paged=2`, `&paged=3`, etc. if needed.

**Build the matrix** — present findings to the user as a table:
| Service | Location A | Location B | Location C | ... |
|---------|-----------|-----------|-----------|-----|
| Service 1 | ✅ | ✅ | ❌ | |
| Service 2 | ✅ | ❌ | ❌ | |

Highlight **missing combos** clearly — these are the gaps to fill.

---

## Step 3: Identify Opportunities

Present two categories of opportunities:

### Missing combos (existing service + existing location)
These are the highest-priority gaps — templates already exist, just needs duplication.

### New service keywords
Based on the business type and existing services, suggest 4-6 services not yet covered.
Think about: what do similar businesses in this market typically offer? What are high-intent
search terms in this region?

### New geo locations
Based on existing locations, suggest nearby markets not yet covered.
Consider: neighboring cities, suburbs, counties — especially those with population growth
or underserved demand.

---

## Step 4: Discover ACF Field Keys

Before creating pages, open any existing local page to get the ACF field keys for this site:

```javascript
Array.from(document.querySelectorAll('[data-name]')).map(el => ({
  dataName: el.dataset.name,
  inputName: el.querySelector('input, textarea')?.name,
  value: el.querySelector('input, textarea')?.value
})).filter(f => f.inputName?.includes('acf'));
```

Common fields (keys vary per site):
- **keyword** — the service name (e.g., "Flooring Installation")
- **location** — the geo target (e.g., "Port Orange, FL")
- **main_image** — attachment ID for the hero image

Note the field keys (e.g., `acf[field_68d2a231fb1bd]`) — you'll use them for all pages on this site.

---

## Step 5: Create New Pages

### 5a. Duplicate a template page

Find the post ID of the best matching existing page to use as a template (same service if available).

```javascript
// Trigger "Duplicate This" plugin for a specific post ID
const rows = Array.from(document.querySelectorAll('tr.type-local'));
const targetRow = rows.find(row =>
  Array.from(row.querySelectorAll('a'))
    .find(a => a.textContent.trim() === 'Edit')?.href?.includes('post=XXXXX')
);
const dupLink = targetRow
  ? Array.from(targetRow.querySelectorAll('a')).find(a => a.textContent.includes('Duplicate This'))
  : null;
if (dupLink) { window.location.href = dupLink.href; }
```

After duplication, navigate to the draft list to get the new post ID:
`https://[domain]/wp-admin/edit.php?post_type=local&post_status=draft`

```javascript
Array.from(document.querySelectorAll('tr.type-local')).map(row => ({
  title: row.querySelector('.row-title')?.textContent?.trim(),
  postId: Array.from(row.querySelectorAll('a'))
    .find(a => a.textContent.trim() === 'Edit')?.href?.match(/post=(\d+)/)?.[1]
}));
```

### 5b. Update all fields

Navigate to `https://[domain]/wp-admin/post.php?post=XXXXX&action=edit`, then run:

```javascript
// Title
const titleInput = document.querySelector('#title');
if (titleInput) {
  titleInput.value = 'NEW TITLE HERE';
  titleInput.dispatchEvent(new Event('input', {bubbles:true}));
}

// ACF location field
const locationInput = document.querySelector('input[name="acf[field_XXXXXXXX]"]');
if (locationInput) {
  locationInput.value = 'City, FL';
  locationInput.dispatchEvent(new Event('change', {bubbles:true}));
}

// ACF keyword field
const keywordInput = document.querySelector('input[name="acf[field_XXXXXXXX]"]');
if (keywordInput) {
  keywordInput.value = 'Service Name';
  keywordInput.dispatchEvent(new Event('change', {bubbles:true}));
}

// Yoast focus keyphrase
const kpInput = document.querySelector('input[name="yoast_wpseo_focuskw"]');
if (kpInput) {
  kpInput.value = 'Service Name City FL';
  kpInput.dispatchEvent(new Event('input', {bubbles:true}));
  kpInput.dispatchEvent(new Event('change', {bubbles:true}));
}

// Slug
const slugInput = document.querySelector('#new-post-slug');
if (slugInput) {
  slugInput.value = 'service-name-city-fl';
  slugInput.dispatchEvent(new Event('input', {bubbles:true}));
}
```

### 5c. Publish or save as draft

**Publish:**
```javascript
document.querySelector('#publish').click();
```

**Save as draft:**
```javascript
document.querySelector('#save-post').click();
```

### 5d. Handle connection errors

WordPress auto-saves can trigger "Connection lost" banners that prevent saving.
If this happens: wait for the banner to disappear, re-apply all field values, then
click Publish/Save again. Check connection status with:
```javascript
document.querySelector('.wp-connection-lost') ? 'lost' : 'ok';
```

---

## Step 6: Verify Each Page

After publish, confirm the page saved correctly:

```javascript
JSON.stringify({
  status: document.querySelector('#post-status-display')?.textContent?.trim(),
  publishBtn: document.querySelector('#publish')?.value,  // "Update" = published
  title: document.querySelector('#title')?.value,
  location: document.querySelector('input[name="acf[field_XXXXXXXX]"]')?.value,
  keyword: document.querySelector('input[name="acf[field_XXXXXXXX]"]')?.value,
  kp: document.querySelector('input[name="yoast_wpseo_focuskw"]')?.value
});
```

URL indicators: `message=1` or `message=6` in the URL = published. `message=10` = draft saved.

---

## Step 7: Get Live URLs

After all pages are created, verify URLs via the REST API:

```javascript
const postIds = [/* array of new post IDs */];
Promise.all(postIds.map(id =>
  fetch(`/wp-json/wp/v2/local/${id}?_fields=id,title,slug,status,link`, {credentials:'include'})
    .then(r => r.json())
    .then(d => ({ id: d.id, title: d.title?.rendered, status: d.status, link: d.link }))
)).then(results => { window._newPages = results; });

// Then read:
window._newPages?.map(p => `${p.title} | ${p.status} | ${p.link || 'draft'}`).join('\n');
```

Note: Draft posts return empty from the public REST API — that's expected.

---

## Workflow Summary

Present a final summary table to the user:

| Page | Status | Keyphrase | Location |
|------|--------|-----------|----------|
| Page Title | ✅ Published / 📝 Draft | keyphrase | City, FL |

Then list the live URLs clearly.

---

## Tips & Gotchas

- **Duplicate This** plugin nonce links are session-specific — always navigate to them directly
  via `window.location.href = dupLink.href` rather than `fetch()` or `click()`.
- If extra duplicates are accidentally created, trash them via the draft list before proceeding.
- ACF field keys are **unique per site** — always discover them fresh on each new site.
- The slug field ID is `#new-post-slug` (not `#post_name`) — WordPress uses a live-edit slug
  field in the permalink bar on the classic editor.
- Yoast keyphrase format convention: `"Service Name City State"` (e.g., "Roof Repair Jacksonville FL").
- For the "leave 1 as draft" pattern, always make the **last** page in the batch the draft.
- Always use `dispatchEvent(new Event('change', {bubbles:true}))` on ACF inputs — otherwise
  WordPress may not register the change before save.
