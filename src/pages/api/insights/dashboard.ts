import type { APIRoute } from 'astro'
import { prisma } from '../../../lib/prisma'
import { verifySession } from '../../../lib/auth'

export const GET: APIRoute = async ({ cookies }) => {
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

  try {
    const totalSaves = await prisma.savedContent.count({
      where: { userId: payload.userId },
    })

    const categoryRaw = await prisma.savedContent.groupBy({
      by: ['category'],
      where: { userId: payload.userId },
      _count: { id: true },
    })

    const categoryDistribution: Record<string, number> = {}
    for (const cat of categoryRaw) {
      if (cat.category) categoryDistribution[cat.category] = cat._count.id
    }

    const recentSavesRaw = await prisma.savedContent.findMany({
      where: { userId: payload.userId },
      orderBy: { createdAt: 'desc' },
      take: 5,
      include: { tags: { include: { tag: true } } },
    })

    const recentSaves = recentSavesRaw.map((item) => ({
      ...item,
      tags: item.tags.map((ct) => ({ id: ct.tag.id, name: ct.tag.name, slug: ct.tag.slug })),
      createdAt: item.createdAt.toISOString(),
      updatedAt: item.updatedAt.toISOString(),
      publishedAt: item.publishedAt?.toISOString() || null,
      lastViewedAt: item.lastViewedAt?.toISOString() || null,
    }))

    return new Response(
      JSON.stringify({ totalSaves, categoryDistribution, recentSaves, topTags: [], weeklyActivity: [] }),
      { status: 200, headers: { 'Content-Type': 'application/json' } }
    )
  } catch {
    return new Response(
      JSON.stringify({ totalSaves: 0, categoryDistribution: {}, recentSaves: [], topTags: [], weeklyActivity: [] }),
      { status: 200, headers: { 'Content-Type': 'application/json' } }
    )
  }
}
