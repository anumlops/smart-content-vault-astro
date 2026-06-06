import type { APIRoute } from 'astro'
import { prisma } from '../../lib/prisma'
import { verifySession } from '../../lib/auth'
import { WebsiteProcessor } from '../../modules/website/service'

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
    const contentId = body.contentId?.toString()
    const url = body.url?.toString()

    if (!contentId && !url) {
      return new Response(JSON.stringify({ error: 'contentId or url required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    let targetUrl = url
    let existingContent = null

    if (contentId) {
      existingContent = await prisma.savedContent.findUnique({
        where: { id: contentId },
      })

      if (!existingContent || existingContent.userId !== payload.userId) {
        return new Response(JSON.stringify({ error: 'Content not found' }), {
          status: 404,
          headers: { 'Content-Type': 'application/json' },
        })
      }

      targetUrl = existingContent.originalUrl
    }

    if (!targetUrl) {
      return new Response(JSON.stringify({ error: 'No URL to process' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    if (existingContent) {
      await prisma.savedContent.update({
        where: { id: contentId },
        data: { enrichmentStatus: 'processing' },
      })
    }

    const processor = new WebsiteProcessor()
    const result = await processor.processUrl(targetUrl)

    if (existingContent && contentId) {
      await prisma.savedContent.update({
        where: { id: contentId },
        data: {
          title: result.title || existingContent.title,
          description: result.summary || existingContent.description,
          category: result.category || existingContent.category,
          aiSummary: result.summary,
          aiTags: JSON.stringify(result.tags),
          aiCategory: result.category,
          keyTakeaways: JSON.stringify(result.keyTakeaways),
          enrichmentStatus: result.status,
          processingVersion: (existingContent.processingVersion || 0) + 1,
        },
      })

      for (const tagName of result.tags) {
        const slug = tagName.toLowerCase().replace(/[^a-z0-9-]/g, '')
        const tag = await prisma.tag.upsert({
          where: { slug },
          update: {},
          create: { name: tagName, slug },
        })

        const exists = await prisma.contentTag.findUnique({
          where: { contentId_tagId: { contentId, tagId: tag.id } },
        })

        if (!exists) {
          await prisma.contentTag.create({
            data: { contentId, tagId: tag.id },
          }).catch(() => {})
        }
      }
    }

    return new Response(
      JSON.stringify({
        success: true,
        id: contentId || null,
        url: targetUrl,
        title: result.title,
        summary: result.summary,
        category: result.category,
        tags: result.tags,
        keyTakeaways: result.keyTakeaways,
        enrichmentStatus: result.status,
        error: result.error,
      }),
      { status: 200, headers: { 'Content-Type': 'application/json' } }
    )
  } catch (e: any) {
    return new Response(
      JSON.stringify({ error: e.message || 'Enrichment failed' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    )
  }
}

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

  const contentId = url.searchParams.get('contentId')

  if (!contentId) {
    return new Response(JSON.stringify({ error: 'contentId is required' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    })
  }

  const content = await prisma.savedContent.findUnique({
    where: { id: contentId },
    include: { tags: { include: { tag: true } } },
  })

  if (!content || content.userId !== payload.userId) {
    return new Response(JSON.stringify({ error: 'Not found' }), {
      status: 404,
      headers: { 'Content-Type': 'application/json' },
    })
  }

  return new Response(
    JSON.stringify({
      id: content.id,
      url: content.originalUrl,
      title: content.title,
      description: content.description,
      category: content.category,
      tags: content.tags.map((t) => t.tag.name),
      aiSummary: content.aiSummary,
      aiTags: content.aiTags ? JSON.parse(content.aiTags) : [],
      aiCategory: content.aiCategory,
      keyTakeaways: content.keyTakeaways ? JSON.parse(content.keyTakeaways) : [],
      enrichmentStatus: content.enrichmentStatus,
    }),
    { status: 200, headers: { 'Content-Type': 'application/json' } }
  )
}
