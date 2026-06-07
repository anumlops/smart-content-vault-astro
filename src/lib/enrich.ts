import { prisma } from './prisma'
import { WebsiteProcessor } from '../modules/website/service'

export async function enrichContent(contentId: string, url: string): Promise<void> {
  try {
    await prisma.savedContent.update({
      where: { id: contentId },
      data: { enrichmentStatus: 'processing' },
    })

    const processor = new WebsiteProcessor()
    const result = await processor.processUrl(url)

    await prisma.savedContent.update({
      where: { id: contentId },
      data: {
        title: result.title || undefined,
        description: result.summary || undefined,
        category: result.category || undefined,
        aiSummary: result.summary,
        aiTags: JSON.stringify(result.tags),
        aiCategory: result.category,
        keyTakeaways: JSON.stringify(result.keyTakeaways),
        enrichmentStatus: result.status,
        extractedText: result.extractedText,
        rawContent: result.rawContent,
        processingVersion: { increment: 1 },
      },
    })

    for (const tagName of result.tags) {
      const slug = tagName.toLowerCase().replace(/[^a-z0-9-]/g, '')
      const tag = await prisma.tag.upsert({
        where: { slug },
        update: {},
        create: { name: tagName, slug },
      })
      await prisma.contentTag.upsert({
        where: { contentId_tagId: { contentId, tagId: tag.id } },
        update: {},
        create: { contentId, tagId: tag.id },
      }).catch(() => {})
    }
  } catch {
    await prisma.savedContent.update({
      where: { id: contentId },
      data: { enrichmentStatus: 'failed' },
    }).catch(() => {})
  }
}
