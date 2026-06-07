import type { APIRoute } from 'astro'
import { prisma } from '../../../lib/prisma'
import { processContent } from '../../../lib/processing'
import { enrichContent } from '../../../lib/enrich'
import { verifySession } from '../../../lib/auth'

export const POST: APIRoute = async ({ request, cookies }) => {
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
    const body = await request.json()
    const url = body.url?.toString()

    if (!url) {
      return new Response(JSON.stringify({ error: 'URL is required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    try {
      new URL(url)
    } catch {
      return new Response(JSON.stringify({ error: 'Invalid URL' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    const processed = await processContent(url)

    const content = await prisma.savedContent.create({
      data: {
        userId: payload.userId,
        originalUrl: processed.originalUrl,
        normalizedUrl: processed.normalizedUrl,
        sourceDomain: processed.sourceDomain,
        contentType: processed.contentType,
        title: processed.title,
        description: processed.description,
        thumbnailUrl: processed.thumbnailUrl,
        faviconUrl: processed.faviconUrl,
        author: processed.author,
        publisher: processed.publisher,
        publishedAt: processed.publishedAt,
        category: processed.category,
        enrichmentStatus: processed.enrichmentStatus,
        tags: {
          create: await Promise.all(
            processed.tags.map(async (tagName) => {
              const slug = tagName.toLowerCase().replace(/[^a-z0-9-]/g, '')
              const tag = await prisma.tag.upsert({
                where: { slug },
                update: {},
                create: { name: tagName, slug },
              })
              return { tagId: tag.id }
            })
          ),
        },
      },
    })

    await enrichContent(content.id, processed.originalUrl).catch(() => {})

    return new Response(JSON.stringify({ id: content.id }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    })
  } catch {
    return new Response(JSON.stringify({ error: 'Failed to save content' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    })
  }
}
