import type { APIRoute } from 'astro'
import { categorize } from '../../../lib/categorizer'
import { generateTags } from '../../../lib/tag-generator'
import { decodeHtmlEntities, getDomain } from '../../../lib/utils'

function extractMetaAttribute(html: string, property: string, attr: string): string {
  const propIdx = html.indexOf(`property="` + property + `"`)
  if (propIdx === -1) return ''
  const attrIdx = html.indexOf(` ` + attr + `="`, propIdx)
  if (attrIdx === -1) return ''
  const start = attrIdx + attr.length + 3
  const end = html.indexOf(`"`, start)
  if (end === -1) return ''
  return html.substring(start, end)
}

function extractMetaContent(html: string, property: string): string {
  return decodeHtmlEntities(extractMetaAttribute(html, property, 'content'))
}

function extractTagContent(html: string, tag: string): string {
  const open = `<${tag}`
  const openIdx = html.indexOf(open)
  if (openIdx === -1) return ''
  const closeIdx = html.indexOf(`>`, openIdx)
  if (closeIdx === -1) return ''
  const endIdx = html.indexOf(`</${tag}>`, closeIdx)
  if (endIdx === -1) return ''
  return html.substring(closeIdx + 1, endIdx).trim()
}

function extractLinkHref(html: string, rel: string): string {
  const relIdx = html.indexOf(`rel="` + rel + `"`)
  if (relIdx === -1) return ''
  const hrefIdx = html.indexOf(`href="`, relIdx)
  if (hrefIdx === -1) return ''
  const start = hrefIdx + 6
  const end = html.indexOf(`"`, start)
  if (end === -1) return ''
  return html.substring(start, end)
}

function extractMetaNameContent(html: string, name: string): string {
  const nameIdx = html.indexOf(`name="` + name + `"`)
  if (nameIdx === -1) return ''
  const contentIdx = html.indexOf(`content="`, nameIdx)
  if (contentIdx === -1) return ''
  const start = contentIdx + 9
  const end = html.indexOf(`"`, start)
  if (end === -1) return ''
  return decodeHtmlEntities(html.substring(start, end))
}

interface InstagramMetadata {
  title: string
  description: string
  image: string
  url: string
  canonicalUrl: string
  pageTitle: string
  metaDescription: string
}

async function fetchInstagramMetadata(url: string): Promise<InstagramMetadata> {
  const empty: InstagramMetadata = {
    title: '', description: '', image: '', url,
    canonicalUrl: '', pageTitle: '', metaDescription: '',
  }

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

    return {
      title: extractMetaContent(html, 'og:title'),
      description: extractMetaContent(html, 'og:description'),
      image: extractMetaContent(html, 'og:image'),
      url: extractMetaContent(html, 'og:url') || url,
      canonicalUrl: extractLinkHref(html, 'canonical'),
      pageTitle: decodeHtmlEntities(extractTagContent(html, 'title')),
      metaDescription: extractMetaNameContent(html, 'description'),
    }
  } catch {
    return empty
  }
}

export const POST: APIRoute = async ({ request }) => {
  try {
    const body = await request.json()
    const url = body.url?.toString().trim()

    if (!url) {
      return new Response(JSON.stringify({ success: false, error: 'URL is required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    let validUrl = url
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      validUrl = 'https://' + url
    }

    const domain = getDomain(validUrl)
    if (!/instagram\.com/i.test(domain)) {
      return new Response(JSON.stringify({ success: false, error: 'Not an Instagram URL' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    const meta = await fetchInstagramMetadata(validUrl)

    const titleText = meta.title || meta.pageTitle || validUrl
    const description = meta.description || meta.metaDescription || ''
    const category = categorize(titleText, validUrl)
    const tags = generateTags(titleText, validUrl)

    return new Response(
      JSON.stringify({
        success: true,
        data: {
          platform: 'instagram',
          url: validUrl,
          canonical_url: meta.canonicalUrl || validUrl,
          title: meta.title || meta.pageTitle || '',
          description,
          thumbnail: meta.image || '',
          extracted_at: new Date().toISOString(),
          category,
          tags,
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
