import { parseHTML } from 'linkedom'
import { Readability } from '@mozilla/readability'

import { extractDomain, validateUrl } from '../shared/utils'
import type { WebsiteContent } from './schemas'

export class WebsiteCrawler {
  canHandle(url: string): boolean {
    return validateUrl(url)
  }

  async extract(url: string): Promise<WebsiteContent> {
    if (!validateUrl(url)) {
      return {
        url,
        domain: extractDomain(url),
        title: null,
        html: null,
        text: null,
        metadata: {},
        error: `Invalid URL: ${url}`,
      }
    }

    const domain = extractDomain(url)

    try {
      const controller = new AbortController()
      const timeout = setTimeout(() => controller.abort(), 15000)

      const response = await fetch(url, {
        signal: controller.signal,
        headers: {
          'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          Accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        },
      })
      clearTimeout(timeout)

      if (!response.ok) {
        return {
          url,
          domain,
          title: null,
          html: null,
          text: null,
          metadata: {},
          error: `Failed to fetch: ${response.status} ${response.statusText}`,
        }
      }

      const html = await response.text()

      const { document } = parseHTML(html)
      const reader = new Readability(document)
      const article = reader.parse()

      const title =
        article?.title ||
        document.querySelector('title')?.textContent ||
        document.querySelector('h1')?.textContent ||
        null

      const text = article?.textContent?.trim() || null
      const content = article?.content || null

      const metadata: Record<string, any> = {}
      const ogTitle = html.match(
        /<meta[^>]+property=["']og:title["'][^>]+content=["']([^"']*)["']/i
      )
      if (ogTitle) metadata.ogTitle = ogTitle[1]

      const ogDesc = html.match(
        /<meta[^>]+property=["']og:description["'][^>]+content=["']([^"']*)["']/i
      )
      if (ogDesc) metadata.ogDescription = ogDesc[1]

      const ogImage = html.match(
        /<meta[^>]+property=["']og:image["'][^>]+content=["']([^"']*)["']/i
      )
      if (ogImage) metadata.ogImage = ogImage[1]

      const author = html.match(
        /<meta[^>]+name=["']author["'][^>]+content=["']([^"']*)["']/i
      )
      if (author) metadata.author = author[1]

      if (!text || text.length < 50) {
        return {
          url,
          domain,
          title,
          html,
          text,
          metadata,
          error: 'Insufficient content extracted',
        }
      }

      return {
        url,
        domain,
        title,
        html,
        text,
        metadata,
      }
    } catch (err: any) {
      return {
        url,
        domain,
        title: null,
        html: null,
        text: null,
        metadata: {},
        error: err.name === 'AbortError' ? 'Request timed out' : `Extraction failed: ${err.message}`,
      }
    }
  }
}
