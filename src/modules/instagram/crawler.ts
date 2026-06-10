import { extractDomain, validateUrl } from '../shared/utils'
import { decodeHtmlEntities } from '../../lib/utils'
import type { InstagramContent } from './schemas'

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

export class InstagramCrawler {
  canHandle(url: string): boolean {
    return /instagram\.com\/(reel|p)\//i.test(url)
  }

  async extract(url: string): Promise<InstagramContent> {
    if (!validateUrl(url)) {
      return { url, domain: extractDomain(url), title: null, description: null, thumbnail: null, html: null, error: 'Invalid URL' }
    }

    const domain = extractDomain(url)

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

      if (!response.ok) {
        return { url, domain, title: null, description: null, thumbnail: null, html: null, error: `Failed to fetch: ${response.status}` }
      }

      const html = await response.text()
      if (!html) {
        return { url, domain, title: null, description: null, thumbnail: null, html: null, error: 'Empty response' }
      }

      const thumbnail = extractMetaContent(html, 'og:image')

      return {
        url,
        domain,
        title: extractMetaContent(html, 'og:title') || null,
        description: extractMetaContent(html, 'og:description') || null,
        thumbnail: isValidImageUrl(thumbnail) ? thumbnail : null,
        html,
      }
    } catch (err: any) {
      return {
        url,
        domain,
        title: null,
        description: null,
        thumbnail: null,
        html: null,
        error: err.name === 'AbortError' ? 'Request timed out' : `Extraction failed: ${err.message}`,
      }
    }
  }
}
