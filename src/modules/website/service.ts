import type { ContentProcessor, ContentSource, ProcessingResult } from '../shared/types'
import type { ContentCategory, EnrichmentStatus } from '../shared/types'
import { extractDomain, validateUrl } from '../shared/utils'
import { WebsiteCrawler } from './crawler'
import { WebsiteAnalyzer } from './analyzer'

export class WebsiteProcessor implements ContentProcessor {
  sourceType = 'website'

  private crawler = new WebsiteCrawler()
  private analyzer = new WebsiteAnalyzer()

  canHandle(url: string): boolean {
    return this.crawler.canHandle(url)
  }

  async extract(url: string): Promise<ContentSource> {
    if (!validateUrl(url)) throw new Error(`Invalid URL: ${url}`)

    const result = await this.crawler.extract(url)

    return {
      url: result.url,
      contentType: 'website',
      rawHtml: result.html,
      extractedText: result.text,
      metadata: {
        title: result.title,
        domain: result.domain,
        ...result.metadata,
      },
    }
  }

  async analyze(source: ContentSource): Promise<ProcessingResult> {
    const websiteContent = {
      url: source.url,
      domain: source.metadata.domain || extractDomain(source.url),
      title: source.metadata.title || null,
      html: source.rawHtml,
      text: source.extractedText,
      metadata: source.metadata,
    }

    const analysis = await this.analyzer.analyze(websiteContent)

    if (analysis.error) {
      return {
        url: source.url,
        domain: extractDomain(source.url),
        title: analysis.title || source.metadata.title || null,
        summary: null,
        category: null,
        tags: [],
        keyTakeaways: [],
        extractedText: source.extractedText,
        rawContent: source.rawHtml,
        error: analysis.error,
        status: 'failed' as EnrichmentStatus,
        processedAt: new Date().toISOString(),
      }
    }

    return {
      url: source.url,
      domain: extractDomain(source.url),
      title: analysis.title || source.metadata.title || null,
      summary: analysis.summary || null,
      category: (analysis.category as ContentCategory) || null,
      tags: analysis.tags || [],
      keyTakeaways: analysis.keyTakeaways || [],
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
