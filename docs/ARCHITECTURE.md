# Architecture Guide

## Overview

Smart Content Vault is built with AstroJS as a server-rendered application with REST API endpoints. The architecture follows a layered approach:

```
User Layer → Presentation Layer → API Layer → Service Layer → Data Layer
```

## Layers

### Presentation Layer (Astro Pages)
- Server-rendered HTML with Astro components
- Responsive mobile-first design
- Layouts: BaseLayout, DashboardLayout, AuthLayout

### API Layer (Astro Server Endpoints)
- RESTful endpoints under `/api/`
- Session-based authentication via httpOnly cookies
- JSON responses for API consumers

### Service Layer
- `lib/processing.ts` — Content ingestion pipeline
- `lib/categorizer.ts` — Keyword-based category assignment
- `lib/tag-generator.ts` — Automatic tag generation
- `lib/thumbnail.ts` — Thumbnail resolution

### Data Layer
- Prisma ORM with PostgreSQL (Neon)
- Models: User, SavedContent, Category, Tag, ContentTag
- Connection pooling via Prisma client singleton

## Data Flow

### Content Save Flow
```
User submits URL → POST /api/content
  → processContent() extracts metadata
  → categorize() assigns category
  → generateTags() creates tags
  → Prisma saves to PostgreSQL
  → Redirect to content detail page
```

### Search Flow
```
User enters query → GET /api/search?q=...
  → Prisma performs LIKE search across title, description, category
  → Results returned with match scores
  → Rendered in SearchResults component
```

## Key Design Decisions

1. **AstroJS over Next.js** — Simpler SSR, better performance, less client JS
2. **Tailwind CSS v4** — Latest utility-first framework with CSS-first config
3. **Prisma v5** — Stable ORM with type-safe queries
4. **Session Auth** — httpOnly cookies for security, no JWT complexity
5. **No AI dependency** — All categorization and tagging is rule-based
