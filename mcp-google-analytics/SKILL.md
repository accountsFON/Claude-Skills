---
name: mcp-google-analytics
description: Use when working with Google Analytics data via the MCP server — listing GA4 properties, running reports on sessions, users, pageviews, conversions, traffic sources, or any other GA4 metrics. Invoke this skill whenever the user mentions Google Analytics, GA4, website traffic, sessions, conversions, bounce rate, or wants analytics data for any client website.
---

# Google Analytics MCP Skill

Query Google Analytics 4 data directly through Claude using the `google-analytics-mcp-server`.

## Setup Status

The MCP server is installed and registered:
- **Repo:** `/Users/julio/Documents/Github/google-analytics-mcp-server`
- **Upstream:** https://github.com/gomarble-ai/google-analytics-mcp-server
- **Config:** `~/.claude/mcp.json` — entry: `google-analytics`
- **Auth account:** `julio@fiveonenine.us` (60+ GA4 properties across 5 accounts)
- **Token:** `/Users/julio/.config/gws/google_analytics_token.json`

## Using GA Tools

GA tools are available automatically once the MCP server is connected.

### List GA4 properties
```
Tool: list_ga4_properties
Args: {}
```
Returns all GA4 properties accessible to the authenticated account.

### Run a GA4 report
```
Tool: run_report
Args: {
  "property_id": "properties/123456789",
  "date_ranges": [{"start_date": "2025-01-01", "end_date": "2025-03-31"}],
  "metrics": [{"name": "sessions"}, {"name": "activeUsers"}],
  "dimensions": [{"name": "sessionDefaultChannelGroup"}]
}
```

### Common metrics
- `sessions`, `activeUsers`, `newUsers`
- `screenPageViews`, `bounceRate`, `averageSessionDuration`
- `conversions`, `eventCount`

### Common dimensions
- `sessionDefaultChannelGroup` — organic, paid, direct, etc.
- `pagePath` — individual pages
- `country`, `city`
- `deviceCategory` — desktop / mobile / tablet
- `date` — day-by-day

## Fresh Installation

If you need to reinstall this server from scratch:

### 1. Requirements
- Python 3.11+ (use `/opt/homebrew/Cellar/python@3.14/3.14.3_1/bin/python3.14` if system Python is too old)
- Google OAuth client secret JSON (project must have **Google Analytics Data API** and **Google Analytics Admin API** enabled)

### 2. Clone and install
```bash
git clone https://github.com/gomarble-ai/google-analytics-mcp-server /path/to/ga-mcp
cd /path/to/ga-mcp
python3.14 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 3. Enable the APIs
In Google Cloud Console → APIs & Services → Enable both:
- **Google Analytics Data API**
- **Google Analytics Admin API**

### 4. Create .env file
```bash
echo "GOOGLE_ANALYTICS_OAUTH_CONFIG_PATH=/path/to/client_secret.json" > .env
echo "LOG_LEVEL=INFO" >> .env
echo "TOKEN_REFRESH_BUFFER=300" >> .env
```

### 5. Register in mcp.json
Add to `~/.claude/mcp.json`:
```json
"google-analytics": {
  "command": "/path/to/ga-mcp/.venv/bin/python",
  "args": ["/path/to/ga-mcp/server.py"],
  "env": {
    "GOOGLE_ANALYTICS_OAUTH_CONFIG_PATH": "/path/to/client_secret.json",
    "LOG_LEVEL": "INFO",
    "TOKEN_REFRESH_BUFFER": "300"
  }
}
```

### 6. Authenticate
The server stores its token at `~/.config/gws/google_analytics_token.json` (derived from the `GOOGLE_ANALYTICS_OAUTH_CONFIG_PATH` directory). On first run it opens a browser for OAuth. To pre-populate without a browser:

1. Obtain an OAuth token via `requests_oauthlib` (no PKCE) with scopes:
   - `https://www.googleapis.com/auth/analytics.readonly`
   - `https://www.googleapis.com/auth/analytics`
2. Run `creds.to_json()` to get the token JSON string
3. Write that string to `~/.config/gws/google_analytics_token.json`

The server will use it silently and auto-refresh when expired.

## Notes

- The `julio@fiveonenine.us` account has access to all client GA4 properties
- `TOKEN_REFRESH_BUFFER=300` refreshes the token 5 minutes before expiry
- The token file location is derived from the directory of `GOOGLE_ANALYTICS_OAUTH_CONFIG_PATH`
- The `accounts@fonmarketing.com` account has no real client data — always use `fiveonenine.us`
