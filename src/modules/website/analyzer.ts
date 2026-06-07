import { CATEGORY_KEYWORDS, TAG_MIN_COUNT, TAG_MAX_COUNT, TAKEAWAY_MAX_COUNT } from '../shared/constants'
import { cleanText, removeStopWords } from '../shared/utils'
import type { WebsiteContent, WebsiteAnalysis } from './schemas'
import { buildUserPrompt, SYSTEM_PROMPT } from './prompts'

export class WebsiteAnalyzer {
  async analyze(content: WebsiteContent): Promise<WebsiteAnalysis> {
    if (content.error && !content.text) {
      return {
        title: content.title,
        summary: null,
        category: null,
        tags: [],
        keyTakeaways: [],
        error: content.error,
        processedAt: new Date().toISOString(),
      }
    }

    const text = content.text || ''
    const llmResult = await this.tryLlmAnalysis(content)
    if (llmResult) return llmResult

    return this.keywordFallback(content, text)
  }

  private async tryLlmAnalysis(content: WebsiteContent): Promise<WebsiteAnalysis | null> {
    const text = (content.text || '').slice(0, 8000)
    if (!text) return null

    const microserviceUrl = process.env.AI_MICROSERVICE_URL
    if (microserviceUrl) {
      try {
        const controller = new AbortController()
        const timeout = setTimeout(() => controller.abort(), 60000)
        const response = await fetch(`${microserviceUrl}/api/v1/analyze-llm`, {
          signal: controller.signal,
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title: content.title, content: text }),
        })
        clearTimeout(timeout)
        if (response.ok) {
          const data = await response.json()
          return {
            title: content.title || null,
            summary: data.summary || null,
            category: this.detectCategory(content),
            tags: Array.isArray(data.tags) ? data.tags.slice(0, 5) : [],
            keyTakeaways: this.generateTakeaways(text),
            processedAt: new Date().toISOString(),
          }
        }
      } catch {
        // fall through to direct LLM
      }
    }

    const apiKey = process.env.LLM_API_KEY
    const apiUrl = process.env.LLM_API_URL || 'https://api.openai.com/v1/chat/completions'
    const model = process.env.LLM_MODEL || 'gpt-4o-mini'
    if (!apiKey) return null

    const userPrompt = buildUserPrompt(content.title, content.domain, content.url, text)
    try {
      const controller = new AbortController()
      const timeout = setTimeout(() => controller.abort(), 30000)
      const response = await fetch(apiUrl, {
        signal: controller.signal,
        method: 'POST',
        headers: {
          Authorization: `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model,
          messages: [
            { role: 'system', content: SYSTEM_PROMPT },
            { role: 'user', content: userPrompt },
          ],
          temperature: 0.3,
          max_tokens: 1000,
          response_format: { type: 'json_object' },
        }),
      })
      clearTimeout(timeout)
      if (!response.ok) return null
      const data = await response.json()
      const raw = data.choices?.[0]?.message?.content
      if (!raw) return null
      return this.parseAndValidate(raw, content)
    } catch {
      return null
    }
  }

  private parseAndValidate(raw: string, content: WebsiteContent): WebsiteAnalysis {
    try {
      const cleaned = raw.replace(/^```(?:json)?\s*/, '').replace(/\s*```$/, '')
      const parsed = JSON.parse(cleaned)

      const category = this.validateCategory(parsed.category) ? parsed.category : this.detectCategory(content)
      const tags = this.validateTags(parsed.tags)
      const takeaways = this.validateTakeaways(parsed.key_takeaways)

      return {
        title: parsed.title || content.title,
        summary: parsed.summary || null,
        category,
        tags,
        keyTakeaways: takeaways,
        processedAt: new Date().toISOString(),
      }
    } catch {
      return this.keywordFallback(content, content.text || '')
    }
  }

  private keywordFallback(content: WebsiteContent, text: string): WebsiteAnalysis {
    const title = content.title || this.extractTitleFromText(text) || null
    const category = content.metadata?.ogTitle
      ? this.detectCategory({ ...content, title: content.metadata.ogTitle })
      : this.detectCategory(content)
    const tags = this.generateTags(title, text, content.domain)
    const summary = this.generateSummary(text, title)
    const takeaways = this.generateTakeaways(text)

    return {
      title,
      summary,
      category,
      tags,
      keyTakeaways: takeaways,
      processedAt: new Date().toISOString(),
    }
  }

  private detectCategory(content: { title?: string | null; domain?: string; text?: string | null }): string | null {
    const text = [
      content.title || '',
      content.domain || '',
      (content.text || '').slice(0, 2000),
    ].join(' ').toLowerCase()

    let bestCategory: string | null = null
    let bestScore = 0

    for (const [category, keywords] of Object.entries(CATEGORY_KEYWORDS)) {
      let score = 0
      for (const kw of keywords) {
        if (text.includes(kw.toLowerCase())) {
          score++
          // Boost if keyword is in the title
          if ((content.title || '').toLowerCase().includes(kw.toLowerCase())) {
            score += 2
          }
        }
      }
      if (score > bestScore) {
        bestScore = score
        bestCategory = category
      }
    }

    return bestCategory || 'Technology'
  }

  private validateCategory(cat: string): boolean {
    const valid = ['Technology', 'Business', 'Finance', 'Productivity',
      'Education', 'Career', 'Marketing', 'Health', 'Entertainment', 'Lifestyle']
    return valid.includes(cat)
  }

  private extractTitleFromText(text: string): string | null {
    const lines = text.split('\n').filter((l) => l.trim().length > 10)
    return lines[0]?.trim().slice(0, 200) || null
  }

  private generateTags(title: string | null, text: string, domain: string): string[] {
    const tagSet = new Set<string>()

    const source = [title || '', text.slice(0, 3000)].join(' ')
    const words = source
      .toLowerCase()
      .split(/[\s,;.:()\-–—/\\|!?]+/)
      .map((w) => w.replace(/[^a-z0-9]/g, '').trim())
      .filter((w) => w.length > 2)

    const significant = removeStopWords(words)

    for (const word of significant.slice(0, 30)) {
      if (tagSet.size >= TAG_MAX_COUNT) break
      tagSet.add(word)
    }

    // Add domain tag
    const domainTag = domain.split('.')[0]
    if (domainTag && domainTag.length > 2) {
      tagSet.add(domainTag)
    }

    // Detect multi-word tech terms
    const lower = source.toLowerCase()
    const phrases = ['machine learning', 'artificial intelligence', 'data science',
      'web development', 'software engineering', 'project management',
      'digital marketing', 'social media', 'cloud computing', 'deep learning']
    for (const phrase of phrases) {
      if (lower.includes(phrase)) {
        tagSet.add(phrase.replace(/\s+/g, '-'))
      }
      if (tagSet.size >= TAG_MAX_COUNT) break
    }

    const result = Array.from(tagSet).slice(0, TAG_MAX_COUNT)
    if (result.length < TAG_MIN_COUNT) {
      result.push('technology', 'article')
    }

    return result.slice(0, TAG_MAX_COUNT)
  }

  private generateSummary(text: string, title: string | null): string | null {
    if (!text) return null

    const cleaned = cleanText(text)
    const sentences = cleaned.match(/[^.!?]+[.!?]+/g)
    if (!sentences) return cleaned.slice(0, 300) + (cleaned.length > 300 ? '...' : '')

    const first = sentences[0]?.trim() || ''
    const second = sentences[1]?.trim() || ''

    let summary = first
    if (second && summary.length + second.length < 400) {
      summary += ' ' + second
    }

    return summary.length > 500 ? summary.slice(0, 497) + '...' : summary
  }

  private generateTakeaways(text: string): string[] {
    if (!text) return []

    const cleaned = cleanText(text)
    const sentences = cleaned.match(/[^.!?]+[.!?]+/g)
    if (!sentences) return []

    const significant = sentences
      .map((s) => s.trim())
      .filter((s) => s.length > 40 && s.length < 300)

    return significant.slice(0, TAKEAWAY_MAX_COUNT)
  }

  private validateTags(tags: any): string[] {
    if (!Array.isArray(tags)) return []
    const seen = new Set<string>()
    return tags
      .filter((t): t is string => typeof t === 'string' && t.trim().length > 0)
      .map((t) => t.toLowerCase().trim())
      .filter((t) => {
        if (seen.has(t)) return false
        seen.add(t)
        return true
      })
      .slice(0, TAG_MAX_COUNT)
  }

  private validateTakeaways(takeaways: any): string[] {
    if (!Array.isArray(takeaways)) return []
    return takeaways
      .filter((t): t is string => typeof t === 'string' && t.trim().length > 0)
      .map((t) => t.trim())
      .slice(0, TAKEAWAY_MAX_COUNT)
  }
}
