import type { APIRoute } from 'astro'
import { prisma } from '../../../lib/prisma'
import { verifySession } from '../../../lib/auth'
import { normalizeUrl, getDomain } from '../../../lib/utils'
import { INSTAGRAM_CATEGORIES } from '../../../modules/instagram/categories'
import { decodeHtmlEntities } from '../../../lib/utils'

function extractMetaContent(html: string, property: string): string {
  const propIdx = html.indexOf(`property="` + property + `"`)
  if (propIdx === -1) return ''
  const contentIdx = html.indexOf(` content="`, propIdx)
  if (contentIdx === -1) return ''
  const start = contentIdx + 10
  const end = html.indexOf(`"`, start)
  if (end === -1) return ''
  return decodeHtmlEntities(html.substring(start, end))
}

function isValidImageUrl(s: string): boolean {
  if (!s) return false
  try { new URL(s); return true } catch { return false }
}

async function fetchInstagramOG(url: string) {
  const empty = { title: '', description: '', thumbnail: '', url: '' }

  try {
    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort(), 15000)

    const response = await fetch(url, {
      signal: controller.signal,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        Accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        Referer: 'https://www.instagram.com/',
        'Cache-Control': 'max-age=0',
      },
    })
    clearTimeout(timeout)

    if (!response.ok) return empty

    const html = await response.text()
    if (!html) return empty

    const thumbnail = extractMetaContent(html, 'og:image')

    return {
      title: extractMetaContent(html, 'og:title'),
      description: extractMetaContent(html, 'og:description'),
      thumbnail: isValidImageUrl(thumbnail) ? thumbnail : '',
      url: extractMetaContent(html, 'og:url') || url,
    }
  } catch {
    return empty
  }
}

export const GET: APIRoute = async ({ cookies, url }) => {
  const session = cookies.get('session')?.value
  if (!session) {
    return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401, headers: { 'Content-Type': 'application/json' } })
  }

  const payload = verifySession(session)
  if (!payload) {
    return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401, headers: { 'Content-Type': 'application/json' } })
  }

  const category = url.searchParams.get('category')
  const limit = Math.min(Number(url.searchParams.get('limit')) || 50, 100)
  const offset = Number(url.searchParams.get('offset')) || 0

  const where: any = { userId: payload.userId, contentType: 'instagram' }
  if (category) where.category = category

  const [items, total] = await Promise.all([
    prisma.savedContent.findMany({
      where,
      orderBy: { createdAt: 'desc' },
      take: limit,
      skip: offset,
    }),
    prisma.savedContent.count({ where }),
  ])

  const mapped = items.map((item) => ({
    id: item.id,
    url: item.originalUrl,
    title: item.title,
    description: item.description,
    thumbnail: item.thumbnailUrl,
    category: item.category || 'unassigned',
    createdAt: item.createdAt.toISOString(),
  }))

  return new Response(JSON.stringify({ items: mapped, total }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  })
}

export const POST: APIRoute = async ({ request, cookies }) => {
  const session = cookies.get('session')?.value
  if (!session) {
    return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401, headers: { 'Content-Type': 'application/json' } })
  }

  const payload = verifySession(session)
  if (!payload) {
    return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401, headers: { 'Content-Type': 'application/json' } })
  }

  try {
    const body = await request.json()
    const contentId = body.id?.toString().trim()
    const category = body.category?.toString().trim()

    if (contentId) {
      const validCategoryIds = INSTAGRAM_CATEGORIES.map((c) => c.id)
      if (!category || !validCategoryIds.includes(category)) {
        return new Response(JSON.stringify({ error: 'Invalid category' }), { status: 400, headers: { 'Content-Type': 'application/json' } })
      }

      const existing = await prisma.savedContent.findUnique({ where: { id: contentId } })
      if (!existing || existing.userId !== payload.userId) {
        return new Response(JSON.stringify({ error: 'Content not found' }), { status: 404, headers: { 'Content-Type': 'application/json' } })
      }

      await prisma.savedContent.update({
        where: { id: contentId },
        data: { category },
      })

      return new Response(JSON.stringify({ id: contentId, category }), { status: 200, headers: { 'Content-Type': 'application/json' } })
    }

    const rawUrl = body.url?.toString().trim()

    if (!rawUrl) {
      return new Response(JSON.stringify({ error: 'URL is required' }), { status: 400, headers: { 'Content-Type': 'application/json' } })
    }

    const url = normalizeUrl(rawUrl)
    let hostname: string
    try { hostname = new URL(url).hostname.replace('www.', '') } catch {
      return new Response(JSON.stringify({ error: 'Invalid URL' }), { status: 400, headers: { 'Content-Type': 'application/json' } })
    }

    if (!/instagram\.com/i.test(hostname)) {
      return new Response(JSON.stringify({ error: 'Not an Instagram URL' }), { status: 400, headers: { 'Content-Type': 'application/json' } })
    }

    const validCategoryIds = INSTAGRAM_CATEGORIES.map((c) => c.id)
    const finalCategory = category && validCategoryIds.includes(category) ? category : 'unassigned'

    const og = await fetchInstagramOG(url)

    const content = await prisma.savedContent.create({
      data: {
        userId: payload.userId,
        originalUrl: url,
        normalizedUrl: url,
        sourceDomain: 'instagram.com',
        contentType: 'instagram',
        title: og.title || null,
        description: og.description || null,
        thumbnailUrl: og.thumbnail || null,
        category: finalCategory,
        enrichmentStatus: 'completed',
      },
    })

    return new Response(
      JSON.stringify({
        id: content.id,
        url,
        title: og.title,
        description: og.description,
        thumbnail: og.thumbnail,
        category: finalCategory,
        createdAt: content.createdAt.toISOString(),
      }),
      { status: 200, headers: { 'Content-Type': 'application/json' } }
    )
  } catch {
    return new Response(JSON.stringify({ error: 'Failed to save Instagram content' }), { status: 500, headers: { 'Content-Type': 'application/json' } })
  }
}
