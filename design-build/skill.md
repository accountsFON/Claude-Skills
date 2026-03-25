---
name: design-build
description: Use when starting a new web app project from a design or idea — covers Google Stitch mockup creation, React scaffolding, and converting designs into working Vite + Tailwind code. Use before hostinger-deploy.
---

# Design → Build

Turn an idea or Google Stitch mockup into a working React + Vite + Tailwind app, ready for deployment.

## When to Use

- User says "build me an app", "new project", "start from this design"
- User has a Google Stitch export to convert
- User wants to scaffold a new React app from scratch
- **After this skill:** use `hostinger-deploy` to ship it

## Phase 1 — Design in Google Stitch

1. Go to stitch.withgoogle.com — describe the app
2. Iterate until layout and components look right
3. Export as **HTML/CSS** — treat it as a detailed mockup, not production code

**Skip this phase** if the user already has a design, HTML mockup, or wants to build directly from a description.

## Phase 2 — Scaffold React + Vite + Tailwind

```bash
npm create vite@latest my-app -- --template react-ts
cd my-app && npm install
```

Tailwind v4 (current default with Vite plugin):
```bash
npm install -D @tailwindcss/vite
```

Add to `vite.config.ts`:
```ts
import tailwindcss from '@tailwindcss/vite';
// add tailwindcss() to plugins array
```

Add to `src/index.css`:
```css
@import "tailwindcss";
```

**For Tailwind v3 projects** (if user prefers or project requires):
```bash
npm install -D tailwindcss postcss autoprefixer && npx tailwindcss init -p
```
Add to `tailwind.config.js` content: `["./index.html", "./src/**/*.{js,jsx,ts,tsx}"]`
Add to `src/index.css`: `@tailwind base; @tailwind components; @tailwind utilities;`

## Phase 3 — Convert Design to React Components

For each section of the Stitch export or HTML mockup:

1. Create `src/ComponentName.tsx` (or `.jsx`)
2. Paste HTML into the `return ()` block
3. Fix for JSX:
   - `class=` → `className=`
   - Self-close void tags (`<img />`, `<input />`, `<br />`)
   - Inline styles → objects (`style={{ color: 'red' }}`)
   - `for=` → `htmlFor=`
4. Replace inline CSS with Tailwind classes
5. Extract repeated patterns into shared components

**Conversion prompt for Claude:**
> "Convert this HTML to a React TSX component using Tailwind CSS classes. Keep the same visual structure."
> [paste HTML block]

## Phase 4 — Backend (if needed)

**Ask early:**
> "Does this app need a backend? (e.g., form submissions, database, API, email notifications)"

If yes, use the **brainstorming skill** to design the backend before building it. Common patterns:

- **Express + SQLite** — simple data storage, lead capture, form submissions
- **Express + MySQL** — relational data, user accounts, complex queries
- **API-only** — proxy to third-party services

Backend structure:
```
server/
├── index.js          # Express setup, CORS, JSON parsing, routes
├── db.js             # Database connection and init
├── routes/           # One file per resource
├── .env              # Credentials (never commit)
└── .env.example      # Template for env vars
```

Local dev:
```bash
npm run dev                    # Frontend — Vite dev server
cd server && node index.js     # Backend — Express on port 3001
```

Add dev proxy to `vite.config.ts` so frontend `/api/*` calls reach the backend:
```ts
server: {
  proxy: { '/api': 'http://localhost:3001' }
}
```

## Checklist Before Deploying

- [ ] App builds cleanly: `npm run build`
- [ ] All pages/routes work in dev
- [ ] If backend: server starts, endpoints respond
- [ ] `.gitignore` includes: `node_modules/`, `dist/`, `.env*`, `!.env.example`, `server/data/`, `server/.env`, `server/node_modules/`
- [ ] `deploy.config.sh` (if deploying to Hostinger)

**Next step:** Use `hostinger-deploy` skill to ship it.
