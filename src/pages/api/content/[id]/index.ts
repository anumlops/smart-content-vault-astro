import type { APIRoute } from 'astro'
import { prisma } from '../../../../lib/prisma'
import { verifySession } from '../../../../lib/auth'

export const GET: APIRoute = async ({ params, cookies }) => {
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

  const { id } = params

  try {
    const content = await prisma.savedContent.findUnique({
      where: { id },
      include: { tags: { include: { tag: true } } },
    })

    if (!content || content.userId !== payload.userId) {
      return new Response(JSON.stringify({ error: 'Not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    await prisma.savedContent.update({
      where: { id },
      data: { viewCount: { increment: 1 }, lastViewedAt: new Date() },
    })

    const mapped = {
      ...content,
      tags: content.tags.map((ct) => ({ id: ct.tag.id, name: ct.tag.name, slug: ct.tag.slug })),
      createdAt: content.createdAt.toISOString(),
      updatedAt: content.updatedAt.toISOString(),
      publishedAt: content.publishedAt?.toISOString() || null,
      lastViewedAt: content.lastViewedAt?.toISOString() || null,
    }

    return new Response(JSON.stringify(mapped), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    })
  } catch {
    return new Response(JSON.stringify({ error: 'Not found' }), {
      status: 404,
      headers: { 'Content-Type': 'application/json' },
    })
  }
}

export const DELETE: APIRoute = async ({ params, cookies }) => {
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

  const { id } = params

  try {
    const content = await prisma.savedContent.findUnique({ where: { id } })
    if (!content || content.userId !== payload.userId) {
      return new Response(JSON.stringify({ error: 'Not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    await prisma.savedContent.delete({ where: { id } })

    return new Response(null, { status: 204 })
  } catch {
    return new Response(JSON.stringify({ error: 'Delete failed' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    })
  }
}
