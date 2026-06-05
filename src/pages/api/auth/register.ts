import type { APIRoute } from 'astro'
import { prisma } from '../../../lib/prisma'
import { hashPassword } from '../../../lib/auth'

export const POST: APIRoute = async ({ request, redirect }) => {
  try {
    const formData = await request.formData()
    const email = formData.get('email')?.toString()
    const password = formData.get('password')?.toString()
    const name = formData.get('name')?.toString()

    if (!email || !password) {
      return redirect('/register?error=Email and password are required')
    }

    if (password.length < 8) {
      return redirect('/register?error=Password must be at least 8 characters')
    }

    const existing = await prisma.user.findUnique({ where: { email } })
    if (existing) {
      return redirect('/register?error=Email already registered')
    }

    const hashed = await hashPassword(password)
    await prisma.user.create({
      data: { email, password: hashed, name },
    })

    return redirect('/login?registered=true')
  } catch {
    return redirect('/register?error=Registration failed')
  }
}
