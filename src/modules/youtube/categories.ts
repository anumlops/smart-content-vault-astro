export const YOUTUBE_CATEGORIES = [
  { id: 'life-advice-relationships', label: 'Life Advice & Relationships' },
  { id: 'courses-learning', label: 'Courses & Learning' },
  { id: 'exercise-running', label: 'Exercise & Running' },
] as const

export type YouTubeCategoryId = (typeof YOUTUBE_CATEGORIES)[number]['id']

export function getYouTubeCategoryLabel(id: string): string {
  return YOUTUBE_CATEGORIES.find((c) => c.id === id)?.label || 'Unassigned'
}
