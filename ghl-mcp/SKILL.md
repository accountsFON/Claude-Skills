---
name: ghl-mcp
description: Use when working with GoHighLevel (GHL) via the MCP server — connecting to the agency, listing sub-accounts, switching between client locations, and using any GHL capability (contacts, conversations, opportunities, calendar, invoices, payments, social media, workflows, etc.)
---

# GoHighLevel MCP Skill

Connect to the GoHighLevel agency, dynamically switch between client sub-accounts, and use the full GHL toolset.

## Setup (one-time)

The MCP server is already installed and registered in Claude Desktop:
- **Location:** `/Users/julio/Documents/Github/GoHighLevel-MCP`
- **Config:** `~/Library/Application Support/Claude/claude_desktop_config.json` — entry: `ghl-mcp-server`
- **API Key:** Agency private integration token (already configured in env)
- **No fixed location ID** — switch accounts dynamically using the tools below

## Agency Workflow

### Step 1 — Discover accounts
Always start by listing locations when the user doesn't specify an account, or when switching clients:

```
Tool: list_ghl_locations
Args: { "query": "optional name filter", "limit": 100 }
```

Returns: array of `{ id, name, city, state }` — present a clean list to the user.

### Step 2 — Switch to the target account
```
Tool: set_active_location
Args: { "locationId": "<id from step 1>", "locationName": "<human name>" }
```

All subsequent tool calls are now scoped to that location. Confirm to the user: *"Switched to [Name] — ready to work with their account."*

### Step 3 — Use any GHL capability

With a location active, use any of the 253 available tools:

| Category | Key Tools |
|---|---|
| **Contacts** | `search_contacts`, `create_contact`, `update_contact`, `upsert_contact`, `add_contact_tag` |
| **Conversations** | `search_conversations`, `send_sms`, `send_email`, `get_messages` |
| **Opportunities** | `search_opportunities`, `get_pipelines`, `create_opportunity`, `update_opportunity_status` |
| **Calendar** | `get_calendars`, `get_free_slots`, `create_appointment`, `get_calendar_events` |
| **Invoices** | `create_invoice`, `send_invoice`, `list_invoices`, `create_estimate` |
| **Payments** | `list_orders`, `list_transactions`, `list_subscriptions` |
| **Social Media** | `create_social_post`, `search_social_posts`, `get_social_accounts` |
| **Email Marketing** | `get_email_campaigns`, `create_email_template` |
| **Workflows** | `get_workflows`, `add_contact_to_workflow` |
| **Location** | `get_location`, `update_location`, `get_location_custom_fields` |
| **Blog** | `create_blog_post`, `get_blog_posts`, `get_blog_sites` |
| **Media** | `upload_media_file`, `get_media_files` |

### Step 4 — Switch accounts mid-conversation
When the user says "now do the same for [another client]", go back to Step 1 or directly call `set_active_location` if you already know the location ID.

## Rules

- **Always confirm the active location** before performing write operations (create, update, delete). Ask: *"This will affect [Location Name] — confirm?"*
- **Use `list_ghl_locations` with a query** to quickly find a specific client by name rather than scrolling through all accounts.
- **Location IDs are stable** — you can remember them within a conversation but don't assume them across sessions.
- **Contacts need a locationId** — it's injected automatically from the active location, so no need to pass it manually.

## Example Interactions

**"Show me all my GHL accounts"**
→ Call `list_ghl_locations`, display name + city/state in a clean list.

**"Pull up the pipeline for All Pro Roofing"**
→ `list_ghl_locations` with query "All Pro", set active, then `search_opportunities` or `get_pipelines`.

**"Add a contact to Akkoo Coffee's account"**
→ Set active location to Akkoo Coffee, then `create_contact` or `upsert_contact`.

**"Send a follow-up SMS to all contacts tagged 'lead' in ACE Handyman"**
→ Set active location, `search_contacts` with tag filter, then `send_sms` for each.

## Troubleshooting

| Issue | Fix |
|---|---|
| Server not found in Claude Desktop | Restart Claude Desktop after config changes |
| `list_ghl_locations` returns empty | Check API key is a Private Integration Token (not a regular key) |
| Tool fails with 401 | API key expired — regenerate in GHL → Settings → Integrations → Private Integrations |
| Wrong location active | Call `set_active_location` again with the correct ID |
