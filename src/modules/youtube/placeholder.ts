import type { ContentProcessor, ContentSource, ProcessingResult } from '../shared/types'

export class YouTubeProcessor implements ContentProcessor {
  sourceType = 'youtube'

  canHandle(url: string): boolean {
    return /youtube\.com|youtu\.be/i.test(url)
  }

  async extract(_url: string): Promise<ContentSource> {
    throw new Error('YouTube processing not yet implemented')
  }

  async analyze(_source: ContentSource): Promise<ProcessingResult> {
    throw new Error('YouTube processing not yet implemented')
  }
}
