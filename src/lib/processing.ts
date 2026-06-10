import { getDomain, normalizeUrl, getContentType, decodeHtmlEntities } from './utils'
import { categorize } from './categorizer'
import { generateTags } from './tag-generator'
import { InstagramCrawler } from '../modules/instagram/crawler'

const instagramCrawler = new InstagramCrawler()

interface MetadataResult {
  title: string | null
  description: string | null
  thumbnailUrl: string | null
  faviconUrl: string | null
  author: string | null
  publisher: string | null
  publishedAt: string | null
}

async function extractMetadata(url: string): Promise<MetadataResult> {
  const metadata: MetadataResult = {
    title: null,
    description: null,
    thumbnailUrl: null,
    faviconUrl: null,
    author: null,
    publisher: null,
    publishedAt: null,
  }

  if (instagramCrawler.canHandle(url)) {
    const result = await instagramCrawler.extract(url)
    if (!result.error) {
      metadata.title = result.title
      metadata.description = result.description
      metadata.thumbnailUrl = result.thumbnail
    }
    return metadata
  }

  try {
    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort(), 5000)

    const response = await fetch(url, {
      signal: controller.signal,
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; Limo/1.0)',
        'Accept': 'text/html, application/xhtml+xml',
      },
    })
    clearTimeout(timeout)

    metadata.faviconUrl = `https://www.google.com/s2/favicons?domain=${getDomain(url)}&sz=64`

    if (response.ok) {
      const html = await response.text()

      const titleMatch = html.match(/<title[^>]*>([^<]*)<\/title>/i)
      if (titleMatch) metadata.title = decodeHtmlEntities(titleMatch[1].trim())

      const ogTitleMatch = html.match(/<meta[^>]+property=["']og:title["'][^>]+content=["']([^"']*)["'][^>]*\/?>/i)
      if (ogTitleMatch) metadata.title = decodeHtmlEntities(ogTitleMatch[1])

      const descMatch = html.match(/<meta[^>]+name=["']description["'][^>]+content=["']([^"']*)["'][^>]*\/?>/i)
      if (descMatch) metadata.description = decodeHtmlEntities(descMatch[1])

      const ogDescMatch = html.match(/<meta[^>]+property=["']og:description["'][^>]+content=["']([^"']*)["'][^>]*\/?>/i)
      if (ogDescMatch) metadata.description = decodeHtmlEntities(ogDescMatch[1])

      const ogImageMatch = html.match(/<meta[^>]+property=["']og:image["'][^>]+content=["']([^"']*)["'][^>]*\/?>/i)
      if (ogImageMatch) metadata.thumbnailUrl = ogImageMatch[1]

      const ogAuthorMatch = html.match(/<meta[^>]+property=["']article:author["'][^>]+content=["']([^"']*)["'][^>]*\/?>/i)
      if (ogAuthorMatch) metadata.author = decodeHtmlEntities(ogAuthorMatch[1])

      const ogPubMatch = html.match(/<meta[^>]+property=["']article:published_time["'][^>]+content=["']([^"']*)["'][^>]*\/?>/i)
      if (ogPubMatch) metadata.publishedAt = ogPubMatch[1]

      const ogSiteMatch = html.match(/<meta[^>]+property=["']og:site_name["'][^>]+content=["']([^"']*)["'][^>]*\/?>/i)
      if (ogSiteMatch) metadata.publisher = decodeHtmlEntities(ogSiteMatch[1])

      if (!metadata.title) {
        const h1Match = html.match(/<h1[^>]*>([^<]*)<\/h1>/i)
        if (h1Match) metadata.title = decodeHtmlEntities(h1Match[1].trim())
      }
    }
  } catch {
    // Metadata extraction failed silently
  }

  const youtubeMatch = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]+)/)
  if (youtubeMatch) {
    metadata.thumbnailUrl = `https://img.youtube.com/vi/${youtubeMatch[1]}/maxresdefault.jpg`
    metadata.publisher = 'YouTube'
  }

  return metadata
}

export async function processContent(url: string) {
  const normalizedUrl = normalizeUrl(url)
  const domain = getDomain(url)
  const contentType = getContentType(url)

  const metadata = await extractMetadata(url)

  const title = metadata.title || url
  const category = categorize(title, url)
  const tags = generateTags(title, url)

  return {
    originalUrl: url,
    normalizedUrl,
    sourceDomain: domain,
    contentType,
    title: metadata.title,
    description: metadata.description,
    thumbnailUrl: metadata.thumbnailUrl,
    faviconUrl: metadata.faviconUrl,
    author: metadata.author,
    publisher: metadata.publisher,
    publishedAt: metadata.publishedAt ? new Date(metadata.publishedAt) : null,
    category,
    tags,
    enrichmentStatus: 'completed',
  }
}
