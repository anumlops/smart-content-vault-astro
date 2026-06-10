import type { APIRoute } from 'astro'
import { prisma } from '../../../lib/prisma'
import { processContent } from '../../../lib/processing'
import { enrichContent } from '../../../lib/enrich'
import { verifySession } from '../../../lib/auth'
import { INSTAGRAM_CATEGORIES } from '../../../modules/instagram/categories'
import { YOUTUBE_CATEGORIES } from '../../../modules/youtube/categories'

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
    const categoryOverride = body.category?.toString().trim()

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

    const validInstagramCats = INSTAGRAM_CATEGORIES.map((c) => c.id)
    const finalCategory = processed.contentType === 'instagram' && categoryOverride && validInstagramCats.includes(categoryOverride)
      ? categoryOverride
      : processed.category

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
        category: finalCategory,
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

    const responseData: any = { id: content.id, contentType: processed.contentType }

    if (processed.contentType === 'instagram') {
      responseData.category = finalCategory
      responseData.availableCategories = INSTAGRAM_CATEGORIES.map((c) => ({ id: c.id, label: c.label }))
      responseData.thumbnail = processed.thumbnailUrl
      responseData.title = processed.title
      responseData.description = processed.description
    } else if (processed.contentType === 'youtube') {
      responseData.category = finalCategory
      responseData.availableCategories = YOUTUBE_CATEGORIES.map((c) => ({ id: c.id, label: c.label }))
      responseData.thumbnail = processed.thumbnailUrl
      responseData.title = processed.title
      responseData.description = processed.description
    }

    return new Response(JSON.stringify(responseData), {
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
