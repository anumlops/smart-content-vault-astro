import type { APIRoute } from 'astro'
import { prisma } from '../../../lib/prisma'
import { verifyPassword, createSession } from '../../../lib/auth'

export const POST: APIRoute = async ({ request, redirect, cookies }) => {
  try {
    const formData = await request.formData()
    const email = formData.get('email')?.toString()
    const password = formData.get('password')?.toString()

    if (!email || !password) {
      return redirect('/login?error=Email and password are required')
    }

    const user = await prisma.user.findUnique({ where: { email } })
    if (!user) {
      return redirect('/login?error=Invalid email or password')
    }

    const valid = await verifyPassword(password, user.password)
    if (!valid) {
      return redirect('/login?error=Invalid email or password')
    }

    const token = createSession(user.id)
    cookies.set('session', token, {
      path: '/',
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 7,
    })

    return redirect('/dashboard')
  } catch {
    return redirect('/login?error=Login failed')
  }
}
