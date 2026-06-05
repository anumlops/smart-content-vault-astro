import type { APIRoute } from 'astro'
import { prisma } from '../../lib/prisma'
import { verifySession } from '../../lib/auth'

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
    const result = await prisma.savedContent.groupBy({
      by: ['category'],
      where: { userId: payload.userId },
      _count: { id: true },
    })

    const categories = result
      .filter((r) => r.category)
      .map((r) => ({ name: r.category, count: r._count.id }))

    return new Response(JSON.stringify(categories), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    })
  } catch {
    return new Response(JSON.stringify([]), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    })
  }
}
