import type { APIRoute } from 'astro'

const YOUTUBE_VIDEO_ID_RE = /(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]+)/
const OEMBED_URL = 'https://www.youtube.com/oembed'

function extractMetaContent(html: string, property: string): string {
  const patterns = [
    `property="og:${property}"`,
    `name="og:${property}"`,
    `name="${property}"`,
  ]
  for (const p of patterns) {
    const propIdx = html.indexOf(p)
    if (propIdx === -1) continue
    const contentIdx = html.indexOf(' content="', propIdx)
    if (contentIdx === -1) continue
    const start = contentIdx + 10
    const end = html.indexOf('"', start)
    if (end === -1) continue
    return html.substring(start, end)
  }
  return ''
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

function extractVideoId(url: string): string | null {
  const m = url.match(YOUTUBE_VIDEO_ID_RE)
  return m ? m[1] : null
}

function isYouTubeUrl(url: string): boolean {
  try {
    const hostname = new URL(url).hostname.replace('www.', '').replace('m.', '')
    return ['youtube.com', 'youtu.be'].includes(hostname)
  } catch {
    return false
  }
}

async function fetchOEmbed(videoUrl: string) {
  try {
    const resp = await fetch(`${OEMBED_URL}?url=${encodeURIComponent(videoUrl)}&format=json`, {
      headers: { Accept: 'application/json' },
    })
    if (!resp.ok) return null
    return await resp.json()
  } catch {
    return null
  }
}

async function fetchYouTubePage(videoUrl: string) {
  try {
    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort(), 10000)
    const resp = await fetch(videoUrl, {
      signal: controller.signal,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        Accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
      },
    })
    clearTimeout(timeout)
    if (!resp.ok) return ''
    return await resp.text()
  } catch {
    return ''
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

    if (!isYouTubeUrl(url)) {
      return new Response(JSON.stringify({ success: false, error: 'Not a YouTube URL' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    const videoId = extractVideoId(url)
    if (!videoId) {
      return new Response(JSON.stringify({ success: false, error: 'Could not extract video ID from URL' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    const watchUrl = `https://www.youtube.com/watch?v=${videoId}`
    const oembed = await fetchOEmbed(watchUrl)
    const html = await fetchYouTubePage(watchUrl)

    const title = oembed?.title || ''
    const channelName = oembed?.author_name || ''
    const channelUrl = oembed?.author_url || ''
    const thumbnail = oembed?.thumbnail_url || `https://i.ytimg.com/vi/${videoId}/maxresdefault.jpg`

    const ogDesc = extractMetaContent(html, 'description')
    const metaDesc = extractMetaContent(html, 'description')
    const description = ogDesc || metaDesc || ''

    return new Response(
      JSON.stringify({
        success: true,
        data: {
          platform: 'youtube',
          url,
          canonicalUrl: watchUrl,
          title,
          description,
          thumbnail: isValidImageUrl(thumbnail) ? thumbnail : '',
          channelName,
          channelUrl,
          videoId,
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
