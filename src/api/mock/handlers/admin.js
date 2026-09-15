import { http, HttpResponse } from 'msw'
import { db, parsePagination, paginated } from '../db/index.js'

function safeUser(u) {
    if (!u) return u
    const { password, ...rest } = u
    return rest
}

export const adminHandlers = [
    // ── Users ────────────────────────────────────────────────────────────────
    http.get('*/admin/users/', () => HttpResponse.json(db.users.all().map(safeUser))),
    http.get('*/admin/users/:id/', ({ params }) => {
        const u = db.users.get(params.id)
        if (!u) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(safeUser(u))
    }),
    http.post('*/admin/users/', async ({ request }) => {
        const body = await request.json()
        const u = db.users.create({ is_active: true, ...body })
        return HttpResponse.json(safeUser(u), { status: 201 })
    }),
    http.post('*/admin/users/:id/deactivate/', ({ params }) => {
        const u = db.users.update(params.id, { is_active: false })
        if (!u) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(safeUser(u))
    }),
    http.patch('*/admin/users/:id/', async ({ params, request }) => {
        const body = await request.json()
        const u = db.users.update(params.id, body)
        if (!u) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(safeUser(u))
    }),

    // ── Roles ────────────────────────────────────────────────────────────────
    http.get('*/admin/roles/', () => HttpResponse.json(db.roles.all())),
    http.get('*/admin/roles/:id/', ({ params }) => {
        const r = db.roles.get(params.id)
        if (!r) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(r)
    }),
    http.post('*/admin/roles/', async ({ request }) => {
        const body = await request.json()
        const r = db.roles.create(body)
        return HttpResponse.json(r, { status: 201 })
    }),
    http.patch('*/admin/roles/:id/', async ({ params, request }) => {
        const body = await request.json()
        const r = db.roles.update(params.id, body)
        if (!r) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(r)
    }),

    // ── Audit log ────────────────────────────────────────────────────────────
    http.get('*/admin/audit-log/', ({ request }) => {
        const url = new URL(request.url)
        const { page, pageSize } = parsePagination(url)
        const rows = db.auditLogs.all().sort((a, b) => (b.timestamp || '').localeCompare(a.timestamp || ''))
        return HttpResponse.json(paginated(rows, page, pageSize))
    }),
]
