import { CATEGORY_KEYWORDS, TAG_MIN_COUNT, TAG_MAX_COUNT, TAKEAWAY_MAX_COUNT } from '../shared/constants'
import { cleanText, removeStopWords } from '../shared/utils'
import type { WebsiteContent, WebsiteAnalysis } from './schemas'

const OPENROUTER_BASE = 'https://openrouter.ai/api/v1/chat/completions'
const DEEPSEEK_MODEL = 'deepseek/deepseek-chat'
const KIMI_MODEL = 'moonshotai/kimi-k2.6'

const ANALYSIS_PROMPT = `You are a content analysis engine.

Analyze the provided content.

Generate:

1. Summary under 500 words.
2. Exactly 5 relevant tags.

Tag Rules:

- lowercase
- concise
- searchable
- no duplicates

Return ONLY valid JSON.

Required Format:

{
  "summary": "",
  "tags": []
}

Content:

{content}`

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

  private async callOpenRouter(model: string, text: string, title?: string): Promise<string | null> {
    const apiKey = process.env.LLM_API_KEY
    if (!apiKey) return null

    const promptText = text.slice(0, 3000)
    let prompt = ANALYSIS_PROMPT.replace('{content}', promptText)
    if (title) prompt += `\n\nThe page title is: ${title}`

    try {
      const controller = new AbortController()
      const timeout = setTimeout(() => controller.abort(), 9000)

      const response = await fetch(OPENROUTER_BASE, {
        signal: controller.signal,
        method: 'POST',
        headers: {
          Authorization: `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model,
          messages: [{ role: 'user', content: prompt }],
          max_tokens: 500,
          temperature: 0.1,
        }),
      })
      clearTimeout(timeout)

      if (response.status === 429) return null
      if (!response.ok) return null

      const data = await response.json()
      const msg = data.choices?.[0]?.message
      return msg?.content || msg?.reasoning || null
    } catch {
      return null
    }
  }

  private parseLLMResponse(raw: string): { summary: string; tags: string[] } | null {
    let text = raw.trim()
    if (text.startsWith('```json')) text = text.slice(7)
    else if (text.startsWith('```')) text = text.slice(3)
    if (text.endsWith('```')) text = text.slice(0, -3)
    text = text.trim()

    try {
      const parsed = JSON.parse(text)
      if (!parsed || typeof parsed !== 'object') return null

      const summary = parsed.summary
      if (typeof summary !== 'string' || !summary.trim()) return null
      if (summary.split(/\s+/).length > 500) return null

      const tags = parsed.tags
      if (!Array.isArray(tags)) return null
      if (tags.length !== 5) return null

      const validatedTags: string[] = []
      const seen = new Set<string>()
      for (const tag of tags) {
        if (typeof tag !== 'string' || !tag.trim()) return null
        const lower = tag.toLowerCase().trim()
        if (seen.has(lower)) return null
        seen.add(lower)
        validatedTags.push(lower)
      }

      return { summary: summary.trim(), tags: validatedTags }
    } catch {
      return null
    }
  }

  private async tryLlmAnalysis(content: WebsiteContent): Promise<WebsiteAnalysis | null> {
    const text = content.text || ''
    if (!text) return null

    const title = content.title || undefined

    for (const { model, label } of [
      { model: DEEPSEEK_MODEL, label: 'DeepSeek' },
      { model: KIMI_MODEL, label: 'Kimi' },
    ]) {
      const raw = await this.callOpenRouter(model, text, title)
      if (!raw) continue

      const parsed = this.parseLLMResponse(raw)
      if (!parsed) continue

      return {
        title: content.title || null,
        summary: parsed.summary,
        category: this.detectCategory(content),
        tags: parsed.tags,
        keyTakeaways: this.generateTakeaways(text),
        processedAt: new Date().toISOString(),
      }
    }

    return null
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

    const domainTag = domain.split('.')[0]
    if (domainTag && domainTag.length > 2) {
      tagSet.add(domainTag)
    }

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
}
