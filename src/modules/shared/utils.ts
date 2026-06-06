export function extractDomain(url: string): string {
  try {
    const u = new URL(url)
    return u.hostname.replace(/^www\./, '')
  } catch {
    return url
  }
}

export function validateUrl(url: string): boolean {
  if (!url || !url.trim()) return false
  try {
    const u = new URL(url)
    return u.protocol === 'http:' || u.protocol === 'https:'
  } catch {
    return false
  }
}

export function normalizeUrl(url: string): string {
  url = url.trim()
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    url = 'https://' + url
  }
  try {
    const u = new URL(url)
    u.hash = ''
    if (u.pathname.endsWith('/') && u.pathname.length > 1) {
      u.pathname = u.pathname.slice(0, -1)
    }
    return u.href
  } catch {
    return url
  }
}

export function cleanText(text: string): string {
  return text
    .replace(/\s+/g, ' ')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}

export function truncateText(text: string, maxLength = 500): string {
  if (!text || text.length <= maxLength) return text || ''
  return text.slice(0, maxLength).split(' ').slice(0, -1).join(' ') + '...'
}

export function formatTimestamp(date = new Date()): string {
  return date.toISOString()
}

export function removeStopWords(words: string[]): string[] {
  const stopWords = new Set([
    'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and',
    'or', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'can', 'with', 'without',
    'from', 'by', 'as', 'but', 'not', 'this', 'that', 'these',
    'those', 'it', 'its', 'you', 'your', 'we', 'our', 'they',
    'their', 'he', 'she', 'him', 'her', 'his', 'my', 'me',
    'all', 'some', 'any', 'each', 'every', 'how', 'what', 'why',
    'when', 'where', 'who', 'which', 'get', 'make', 'use',
    'new', 'best', 'top', 'guide', 'ways', 'way',
  ])
  return words.filter((w) => !stopWords.has(w.toLowerCase()) && w.length > 2)
}
