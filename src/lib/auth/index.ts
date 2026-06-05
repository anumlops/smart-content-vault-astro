import { prisma } from '../prisma'

export async function getUserFromSession(sessionId: string) {
  // Better Auth session lookup - simplified for now
  // In production, this would use Better Auth's session verification
  return null
}

export async function hashPassword(password: string): Promise<string> {
  const encoder = new TextEncoder()
  const data = encoder.encode(password + (process.env.AUTH_SECRET || 'default-secret'))
  const hash = await crypto.subtle.digest('SHA-256', data)
  return Array.from(new Uint8Array(hash))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('')
}

export async function verifyPassword(password: string, hash: string): Promise<boolean> {
  const computedHash = await hashPassword(password)
  return computedHash === hash
}

export function createSession(userId: string): string {
  const payload = `${userId}:${Date.now()}:${process.env.AUTH_SECRET || 'default'}`
  const encoded = Buffer.from(payload).toString('base64')
  return encoded
}

export function verifySession(token: string): { userId: string } | null {
  try {
    const decoded = Buffer.from(token, 'base64').toString('utf-8')
    const parts = decoded.split(':')
    if (parts.length < 2) return null
    return { userId: parts[0] }
  } catch {
    return null
  }
}
