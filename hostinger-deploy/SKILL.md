---
name: hostinger-deploy
description: Use when deploying a web app (frontend-only or full-stack) to Hostinger shared hosting with a fonbuild.com subdomain, or when deploying updates to an existing Hostinger project.
---

# Hostinger Deploy

Deploy React (Vite) apps — with or without a Node.js backend — to Hostinger shared hosting under `*.fonbuild.com` subdomains.

## Safety Rules

**Do not overwrite existing projects.** When connecting a domain in hPanel:
1. Use an **empty/unused website slot** (temp `*.hostingersite.com` URL, no custom domain), OR
2. **Create a new website** via hPanel → Websites → Add website

Never connect a subdomain to a site that already has an active project. Check the Websites list first.

**Ask about backend needs before deploying.** If the project doesn't have a `server/` directory yet:
> "Does this app need a backend? (e.g., form submissions, database, API, email notifications)"
- **No backend**: use `--frontend-only` flag, skip PM2 setup
- **Backend needed**: design the backend first (use brainstorming skill), then deploy full stack

---

## Project Setup (once per project)

### 1. Copy deploy scripts

Scripts live in `~/Documents/Github/Thrive Votes/scripts/`. Copy to the new project:

```bash
mkdir -p scripts
cp ~/Documents/Github/Thrive\ Votes/scripts/{deploy.sh,new-subdomain.sh,setup-ssh.sh} scripts/
cp ~/Documents/Github/Thrive\ Votes/deploy.config.example.sh .
chmod +x scripts/*.sh
```

### 2. Create `deploy.config.sh`

Copy the example and fill in values:

```bash
cp deploy.config.example.sh deploy.config.sh
```

| Key | Value | Notes |
|-----|-------|-------|
| `SSH_HOST` | `46.202.95.55` | Hostinger server IP |
| `SSH_PORT` | `65002` | Always 65002 on Hostinger |
| `SSH_USER` | `u904210699` | Hostinger username |
| `DOMAIN` | `myapp.fonbuild.com` | The subdomain for this project |
| `PM2_APP_NAME` | `myapp-api` | Only needed if backend exists |
| `PM2_BIN` | `/home/$SSH_USER/.npm-global/bin/pm2` | PM2 binary location |
| `NODE_BIN` | `/opt/alt/alt-nodejs20/root/usr/bin` | Hostinger Node.js path |
| `CF_API_TOKEN` | *(from memory)* | See Cloudflare credentials in memory |
| `CF_ZONE_ID` | *(from memory)* | See Cloudflare credentials in memory |
| `CF_ROOT_DOMAIN` | `fonbuild.com` | Root domain |
| `CF_HOSTINGER_TARGET` | *(from hPanel)* | The `*.hostingersite.com` temp URL of the **target** Hostinger site |

**Finding `CF_HOSTINGER_TARGET`:** In hPanel → Websites, find the empty site you're connecting to. Its temp URL (e.g., `salmon-wolverine-437450.hostingersite.com`) is the target. Each Hostinger site has a unique one.

**Cloudflare credentials** are stored in memory (`reference_cloudflare_fonbuild.md`). Auto-fill `CF_API_TOKEN`, `CF_ZONE_ID`, `CF_ROOT_DOMAIN` from there.

Add to `.gitignore`: `deploy.config.sh`

### 3. Create subdomain DNS record

**CRITICAL: Use an A record pointing to the raw server IP — NOT a CNAME to `*.hostingersite.com`.**

A CNAME to the Hostinger temp URL routes through Hostinger's CDN layer, which doesn't recognize proxied external domains. This causes the parked/placeholder page to show indefinitely.

```bash
source deploy.config.sh

# Create A record (proxied) pointing to the server IP
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CF_API_TOKEN" -H "Content-Type: application/json" \
  --data "{\"type\":\"A\",\"name\":\"myapp\",\"content\":\"$SSH_HOST\",\"ttl\":1,\"proxied\":true}"
```

Then in hPanel: Domains → Connect domain → enter `myapp.fonbuild.com` → Next.

### 4. SSL via Cloudflare proxy

**Cloudflare SSL must be set to Flexible** for Hostinger origins without their own SSL cert. Verify at: Cloudflare dashboard → fonbuild.com → SSL/TLS → set to Flexible. This only needs to be done once for the zone.

### 5. SSH setup (once per machine)

1. Set Hostinger SSH password: hPanel → Advanced → SSH Access → Change Password
2. Run `./scripts/setup-ssh.sh` — uses `sshpass` if available for non-interactive setup

---

## Deploying

### Subsequent deploys (most common)

```bash
./scripts/deploy.sh                  # Full (frontend + backend)
./scripts/deploy.sh --frontend-only  # Frontend only
./scripts/deploy.sh --backend-only   # Backend only
```

What it does:
- Frontend: `npm run build` → rsync `dist/` to `public_html/` (excludes `.htaccess`)
- Backend: rsync `server/` to `nodejs/` (excludes `.env`, `node_modules/`, `data/`) → `npm install --production` → PM2 restart

### First deploy

The deploy script's PM2 `restart` will fail if the app doesn't exist yet. For first deploy:

1. Deploy frontend: `./scripts/deploy.sh --frontend-only`
2. Upload `.htaccess` manually (if project has `public/.htaccess`):
   ```bash
   source deploy.config.sh
   scp -P $SSH_PORT -i ~/.ssh/hostinger_$SSH_USER public/.htaccess $SSH_USER@$SSH_HOST:$REMOTE_PUBLIC_HTML/.htaccess
   ```
3. Upload backend files manually:
   ```bash
   rsync -az --exclude='.env' --exclude='node_modules/' --exclude='data/' \
     -e "ssh -p $SSH_PORT -i ~/.ssh/hostinger_$SSH_USER" \
     server/ $SSH_USER@$SSH_HOST:$REMOTE_NODEJS/
   ```
4. Install deps and start PM2:
   ```bash
   ssh -p $SSH_PORT -i ~/.ssh/hostinger_$SSH_USER $SSH_USER@$SSH_HOST \
     "cd $REMOTE_NODEJS && PATH=$NODE_BIN:\$PATH npm install --production && \
      PATH=$NODE_BIN:\$PATH HOME=/home/$SSH_USER $PM2_BIN start index.js \
        --name $PM2_APP_NAME \
        --cwd $REMOTE_NODEJS \
        --interpreter $NODE_BIN/node && \
      PATH=$NODE_BIN:\$PATH HOME=/home/$SSH_USER $PM2_BIN save"
   ```
   **`--cwd` is required** so `dotenv.config()` finds `.env`. Without it, PM2 uses its daemon's cwd and env vars won't load.
   **`--interpreter` is required** because Hostinger doesn't have `node` in the default PATH.
5. Create `.env` on server (via SSH or hPanel File Manager):
   ```bash
   ssh -p $SSH_PORT -i ~/.ssh/hostinger_$SSH_USER $SSH_USER@$SSH_HOST \
     "cat > $REMOTE_NODEJS/.env << 'EOF'
   PORT=3001
   NODE_ENV=production
   # Add app-specific env vars here
   EOF"
   ```

After first deploy, `./scripts/deploy.sh` works for all subsequent deploys.

---

## .htaccess for SPA + API Proxy

Projects with a backend need this in `public/.htaccess` (Vite copies `public/` to `dist/`):

```apache
RewriteEngine On
RewriteRule ^api/(.*)$ http://127.0.0.1:3001/api/$1 [P,L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^ index.html [L]
```

Frontend-only projects just need the SPA fallback (no API proxy line).

---

## Hostinger Environment

| Detail | Value |
|--------|-------|
| Node.js path | `/opt/alt/alt-nodejs20/root/usr/bin` |
| PM2 binary | `/home/$SSH_USER/.npm-global/bin/pm2` |
| SSH port | `65002` |
| Frontend location | `/home/$SSH_USER/domains/$DOMAIN/public_html` |
| Backend location | `/home/$SSH_USER/domains/$DOMAIN/nodejs` |
| PM2 logs | `pm2 logs <app-name>` (via SSH with correct PATH) |

**npm/node commands on Hostinger require PATH prefix:**
```bash
PATH=/opt/alt/alt-nodejs20/root/usr/bin:$PATH npm install
```

---

## Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| **Parked page persists for hours** | DNS CNAME points to `*.hostingersite.com` which routes through Hostinger CDN — CDN doesn't know proxied external domains | Replace CNAME with **A record → server IP** (e.g., `46.202.95.55`), proxied. This is the #1 gotcha. |
| 503 on `/api/*` routes | PM2 not running or on wrong port | Check `pm2 list`. Ensure PM2 was started with `--cwd` so `.env` loads correctly. |
| PM2 daemon dies, app on wrong port | PM2 started without `--cwd`, so `dotenv.config()` can't find `.env`, PORT defaults wrong | Restart with `--cwd $REMOTE_NODEJS --interpreter $NODE_BIN/node` |
| 525 SSL Handshake error | Cloudflare SSL mode not set to Flexible | Set SSL to Flexible in Cloudflare dashboard (one-time per zone) |
| `npm: command not found` on server | Node not in PATH | Prefix with `PATH=/opt/alt/alt-nodejs20/root/usr/bin:$PATH` |
| PM2 restart fails on first deploy | App doesn't exist yet | Use `pm2 start` first, then `pm2 save` |
| `.env` not updated on server | rsync intentionally skips it | Update via SSH or hPanel File Manager |
