export type ContentType = 'youtube' | 'instagram' | 'article' | 'blog' | 'documentation' | 'github' | 'website' | 'other'

export interface SavedContent {
  id: string
  userId: string
  originalUrl: string
  normalizedUrl: string
  sourceDomain: string
  contentType: ContentType
  title: string | null
  description: string | null
  thumbnailUrl: string | null
  faviconUrl: string | null
  author: string | null
  publisher: string | null
  publishedAt: string | null
  category: string | null
  favorite: boolean
  archived: boolean
  createdAt: string
  updatedAt: string
  lastViewedAt: string | null
  viewCount: number
  enrichmentStatus: string
  tags: { id: string; name: string; slug: string }[]
}

export interface CreateContentInput {
  url: string
  note?: string
}

export interface SearchResult {
  content: SavedContent
  score: number
  matchType: 'keyword'
}

export interface DashboardStats {
  totalSaves: number
  categoryDistribution: Record<string, number>
  recentSaves: SavedContent[]
  topTags: { tag: string; count: number }[]
  weeklyActivity: { date: string; count: number }[]
}

export const CATEGORIES = [
  'Programming', 'AI', 'Machine Learning', 'MLOps', 'DevOps',
  'Cloud', 'Data Science', 'Finance', 'Business', 'Productivity',
  'Career', 'Health', 'Fitness', 'Relationships', 'Education',
  'Entertainment', 'Gaming', 'Travel', 'News', 'Other',
] as const

export type Category = (typeof CATEGORIES)[number]

export const CATEGORY_META: Record<string, { emoji: string; color: string }> = {
  Programming: { emoji: '\u2328\uFE0F', color: 'text-blue-400' },
  AI: { emoji: '\uD83E\uDD16', color: 'text-indigo-400' },
  'Machine Learning': { emoji: '\uD83E\uDDE0', color: 'text-purple-400' },
  MLOps: { emoji: '\u2699\uFE0F', color: 'text-cyan-400' },
  DevOps: { emoji: '\uD83D\uDD27', color: 'text-orange-400' },
  Cloud: { emoji: '\u2601\uFE0F', color: 'text-sky-400' },
  'Data Science': { emoji: '\uD83D\uDCCA', color: 'text-teal-400' },
  Finance: { emoji: '\uD83D\uDCB0', color: 'text-emerald-400' },
  Business: { emoji: '\uD83C\uDFED', color: 'text-green-400' },
  Productivity: { emoji: '\uD83D\uDCCB', color: 'text-yellow-400' },
  Career: { emoji: '\uD83D\uDCBC', color: 'text-rose-400' },
  Health: { emoji: '\u2764\uFE0F', color: 'text-red-400' },
  Fitness: { emoji: '\uD83D\uDCAA', color: 'text-lime-400' },
  Relationships: { emoji: '\uD83D\uDC91', color: 'text-pink-400' },
  Education: { emoji: '\uD83C\uDF93', color: 'text-sky-400' },
  Entertainment: { emoji: '\uD83C\uDFAC', color: 'text-fuchsia-400' },
  Gaming: { emoji: '\uD83C\uDFAE', color: 'text-violet-400' },
  Travel: { emoji: '\u2708\uFE0F', color: 'text-amber-400' },
  News: { emoji: '\uD83D\uDCF0', color: 'text-gray-400' },
  Other: { emoji: '\uD83D\uDCCC', color: 'text-text-muted' },
}
