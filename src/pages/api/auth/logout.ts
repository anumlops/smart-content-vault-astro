import type { APIRoute } from 'astro'

export const POST: APIRoute = async ({ redirect, cookies }) => {
  cookies.delete('session', { path: '/' })
  return redirect('/login')
}

export const GET: APIRoute = async ({ redirect, cookies }) => {
  cookies.delete('session', { path: '/' })
  return redirect('/login')
}
