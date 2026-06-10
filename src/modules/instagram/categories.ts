export const INSTAGRAM_CATEGORIES = [
  { id: 'life-advice-relationships', label: 'Life Advice & Relationships' },
  { id: 'courses-learning', label: 'Courses & Learning' },
  { id: 'exercise-running', label: 'Exercise & Running' },
] as const

export type InstagramCategoryId = (typeof INSTAGRAM_CATEGORIES)[number]['id']

export function getCategoryLabel(id: string): string {
  return INSTAGRAM_CATEGORIES.find((c) => c.id === id)?.label || 'Unassigned'
}
