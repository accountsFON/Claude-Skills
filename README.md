# Claude Skills

A collection of reusable skills for Claude Code. Each skill teaches Claude a repeatable workflow or technique — drop a folder into `~/.claude/skills/` and Claude picks it up automatically.

## What Are Skills?

Skills are reference guides that Claude loads when a task matches their description. They encode proven workflows so you don't have to re-explain your process in every conversation.

## Installation

1. Copy the skill folder into your Claude skills directory:
   ```bash
   cp -r hostinger-deploy ~/.claude/skills/
   ```

2. Register the skill in `~/.claude/CLAUDE.md` under `## Custom Skills`:
   ```
   - hostinger-deploy: Full workflow from Google Stitch design to deploying a React + Node.js app on Hostinger with a custom subdomain. Use when starting a new project or deploying updates.
   ```

3. That's it — Claude will load the skill automatically when relevant.

---

## Available Skills

### `hostinger-deploy`
**Full workflow: Google Stitch → React app → live on Hostinger**

Covers the entire process of going from a design in Google Stitch to a deployed React + Node.js web app on Hostinger shared hosting with a custom subdomain managed through Cloudflare DNS.

**What it includes:**
- Converting Google Stitch HTML/CSS exports into React + Tailwind components
- Setting up a Node.js + Express + MariaDB backend
- Automating Cloudflare DNS subdomain creation via API
- One-command deploys via SSH (build → upload → restart PM2)
- Troubleshooting common Hostinger shared hosting issues (PHP proxy, PM2 restarts, SSL provisioning)

**Scripts included** (in your project's `scripts/` folder):
| Script | Purpose |
|--------|---------|
| `setup-ssh.sh` | One-time SSH key setup for passwordless deploys |
| `new-subdomain.sh` | Creates Cloudflare CNAME + prints Hostinger domain connect steps |
| `deploy.sh` | Full deploy: build → upload frontend + backend → restart PM2 |

**Best for:** Developers deploying Node.js apps on Hostinger shared hosting with Cloudflare-managed DNS.

---

## Contributing

Each skill lives in its own folder with a `SKILL.md` file:
```
skill-name/
  SKILL.md       # Required — the skill content
  supporting.*   # Optional — scripts, templates, reference docs
```

Skills follow the [Claude Code skill format](https://docs.anthropic.com/claude/docs) with YAML frontmatter:
```yaml
---
name: skill-name
description: Use when [specific triggering conditions]
---
```
