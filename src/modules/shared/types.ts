export const CATEGORIES = [
  'Technology', 'Business', 'Finance', 'Productivity',
  'Education', 'Career', 'Marketing', 'Health',
  'Entertainment', 'Lifestyle',
] as const

export type ContentCategory = (typeof CATEGORIES)[number]

export type EnrichmentStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface ProcessingResult {
  url: string
  domain: string
  title: string | null
  summary: string | null
  category: ContentCategory | null
  tags: string[]
  keyTakeaways: string[]
  extractedText: string | null
  rawContent: string | null
  error: string | null
  status: EnrichmentStatus
  processedAt: string
}

export interface ContentSource {
  url: string
  contentType: string
  rawHtml: string | null
  extractedText: string | null
  metadata: Record<string, any>
}

export interface ContentProcessor {
  sourceType: string
  canHandle(url: string): boolean
  extract(url: string): Promise<ContentSource>
  analyze(source: ContentSource): Promise<ProcessingResult>
}
