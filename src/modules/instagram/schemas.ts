export interface InstagramContent {
  url: string
  domain: string
  title: string | null
  description: string | null
  thumbnail: string | null
  html: string | null
  error?: string | null
}

export interface InstagramAnalysis {
  title: string | null
  description: string | null
  thumbnail: string | null
  summary: string | null
  category: string | null
  tags: string[]
  keyTakeaways: string[]
  error?: string | null
  processedAt: string
}
