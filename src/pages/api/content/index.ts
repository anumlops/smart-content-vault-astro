import type { APIRoute } from 'astro'
import { prisma } from '../../../lib/prisma'
import { processContent } from '../../../lib/processing'
import { enrichContent } from '../../../lib/enrich'
import { verifySession } from '../../../lib/auth'

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

  const category = url.searchParams.get('category')
  const limit = Math.min(Number(url.searchParams.get('limit')) || 20, 100)
  const offset = Number(url.searchParams.get('offset')) || 0

  const where: any = { userId: payload.userId }
  if (category) where.category = category

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

  const mapped = items.map((item) => ({
    ...item,
    tags: item.tags.map((ct) => ({ id: ct.tag.id, name: ct.tag.name, slug: ct.tag.slug })),
    createdAt: item.createdAt.toISOString(),
    updatedAt: item.updatedAt.toISOString(),
    publishedAt: item.publishedAt?.toISOString() || null,
    lastViewedAt: item.lastViewedAt?.toISOString() || null,
  }))

  return new Response(JSON.stringify({ items: mapped, total }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  })
}

export const POST: APIRoute = async ({ request, cookies, redirect }) => {
  const session = cookies.get('session')?.value
  if (!session) {
    return redirect('/login')
  }

  const payload = verifySession(session)
  if (!payload) {
    return redirect('/login')
  }

  try {
    const formData = await request.formData()
    const url = formData.get('url')?.toString()

    if (!url) {
      return redirect('/content/new?error=URL is required')
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

    return redirect(`/content/${content.id}`)
  } catch {
    return redirect('/content/new?error=Failed to save content')
  }
}
