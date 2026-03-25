---
name: webflow-local-seo
description: >
  Workflow for auditing and creating Webflow CMS Local Landing Pages (service × location
  or product × location pairings) for local SEO across multiple client sites managed via
  the Webflow MCP tool. Use this skill whenever the user mentions Webflow local landing
  pages, finding missing combos in Webflow CMS, creating local SEO pages in Webflow,
  or says "let's work on [client name]'s local landing" in a Webflow context. Also trigger
  when the user wants to fill CMS gaps, add service/location combos, or publish local
  landing drafts on a Webflow site. Covers: finding the site, auditing all 3 collections
  (Local Landings + Services/Products + Locations), pagination, ID-based gap analysis,
  creating draft items, publishing, and returning live URLs.
---

# Webflow Local SEO — Local Landing Pages Workflow

This skill drives the full lifecycle of Webflow CMS Local Landing pages: audit existing
coverage, find missing service×location (or product×location) combos, create draft items,
publish, and return live URLs.

## MCP Tool Reference

All Webflow operations go through:
- **`mcp__053daac2-5359-413e-a95d-51bdba05ef4f__data_sites_tool`** — list/find sites
- **`mcp__053daac2-5359-413e-a95d-51bdba05ef4f__data_cms_tool`** — collections, items, publishing

---

## Step 1 — Find the Site

Ask the user which client site to work on (or read from context). Then list all sites to get the `site_id`:

```json
[{"list_sites": {}}]
```

Match by display name (case-insensitive). Cache the `site_id` — you'll need it for publishing.

---

## Step 2 — Identify the 3 Key Collections

Every Webflow Local SEO site has three collections:
1. **Local Landings** — the junction collection (one item per combo)
2. **Services** or **Products** — the "what" dimension
3. **Locations** — the "where" dimension

List all collections for the site:

```json
[{"list_collections": {"site_id": "<site_id>"}}]
```

Look for names like: *Local Landings*, *Local Landing*, *Services*, *Products*, *Locations*, *Location Settings*. If unsure, get collection details to inspect field names.

---

## Step 3 — Fetch ALL Items (paginate!)

Collections often have 100+ items. Always paginate — one page is rarely enough.

Fetch page 1 (offset 0), then check `total` vs items returned. Keep fetching at offset 100, 200, etc. until you have everything.

```json
[{"list_collection_items": {"collection_id": "<id>", "request": {"limit": 100, "offset": 0}}}]
[{"list_collection_items": {"collection_id": "<id>", "request": {"limit": 100, "offset": 100}}}]
```

Fetch Services/Products, Locations, and Local Landings this way. Build three maps:
- `svc_map`: `{id → name}` for all services or products
- `loc_map`: `{id → name}` for all locations
- `existing`: set of `(loc_id, svc_id)` tuples from Local Landings

---

## Step 4 — Gap Analysis (Python, ID-based)

**Always use reference IDs — never names** — for the gap analysis. Names can be misleading (e.g., "Fences in Nocatee" ≠ service name "Fencing Installation"). IDs are authoritative.

Use the helper script at `scripts/gap_analysis.py`, or run inline:

```python
import json, sys

# Inputs: svc_map {id:name}, loc_map {id:name}, landing_items [list of fieldData dicts]
# Field names differ per site — check actual collection schema:
#   service field:  "service" OR "product-reference"
#   location field: "location" OR "location-setting"

existing = set()
for item in landing_items:
    fd = item['fieldData']
    loc_id = fd.get('location') or fd.get('location-setting') or ''
    svc_id = fd.get('service') or fd.get('product-reference') or ''
    if loc_id and svc_id:
        existing.add((loc_id, svc_id))

missing = []
for loc_id, loc_name in loc_map.items():
    for svc_id, svc_name in svc_map.items():
        if (loc_id, svc_id) not in existing:
            missing.append((loc_name, svc_name, loc_id, svc_id))

print(f"Total existing: {len(existing)}")
print(f"Total missing: {len(missing)}")
for m in missing:
    print(f"  {m[1]} in {m[0]}")
```

Present the full missing list to the user and ask how many to create (default: 3–10).

---

## Step 5 — Create Draft CMS Items

For each combo to create, build the item payload using the **actual field slugs** from the collection schema:

| Field purpose | Common field slugs |
|---|---|
| Item name | `name` (required) |
| URL slug | `slug` (required) |
| Target keyword | `target-keyword`, `key-word`, or `keywords` |
| Service/Product ref | `service`, `product-reference` |
| Location ref | `location`, `location-setting` |

**Field values:**
- `name`: `"Service Name in Location Name"` (e.g., `"Deck Maintenance in Orange Park, FL"`)
- `slug`: `"service-name-in-location-name"` (lowercase, hyphens, e.g., `"deck-maintenance-in-orange-park-fl"`)
- `target-keyword`: **service/product name only** — NOT "Service in Location" — just the service name (e.g., `"Deck Maintenance"`)
- `service` / `product-reference`: the service/product reference ID
- `location` / `location-setting`: the location reference ID

Create all items in a single batched call when possible:

```json
[{"create_collection_items": {
  "collection_id": "<local_landings_collection_id>",
  "request": {
    "isDraft": true,
    "fieldData": [
      {
        "name": "Deck Maintenance in Orange Park, FL",
        "slug": "deck-maintenance-in-orange-park-fl",
        "target-keyword": "Deck Maintenance",
        "service": "<service_ref_id>",
        "location": "<location_ref_id>"
      }
    ]
  }
}}]
```

> **Note on target-keyword**: This is the most common mistake. The keyword field should contain only the service/product name — not "Service in Location, FL". The location is already captured by the location reference field.

---

## Step 6 — Publish

Publish in two stages:

**Stage 1: Publish the CMS items**

```json
[{"publish_collection_items": {
  "collection_id": "<local_landings_collection_id>",
  "request": {"itemIds": ["<id1>", "<id2>", ...]}
}}]
```

**Stage 2: Publish the site**

```json
[{"publish_site": {
  "site_id": "<site_id>",
  "request": {"customDomains": [], "publishToWebflowSubdomain": false}
}}]
```

> **Rate limiting (429)**: The `publish_site` endpoint is aggressively rate-limited. If you get a 429, wait ~10 seconds and retry once. If it persists, inform the user and provide the URLs anyway — the CMS items are published and will go live once the user manually publishes from the Webflow Designer. Don't spin in a loop retrying.

> **409 Conflict ("site not published")**: Some sites need to be published to their custom domain first from Webflow Designer. Inform the user if this happens.

---

## Step 7 — Return Live URLs

Construct URLs using the site's primary domain + the local landings collection slug.

The typical pattern is:
```
https://www.clientdomain.com/<local-landings-collection-slug>/<item-slug>
```

To find the collection's URL prefix, either:
- Check an existing published landing page URL for the pattern
- Use `get_collection_details` — the `slug` field is the URL prefix

Return a clean numbered list:
```
1. Deck Maintenance in Orange Park → https://www.clientdomain.com/local/deck-maintenance-in-orange-park-fl
2. ...
```

---

## Common Patterns & Gotchas

| Situation | What to do |
|---|---|
| Site has 100+ landing items | Always paginate — fetch offset 0, 100, 200... until `total` is covered |
| Can't find a service in existing items | User may have recently added it — fetch fresh data |
| Slug collision | Append location abbreviation or state code to slug |
| Wrong field names | Fetch collection schema first (`get_collection_details`) and match exact slugs |
| `product-reference` instead of `service` | Alliant-style sites use products × locations rather than services × locations |
| Combos appear "missing" but exist | Always use IDs, never match by name — names can be misleading |
| Can't publish site | Publish CMS items only and inform user to manually publish from Designer |

---

## Quick Reference: Field Name Variants by Site Type

| Site type | Service/Product field | Location field | Keyword field |
|---|---|---|---|
| Service-based (HVAC, Fencing, etc.) | `service` | `location` | `target-keyword` |
| Product-based (Supply, Retail, etc.) | `product-reference` | `location-setting` | `target-keyword` |

Always verify with `get_collection_details` before creating items.
