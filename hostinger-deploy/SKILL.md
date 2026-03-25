---
name: hostinger-deploy
description: Use when starting a new web app project from a Google Stitch design through to deploying on Hostinger shared hosting with a custom subdomain, or when deploying updates to an existing Hostinger project using the deploy scripts.
---

# Hostinger Deploy Workflow

## Overview
Full workflow: Google Stitch design → React + Node.js app → live on Hostinger shared hosting with a custom subdomain. Three scripts handle the repeatable parts: `setup-ssh.sh` (once per machine), `new-subdomain.sh` (once per project), `deploy.sh` (every deploy).

Scripts live in `scripts/` and config lives in `deploy.config.sh` (gitignored). Copy `deploy.config.example.sh` to get started.

---

## Phase 1 — Design in Google Stitch
1. Go to stitch.withgoogle.com — describe the app
2. Iterate until the layout and components look right
3. Export as **HTML/CSS** — treat it as a detailed mockup, not production code

---

## Phase 2 — Convert Stitch Output to React

**Scaffold:**
```bash
npm create vite@latest my-app -- --template react
cd my-app && npm install
npm install -D tailwindcss postcss autoprefixer && npx tailwindcss init -p
```
Add to `tailwind.config.js` content: `["./index.html", "./src/**/*.{js,jsx}"]`
Add to `src/index.css`: `@tailwind base; @tailwind components; @tailwind utilities;`

**Convert each Stitch section:**
1. Create `src/ComponentName.jsx`
2. Paste Stitch HTML into `return ()` block
3. Fix JSX: `class=` → `className=`, self-close void tags (`<img />`), inline styles → objects (`style={{ color: 'red' }}`)
4. Replace inline CSS with Tailwind classes

**Claude prompt for conversion:**
> "Convert this HTML to a React JSX component using Tailwind CSS classes. Keep the same visual structure."
> [paste HTML block]

---

## Phase 3 — Backend
Standard stack: Node.js + Express + MariaDB. Recommended structure:
- `server/index.js` — Express setup, middleware, route imports
- `server/db.js` — mysql2 connection pool
- `server/routes/` — one file per resource
- `server/schema.sql` — DB schema
- `server/.env` — DB credentials (never commit)

Local dev:
```bash
npm run dev                   # Frontend — Vite at localhost:5173
cd server && node index.js    # API at localhost:3001
```

Set `VITE_API_URL=http://localhost:3001` in `.env.local` for local API routing.

---

## Phase 4 — New Subdomain (once per project)

**Get Cloudflare credentials first:**
- API token: dash.cloudflare.com/profile/api-tokens → Edit zone DNS → scope to your domain
- Zone ID: Cloudflare → your domain → Overview → right sidebar

Fill `CF_API_TOKEN` + `CF_ZONE_ID` into `deploy.config.sh`, then:
```bash
./scripts/new-subdomain.sh <subdomain>
# e.g. ./scripts/new-subdomain.sh myapp → creates myapp.yourdomain.com
```

Follow the printed Hostinger hPanel steps (Domains → Connect domain → enter full subdomain → Next). Hostinger auto-installs SSL.

⏳ Wait **1–4 hours** for SSL + routing. Verify: `curl https://<subdomain>.yourdomain.com/api/health`

---

## Phase 5 — SSH Setup (once per machine)
1. Set Hostinger SSH password: hPanel → Advanced → SSH Access → Change Password
2. Run: `./scripts/setup-ssh.sh` — enter the password once, never again

**Hostinger SSH details** (find in hPanel → Advanced → SSH Access):
- Host: your server IP
- Port: `65002` (always this on Hostinger shared hosting)
- User: your hosting username (e.g. `u123456789`)

---

## Phase 6 — Deploy
```bash
./scripts/deploy.sh                  # Full deploy (frontend + backend)
./scripts/deploy.sh --frontend-only  # Skip backend + PM2 restart
./scripts/deploy.sh --backend-only   # Skip frontend build/upload
```

What it does: `npm run build` → rsync `dist/` → rsync `server/` (skips `.env`, `node_modules/`) → `npm install --production` on server → PM2 restart

---

## deploy.config.sh Reference

| Key | Description | Example |
|-----|-------------|---------|
| `SSH_HOST` | Your Hostinger server IP | `46.x.x.x` |
| `SSH_PORT` | Always 65002 on Hostinger | `65002` |
| `SSH_USER` | Hostinger account username | `u123456789` |
| `DOMAIN` | Your subdomain | `myapp.yourdomain.com` |
| `REMOTE_PUBLIC_HTML` | Path to public_html | `/home/$SSH_USER/domains/$DOMAIN/public_html` |
| `REMOTE_NODEJS` | Path to Node.js app folder | `/home/$SSH_USER/domains/$DOMAIN/nodejs` |
| `PM2_APP_NAME` | Name used in `pm2 start` | `myapp-api` |
| `PM2_BIN` | Full path to pm2 binary | `/home/$SSH_USER/.npm-global/bin/pm2` |
| `NODE_BIN` | Node.js bin directory | `/opt/alt/alt-nodejs20/root/usr/bin` |
| `CF_API_TOKEN` | Cloudflare API token (DNS:Edit) | — |
| `CF_ZONE_ID` | Cloudflare Zone ID for your domain | — |
| `CF_ROOT_DOMAIN` | Your root domain | `yourdomain.com` |
| `CF_HOSTINGER_TARGET` | Hostinger temp URL for your site | `abc123.hostingersite.com` |

Copy `deploy.config.example.sh` → `deploy.config.sh` (gitignored — never commit it)

---

## Hostinger Architecture Notes

Hostinger shared hosting can't make direct TCP connections from Apache to Node.js processes. The workaround is a **PHP reverse proxy**:

```
Browser → Apache (public_html) → nodeproxy.php → Node.js :3000 → MariaDB
```

Required files in `public_html/`:
- `.htaccess` — routes `/api/*` requests to `nodeproxy.php`
- `nodeproxy.php` — PHP cURL proxy to Node.js

These are excluded from rsync deploys (deploy.sh uses `--exclude='.htaccess' --exclude='nodeproxy.php'`) so they're never accidentally overwritten.

---

## PM2 on Hostinger

Node.js processes are managed with PM2. To start the app for the first time:
```bash
# Via SSH
PATH=/opt/alt/alt-nodejs20/root/usr/bin:/usr/local/bin:/usr/bin:/bin \
HOME=/home/<your-user> \
/home/<your-user>/.npm-global/bin/pm2 start index.js --name myapp-api
```

After SSH is set up, `deploy.sh` handles restarts automatically.

**If you don't have SSH access yet** (e.g. during initial setup), restart PM2 via a temporary PHP file:
```php
<?php
$pm2 = '/home/<your-user>/.npm-global/bin/pm2';
$dir = '/home/<your-user>/domains/<your-site>/nodejs';
putenv("PATH=/opt/alt/alt-nodejs20/root/usr/bin:/usr/local/bin:/usr/bin:/bin");
putenv("HOME=/home/<your-user>");
echo shell_exec("cd $dir && $pm2 restart myapp-api 2>&1");
```
Upload to `public_html/restart-node.php`, hit the URL, then **delete it immediately**.

---

## Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| Parked page after connecting domain | Hostinger routing still propagating | Wait 1–4 hours |
| HTTPS TLS error (exit 35) | SSL still provisioning | Wait, retry |
| PM2 not restarting via deploy.sh | SSH key not set up | Run `setup-ssh.sh` first |
| `.env` not updated on server | rsync intentionally skips it | Update manually via hPanel File Manager |
| Old JS bundles still loading | Stale files in `public_html/assets/` | Hard refresh or delete old asset files via File Manager |
| `Permission denied` on SSH | Password not set or key not copied | Set password in hPanel → re-run `setup-ssh.sh` |

---

## Setup Checklist (New Project)

- [ ] Design in Google Stitch
- [ ] Scaffold React + Vite + Tailwind
- [ ] Convert Stitch HTML → React components
- [ ] Build Express backend + MariaDB schema
- [ ] Test locally
- [ ] Copy `deploy.config.example.sh` → `deploy.config.sh` and fill in values
- [ ] Run `./scripts/setup-ssh.sh` (first time on this machine)
- [ ] Run `./scripts/new-subdomain.sh <name>` and follow Hostinger steps
- [ ] Wait for SSL (~1–4 hours), verify `/api/health`
- [ ] Run `./scripts/deploy.sh`
