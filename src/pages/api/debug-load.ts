import type { APIRoute } from 'astro'

export const GET: APIRoute = async () => {
  try {
    const { WebsiteProcessor } = await import('../../modules/website/service')
    return new Response(JSON.stringify({ ok: true, hasProcessor: !!WebsiteProcessor }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    })
  } catch (e: any) {
    return new Response(
      JSON.stringify({ error: e.message, stack: e.stack?.split('\n').slice(0, 5) }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    )
  }
}
