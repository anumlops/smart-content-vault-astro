import type { ContentProcessor, ContentSource, ProcessingResult } from '../shared/types'
import type { EnrichmentStatus } from '../shared/types'
import { extractDomain, validateUrl } from '../shared/utils'
import { InstagramCrawler } from './crawler'
import { INSTAGRAM_CATEGORIES } from './categories'

export class InstagramProcessor implements ContentProcessor {
  sourceType = 'instagram'

  private crawler = new InstagramCrawler()

  canHandle(url: string): boolean {
    return this.crawler.canHandle(url)
  }

  async extract(url: string): Promise<ContentSource> {
    if (!validateUrl(url)) throw new Error(`Invalid URL: ${url}`)

    const result = await this.crawler.extract(url)

    return {
      url: result.url,
      contentType: 'instagram',
      rawHtml: result.html,
      extractedText: (result.title || '') + ' ' + (result.description || ''),
      metadata: {
        title: result.title,
        domain: result.domain,
        description: result.description,
        thumbnail: result.thumbnail,
      },
    }
  }

  async analyze(source: ContentSource): Promise<ProcessingResult> {
    const title = source.metadata.title || null
    const description = source.metadata.description || null
    const thumbnail = source.metadata.thumbnail || null
    const domain = source.metadata.domain || extractDomain(source.url)

    return {
      url: source.url,
      domain,
      title,
      summary: description,
      category: null,
      tags: [],
      keyTakeaways: [],
      extractedText: source.extractedText,
      rawContent: source.rawHtml,
      error: null,
      status: 'completed' as EnrichmentStatus,
      processedAt: new Date().toISOString(),
    }
  }

  async processUrl(url: string): Promise<ProcessingResult> {
    try {
      const source = await this.extract(url)
      return await this.analyze(source)
    } catch (err: any) {
      return {
        url,
        domain: extractDomain(url),
        title: null,
        summary: null,
        category: null,
        tags: [],
        keyTakeaways: [],
        extractedText: null,
        rawContent: null,
        error: err.message || 'Processing failed',
        status: 'failed' as EnrichmentStatus,
        processedAt: new Date().toISOString(),
      }
    }
  }
}
