# Setup Guide

## Prerequisites

- Node.js 20+
- npm 10+
- PostgreSQL database (local or Neon)

## Local Development

### 1. Clone and Install

```bash
git clone <repo-url>
cd limo
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your database connection string:

```
DATABASE_URL="postgresql://user:password@host:5432/dbname?schema=public"
AUTH_SECRET="your-random-secret-at-least-32-chars"
PUBLIC_APP_URL="http://localhost:4321"
```

### 3. Set Up Database

```bash
npm run prisma:generate
npm run prisma:push
```

### 4. Start Development Server

```bash
npm run dev
```

Visit http://localhost:4321

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `AUTH_SECRET` | Session signing secret (32+ chars) | Yes |
| `PUBLIC_APP_URL` | Application base URL | Yes |

## Database Management

```bash
npm run prisma:studio   # Open Prisma Studio (GUI)
npm run prisma:push     # Push schema to database
npm run prisma:generate # Regenerate Prisma client
```
