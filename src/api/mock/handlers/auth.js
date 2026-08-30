import { http, HttpResponse } from 'msw'
import { db } from '../db/index.js'

// Simulate token storage: username → token
const tokens = new Map()
let _tokenSeq = 1

function makeToken(userId) {
    const tok = `mock-token-${userId}-${_tokenSeq++}`
    tokens.set(tok, userId)
    return tok
}

export const authHandlers = [

    // POST /api/v1/auth/login/
    http.post('*/auth/login/', async ({ request }) => {
        const { username, password } = await request.json()
        const user = db.users.find(u => u.username === username && u.password === password)
        if (!user) {
            return HttpResponse.json({ detail: 'Invalid credentials.' }, { status: 400 })
        }
        const token = makeToken(user.id)
        const { password: _pw, ...safeUser } = user
        return HttpResponse.json({ token, user: safeUser })
    }),

    // POST /api/v1/auth/logout/
    http.post('*/auth/logout/', ({ request }) => {
        const tok = request.headers.get('Authorization')?.replace('Token ', '')
        if (tok) tokens.delete(tok)
        return HttpResponse.json({ detail: 'Logged out.' })
    }),

    // GET /api/v1/auth/me/
    http.get('*/auth/me/', ({ request }) => {
        const tok = request.headers.get('Authorization')?.replace('Token ', '')
        const userId = tokens.get(tok)
        if (!userId) return HttpResponse.json({ detail: 'Authentication credentials were not provided.' }, { status: 401 })
        const user = db.users.get(userId)
        if (!user) return HttpResponse.json({ detail: 'User not found.' }, { status: 404 })
        const { password: _pw, ...safeUser } = user
        return HttpResponse.json(safeUser)
    }),

    // POST /api/v1/auth/step-up/
    http.post('*/auth/step-up/', async ({ request }) => {
        const { password } = await request.json()
        const tok = request.headers.get('Authorization')?.replace('Token ', '')
        const userId = tokens.get(tok)
        if (!userId) return HttpResponse.json({ detail: 'Not authenticated.' }, { status: 401 })
        const user = db.users.get(userId)
        if (user?.password !== password) {
            return HttpResponse.json({ detail: 'Incorrect password.' }, { status: 400 })
        }
        return HttpResponse.json({ step_up_token: `stepup-${Date.now()}` })
    }),

    // POST /api/v1/auth/change-password/
    http.post('*/auth/change-password/', async ({ request }) => {
        const { old_password, new_password } = await request.json()
        const tok = request.headers.get('Authorization')?.replace('Token ', '')
        const userId = tokens.get(tok)
        const user = db.users.get(userId)
        if (!user || user.password !== old_password) {
            return HttpResponse.json({ detail: 'Old password incorrect.' }, { status: 400 })
        }
        db.users.update(userId, { password: new_password })
        return HttpResponse.json({ detail: 'Password changed.' })
    }),
]
