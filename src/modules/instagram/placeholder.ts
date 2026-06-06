import type { ContentProcessor, ContentSource, ProcessingResult } from '../shared/types'

export class InstagramProcessor implements ContentProcessor {
  sourceType = 'instagram'

  canHandle(url: string): boolean {
    return /instagram\.com/i.test(url)
  }

  async extract(_url: string): Promise<ContentSource> {
    throw new Error('Instagram processing not yet implemented')
  }

  async analyze(_source: ContentSource): Promise<ProcessingResult> {
    throw new Error('Instagram processing not yet implemented')
  }
}
