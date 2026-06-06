export interface WebsiteContent {
  url: string
  domain: string
  title: string | null
  html: string | null
  text: string | null
  metadata: Record<string, any>
  error?: string | null
}

export interface WebsiteAnalysis {
  title: string | null
  summary: string | null
  category: string | null
  tags: string[]
  keyTakeaways: string[]
  error?: string | null
  processedAt: string
}
