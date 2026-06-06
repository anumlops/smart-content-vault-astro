import type { APIRoute } from 'astro'
import { prisma } from '../../lib/prisma'
import { verifySession } from '../../lib/auth'
import { getDomain } from '../../lib/utils'

const PYTHON_SERVICE_URL = process.env.WEBSITE_INTELLIGENCE_URL || 'http://localhost:8001'

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

    if (!contentId) {
      return new Response(JSON.stringify({ error: 'contentId is required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    const content = await prisma.savedContent.findUnique({
      where: { id: contentId },
    })

    if (!content || content.userId !== payload.userId) {
      return new Response(JSON.stringify({ error: 'Content not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    await prisma.savedContent.update({
      where: { id: contentId },
      data: { enrichmentStatus: 'processing' },
    })

    let analysisResult: any

    try {
      const controller = new AbortController()
      const timeout = setTimeout(() => controller.abort(), 30000)

      const response = await fetch(`${PYTHON_SERVICE_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: content.originalUrl }),
        signal: controller.signal,
      })
      clearTimeout(timeout)

      if (!response.ok) {
        throw new Error(`Python service returned ${response.status}`)
      }

      analysisResult = await response.json()
    } catch (serviceError: any) {
      // Fallback: use existing metadata as enrichment
      analysisResult = {
        url: content.originalUrl,
        domain: getDomain(content.originalUrl),
        title: content.title,
        summary: content.description,
        category: content.category,
        tags: [],
        key_takeaways: [],
        status: 'completed',
        error: serviceError.message || 'Python service unavailable, used fallback',
      }
    }

    const tags = analysisResult.tags || []
    const category = analysisResult.category || content.category || null

    await prisma.savedContent.update({
      where: { id: contentId },
      data: {
        title: analysisResult.title || content.title,
        description: analysisResult.summary || content.description,
        category: category,
        aiSummary: analysisResult.summary || null,
        aiTags: JSON.stringify(tags),
        aiCategory: category,
        enrichmentStatus: 'completed',
        processingVersion: 1,
      },
    })

    if (tags.length > 0) {
      const existingTags = await prisma.contentTag.findMany({
        where: { contentId },
        select: { tagId: true },
      })
      const existingTagIds = new Set(existingTags.map((t) => t.tagId))

      for (const tagName of tags) {
        const slug = tagName.toLowerCase().replace(/[^a-z0-9-]/g, '')
        const tag = await prisma.tag.upsert({
          where: { slug },
          update: {},
          create: { name: tagName, slug },
        })

        if (!existingTagIds.has(tag.id)) {
          await prisma.contentTag.create({
            data: { contentId, tagId: tag.id },
          }).catch(() => {})
        }
      }
    }

    return new Response(
      JSON.stringify({
        success: true,
        id: contentId,
        title: analysisResult.title || content.title,
        summary: analysisResult.summary || content.description,
        category: category,
        tags: tags,
        key_takeaways: analysisResult.key_takeaways || [],
        enrichmentStatus: 'completed',
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
      enrichmentStatus: content.enrichmentStatus,
      keyTakeaways: [], // stored in a future model
    }),
    { status: 200, headers: { 'Content-Type': 'application/json' } }
  )
}
