# Limo

**Linked Memory. Save. Organize. Rediscover.**

A personal knowledge bookmarking platform. Save content from across the internet, organize it automatically, and rediscover it later.

## Why Limo

People consume enormous amounts of online content daily — YouTube videos, articles, documentation, GitHub repositories, Instagram posts, and more. Valuable information gets lost in browser tabs, forgotten bookmarks, and endless scroll.

Limo solves this by providing a central place to:

- **Capture** content instantly with a single link
- **Organize** automatically using smart categories and tags
- **Browse** by timeline, category, or search
- **Rediscover** saved content when you need it

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | AstroJS, TypeScript, Tailwind CSS v4 |
| Backend | Astro Server Endpoints |
| Database | Neon PostgreSQL |
| ORM | Prisma |
| Auth | Session-based (httpOnly cookies) |
| Deployment | Vercel |

## Quick Start

### Prerequisites

- Node.js 20+
- PostgreSQL (or Neon connection string)

### Setup

```bash
npm install
cp .env.example .env
# Edit .env with your DATABASE_URL
npm run prisma:generate
npm run prisma:push
npm run dev
```

Visit `http://localhost:4321`

## Project Structure

```
src/
├── components/
│   ├── auth/          # Login/Register forms
│   ├── content/       # Content cards, detail, form
│   ├── dashboard/     # Stats, categories, timeline
│   ├── layout/        # Sidebar, navbar, bottom nav, FAB
│   ├── search/        # Search bar and results
│   └── ui/            # Reusable UI primitives
├── layouts/           # Page layouts (Base, Dashboard, Auth)
├── lib/               # Core logic (processing, categorization, tags)
├── pages/             # Routes (pages + API endpoints)
│   ├── api/           # REST API endpoints
│   ├── content/       # Content detail and save pages
│   └── ...            # Dashboard, search, timeline, auth pages
├── styles/            # Global CSS with Tailwind v4
└── types/             # TypeScript types and constants
```

## Features

- URL saving with automatic metadata extraction
- Smart categorization (20 categories)
- Auto tag generation
- Full-text search
- Timeline view
- Responsive design (mobile-first, 375px+)
- PWA support
- Dark mode

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Sign in |
| GET/POST | `/api/auth/logout` | Sign out |
| GET | `/api/auth/me` | Current user |
| GET | `/api/content` | List saved content |
| POST | `/api/content` | Save new content |
| GET | `/api/content/:id` | Get content details |
| DELETE | `/api/content/:id` | Delete content |
| GET | `/api/search` | Search content |
| GET | `/api/categories` | List categories |
| GET | `/api/insights/dashboard` | Dashboard stats |

## Roadmap

### Phase 1 — Current
- URL saving with metadata extraction
- Categories and tags
- Search and timeline
- PWA support

### Phase 2 — Coming Next
- Collections for grouping content
- Browser extension
- Advanced filtering

### Phase 3 — Future
- AI summaries (optional)
- Semantic search
- Knowledge graph

## Deployment

See [DEPLOYMENT.md](./docs/DEPLOYMENT.md) for detailed deployment instructions to Vercel + Neon.

## License

MIT
