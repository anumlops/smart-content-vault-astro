import type { APIRoute } from 'astro'
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
  try {
    const u = new URL(s)
    return u.protocol === 'http:' || u.protocol === 'https:'
  } catch {
    return false
  }
}

async function fetchInstagramOG(url: string) {
  const empty = { title: '', description: '', thumbnail: '', url: '', htmlSize: 0 }

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
    const title = extractMetaContent(html, 'og:title')
    const description = extractMetaContent(html, 'og:description')
    const ogUrl = extractMetaContent(html, 'og:url') || url

    return {
      title,
      description,
      thumbnail: isValidImageUrl(thumbnail) ? thumbnail : '',
      url: ogUrl,
      htmlSize: html.length,
    }
  } catch {
    return empty
  }
}

export const POST: APIRoute = async ({ request }) => {
  try {
    const body = await request.json()
    const rawUrl = body.url?.toString().trim()

    if (!rawUrl) {
      return new Response(JSON.stringify({ success: false, error: 'URL is required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    const url = rawUrl.startsWith('http') ? rawUrl : 'https://' + rawUrl

    let hostname: string
    try { hostname = new URL(url).hostname.replace('www.', '') } catch {
      return new Response(JSON.stringify({ success: false, error: 'Invalid URL' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    if (!/instagram\.com/i.test(hostname)) {
      return new Response(JSON.stringify({ success: false, error: 'Not an Instagram URL' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    const og = await fetchInstagramOG(url)

    return new Response(
      JSON.stringify({
        success: true,
        data: {
          platform: 'instagram',
          url,
          title: og.title,
          description: og.description,
          thumbnail: og.thumbnail,
          extractedAt: new Date().toISOString(),
        },
      }),
      { status: 200, headers: { 'Content-Type': 'application/json' } }
    )
  } catch {
    return new Response(JSON.stringify({ success: false, error: 'Extraction failed' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    })
  }
}
