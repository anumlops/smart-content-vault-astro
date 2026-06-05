# Deployment Guide

## Deploying to Vercel + Neon

### 1. Set Up Neon Database

1. Create an account at [neon.tech](https://neon.tech)
2. Create a new project
3. Copy the connection string (Pooled connection recommended)

### 2. Prepare for Deployment

```bash
npm run build
```

### 3. Deploy to Vercel

Via Vercel CLI:

```bash
npm i -g vercel
vercel login
vercel
```

Or connect your GitHub repository to Vercel:

1. Push to GitHub
2. Import repository in Vercel
3. Set framework to AstroJS
4. Add environment variables:
   - `DATABASE_URL` — Your Neon connection string
   - `AUTH_SECRET` — Generate: `openssl rand -hex 32`
   - `PUBLIC_APP_URL` — Your Vercel deployment URL
5. Deploy

### 4. Post-Deployment

Run migrations from your local machine:

```bash
DATABASE_URL="<neon-connection-string>" npx prisma db push
```

Or use Vercel Post-Deploy hooks.

## Project Configuration

The Astro project is configured for server-side rendering with the Vercel adapter:

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import vercel from '@astrojs/vercel';

export default defineConfig({
  output: 'server',
  adapter: vercel(),
  vite: { plugins: [tailwindcss()] },
});
```
