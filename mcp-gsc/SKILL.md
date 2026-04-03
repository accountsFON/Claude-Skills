---
name: mcp-gsc
description: Use when working with Google Search Console data via the MCP server — listing GSC properties, fetching search analytics (clicks, impressions, CTR, position), running performance reports, or doing any SEO analysis against GSC data. Invoke this skill whenever the user mentions GSC, Search Console, search performance, clicks, impressions, rankings, or queries for a website.
---

# Google Search Console MCP Skill

Query Google Search Console data directly through Claude using the `mcp-gsc` server.

## Setup Status

The MCP server is installed and registered:
- **Repo:** `/Users/julio/Documents/Github/mcp-gsc`
- **Upstream:** https://github.com/AminForou/mcp-gsc
- **Config:** `~/.claude/mcp.json` — entry: `gsc`
- **Auth account:** `julio@fiveonenine.us` (54 GSC properties)
- **Token:** `/Users/julio/Documents/Github/mcp-gsc/token.json`

## Using GSC Tools

GSC tools are available automatically once the MCP server is connected. Common workflow:

### List available properties
```
Tool: list_gsc_properties
Args: {}
```
Returns all verified GSC properties for the authenticated account.

### Fetch search analytics
```
Tool: get_search_analytics
Args: {
  "site_url": "https://example.com/",
  "start_date": "2025-01-01",
  "end_date": "2025-03-31",
  "dimensions": ["query", "page"],
  "row_limit": 100
}
```

### Key dimensions
- `query` — search terms
- `page` — individual URLs
- `country` — geographic breakdown
- `device` — desktop / mobile / tablet
- `date` — day-by-day trend

### Key metrics returned
- `clicks`, `impressions`, `ctr`, `position`

## Fresh Installation

If you need to reinstall this server from scratch:

### 1. Requirements
- Python 3.11+ (use `/opt/homebrew/Cellar/python@3.14/3.14.3_1/bin/python3.14` if system Python is too old)
- Google OAuth client secret JSON (project must have **Google Search Console API** enabled)

### 2. Clone and install
```bash
git clone https://github.com/AminForou/mcp-gsc /path/to/mcp-gsc
cd /path/to/mcp-gsc
python3.14 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 3. Enable the API
In Google Cloud Console → APIs & Services → Enable **Google Search Console API** for your project.

### 4. Register in mcp.json
Add to `~/.claude/mcp.json`:
```json
"gsc": {
  "command": "/path/to/mcp-gsc/.venv/bin/python",
  "args": ["/path/to/mcp-gsc/gsc_server.py"],
  "env": {
    "GSC_OAUTH_CLIENT_SECRETS_FILE": "/path/to/client_secret.json",
    "GSC_DATA_STATE": "all"
  }
}
```

### 5. Authenticate
The server stores its token at `<repo>/token.json`. On first run it opens a browser for OAuth. To pre-populate without a browser:

1. Obtain an OAuth token via `requests_oauthlib` (no PKCE) with scopes `https://www.googleapis.com/auth/webmasters.readonly`
2. Run `creds.to_json()` to get the token JSON string
3. Write that string to `<repo>/token.json`

The server will use it silently on subsequent runs and auto-refresh when expired.

## Notes

- `GSC_DATA_STATE=all` includes both fresh and final data (avoids 3-day data lag)
- The `julio@fiveonenine.us` account has access to all client GSC properties
- Token auto-refreshes using the `refresh_token` field — no re-auth needed
