function getDomain(url: string): string {
  try {
    return new URL(url).hostname.replace('www.', '')
  } catch {
    return url
  }
}

const stopWords = new Set([
  'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and',
  'or', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
  'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
  'could', 'should', 'may', 'might', 'shall', 'can', 'need',
  'with', 'without', 'from', 'by', 'as', 'but', 'not', 'no',
  'this', 'that', 'these', 'those', 'it', 'its', 'you', 'your',
  'we', 'our', 'they', 'their', 'he', 'she', 'him', 'her',
  'his', 'my', 'me', 'all', 'some', 'any', 'each', 'every',
  'how', 'what', 'why', 'when', 'where', 'who', 'which',
  'get', 'got', 'make', 'made', 'use', 'used', 'using',
  'new', 'best', 'top', 'guide', 'tips', 'ways', 'way',
  'vs', 'v/s', 'via', 'de', 'la', 'le', 'en', 'el',
  'tutorial', 'beginner', 'advanced', 'introduction', 'overview',
  'complete', 'ultimate', 'simple', 'easy', 'fast', 'quick',
  'learn', 'how-to', 'step-by-step', 'part', 'series',
])

function normalizeTag(word: string): string {
  return word
    .toLowerCase()
    .replace(/[^a-z0-9-]/g, '')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
    .trim()
}

function extractMultiWordTerms(title: string): string[] {
  const terms: string[] = []
  const lower = title.toLowerCase()

  const patterns = [
    /machine learning/g, /deep learning/g, /data science/g,
    /artificial intelligence/g, /computer vision/g, /natural language/g,
    /prompt engineering/g, /software engineering/g, /data structure/g,
    /design pattern/g, /cloud computing/g, /web development/g,
    /mobile development/g, /full stack/g, /frontend|front-end/g,
    /backend|back-end/g, /reinforcement learning/g, /transfer learning/g,
    /continuous integration/g, /continuous deployment/g,
    /project management/g, /time management/g, /personal finance/g,
    /mental health/g, /strength training/g, /weight training/g,
    /video game/g, /open world/g, /battle royale/g,
  ]

  for (const pattern of patterns) {
    const match = lower.match(pattern)
    if (match) {
      terms.push(match[0].replace(/\s+/g, '-'))
    }
  }

  return terms
}

export function generateTags(title: string, url: string): string[] {
  const tags = new Set<string>()
  const domain = getDomain(url)

  const multiWord = extractMultiWordTerms(title)
  for (const term of multiWord) {
    if (term.length > 1) tags.add(term)
  }

  const words = title
    .toLowerCase()
    .split(/[\s,;:()\-–—/\\|]+/)
    .map(normalizeTag)
    .filter((w) => w.length > 2)

  for (const word of words) {
    if (!stopWords.has(word) && word.length >= 3) {
      tags.add(word)
    }
  }

  const domainTag = domain.split('.')[0]
  if (domainTag && domainTag.length > 2) {
    tags.add(domainTag)
  }

  return Array.from(tags).slice(0, 5)
}
