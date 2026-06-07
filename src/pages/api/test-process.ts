import type { APIRoute } from 'astro'
import { WebsiteProcessor } from '../../modules/website/service'

export const POST: APIRoute = async ({ request }) => {
  try {
    const body = await request.json()
    const url = body.url?.toString()
    if (!url) {
      return new Response(JSON.stringify({ error: 'url required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    const processor = new WebsiteProcessor()
    const result = await processor.processUrl(url)

    return new Response(JSON.stringify(result), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    })
  } catch (e: any) {
    return new Response(
      JSON.stringify({ error: e.message || 'Unknown error', stack: e.stack }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    )
  }
}
