import type { APIRoute } from 'astro'
import { prisma } from '../../lib/prisma'
import { verifySession } from '../../lib/auth'

export const GET: APIRoute = async ({ cookies, url }) => {
  const session = cookies.get('session')?.value
  if (!session) {
    return new Response(JSON.stringify({ error: 'Unauthorized' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' },
    })
  }

  const payload = verifySession(session)
  if (!payload) {
    return new Response(JSON.stringify({ error: 'Unauthorized' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' },
    })
  }

  const query = url.searchParams.get('q') || ''
  const category = url.searchParams.get('category') || ''
  const limit = Math.min(Number(url.searchParams.get('limit')) || 20, 100)
  const offset = Number(url.searchParams.get('offset')) || 0

  const where: any = { userId: payload.userId }

  if (query) {
    where.OR = [
      { title: { contains: query, mode: 'insensitive' } },
      { description: { contains: query, mode: 'insensitive' } },
      { category: { contains: query, mode: 'insensitive' } },
    ]
  }

  if (category) {
    where.category = category
  }

  try {
    const [items, total] = await Promise.all([
      prisma.savedContent.findMany({
        where,
        orderBy: { createdAt: 'desc' },
        take: limit,
        skip: offset,
        include: { tags: { include: { tag: true } } },
      }),
      prisma.savedContent.count({ where }),
    ])

    const results = items.map((item) => ({
      content: {
        ...item,
        tags: item.tags.map((ct) => ({ id: ct.tag.id, name: ct.tag.name, slug: ct.tag.slug })),
        createdAt: item.createdAt.toISOString(),
        updatedAt: item.updatedAt.toISOString(),
        publishedAt: item.publishedAt?.toISOString() || null,
        lastViewedAt: item.lastViewedAt?.toISOString() || null,
      },
      score: 100,
      matchType: 'keyword' as const,
    }))

    return new Response(JSON.stringify({ results, total }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    })
  } catch {
    return new Response(JSON.stringify({ results: [], total: 0 }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    })
  }
}
