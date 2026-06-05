import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

function toDate(date: unknown): Date | null {
  if (date === undefined || date === null) return null
  if (date instanceof Date) return isNaN(date.getTime()) ? null : date
  if (typeof date === 'string') {
    const d = new Date(date)
    return isNaN(d.getTime()) ? null : d
  }
  return null
}

export function formatRelativeTime(date: unknown): string {
  const target = toDate(date)
  if (!target) return 'Unknown date'
  const now = new Date()
  const diffSecs = Math.floor((now.getTime() - target.getTime()) / 1000)
  if (diffSecs < 60) return 'just now'
  const diffMins = Math.floor(diffSecs / 60)
  if (diffMins < 60) return `${diffMins}m ago`
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 7) return `${diffDays}d ago`
  const diffWeeks = Math.floor(diffDays / 7)
  if (diffWeeks < 4) return `${diffWeeks}w ago`
  const diffMonths = Math.floor(diffDays / 30)
  if (diffMonths < 12) return `${diffMonths}mo ago`
  return target.toLocaleDateString()
}

export function formatDate(date: unknown): string {
  const target = toDate(date)
  if (!target) return 'Unknown date'
  return target.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatDateShort(date: unknown): string {
  const target = toDate(date)
  if (!target) return ''
  return target.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str
  return str.slice(0, length).trimEnd() + '\u2026'
}

export function decodeHtmlEntities(str: string | null | undefined): string {
  if (!str) return ''
  return str
    .replace(/&quot;/g, '\u201c')
    .replace(/&#x27;|&#39;|&#x2019;/g, '\u2019')
    .replace(/&#x201C;/g, '\u201c')
    .replace(/&#x201D;/g, '\u201d')
    .replace(/&#x2013;/g, '\u2013')
    .replace(/&#x2014;/g, '\u2014')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&#(\d+);/g, (_m: string, code: string) => String.fromCharCode(Number(code)))
    .replace(/&#x([0-9a-fA-F]+);/g, (_m: string, code: string) => String.fromCharCode(parseInt(code, 16)))
}

export function getDomain(url: string): string {
  try {
    return new URL(url).hostname.replace('www.', '')
  } catch {
    return url
  }
}

export function normalizeUrl(url: string): string {
  try {
    const u = new URL(url)
    u.hash = ''
    if (u.pathname.endsWith('/')) u.pathname = u.pathname.slice(0, -1)
    return u.href
  } catch {
    return url
  }
}

export function getContentType(url: string): string {
  const domain = getDomain(url)
  if (/youtube\.com|youtu\.be/i.test(domain)) return 'youtube'
  if (/instagram\.com/i.test(domain)) return 'instagram'
  if (/github\.com/i.test(domain)) return 'github'
  if (/medium\.com/i.test(domain)) return 'article'
  if (/dev\.to|hashnode\.com|blog\./i.test(domain)) return 'blog'
  if (/docs\.|documentation/i.test(domain)) return 'documentation'
  return 'website'
}

export function getContentTypeColor(type: string): string {
  const colors: Record<string, string> = {
    youtube: 'text-red-500',
    instagram: 'text-pink-500',
    github: 'text-purple-400',
    article: 'text-emerald-500',
    blog: 'text-orange-500',
    documentation: 'text-sky-400',
    website: 'text-violet-500',
    other: 'text-text-muted',
  }
  return colors[type] || 'text-text-muted'
}

export function getContentTypeIcon(type: string): string {
  const icons: Record<string, string> = {
    youtube: 'youtube',
    instagram: 'instagram',
    github: 'github',
    article: 'article',
    blog: 'blog',
    documentation: 'docs',
    website: 'website',
  }
  return icons[type] || 'link'
}
