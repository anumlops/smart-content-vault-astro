import type { APIRoute } from 'astro'

export const GET: APIRoute = async () => {
  try {
    const { JSDOM } = await import('jsdom')
    const dom = new JSDOM('<p>hello</p>')
    return new Response(JSON.stringify({
      ok: true,
      text: dom.window.document.body.textContent,
    }), { status: 200, headers: { 'Content-Type': 'application/json' } })
  } catch (e: any) {
    return new Response(JSON.stringify({
      error: e.message,
      name: e.constructor?.name,
    }), { status: 200, headers: { 'Content-Type': 'application/json' } })
  }
}
