import { http, HttpResponse } from 'msw'
import { db, parsePagination, paginated } from '../db/index.js'

let _sessionSeq = 100

export const cashHandlers = [
    // ── Sessions ─────────────────────────────────────────────────────────────
    http.get('*/cash/sessions/current/', () => {
        const open = db.cashSessions.find(s => s.status === 'open')
        return HttpResponse.json(open || null)
    }),

    http.post('*/cash/sessions/open/', async ({ request }) => {
        const body = await request.json()
        const existing = db.cashSessions.find(s => s.status === 'open')
        if (existing) return HttpResponse.json({ detail: 'A session is already open.' }, { status: 400 })
        const s = db.cashSessions.create({
            session_number: `CS-${String(_sessionSeq++).padStart(4, '0')}`,
            status: 'open',
            opening_amount: Number(body.opening_amount) || 0,
            opened_at: new Date().toISOString(),
            ...body,
        })
        return HttpResponse.json(s, { status: 201 })
    }),

    http.post('*/cash/sessions/close/', async ({ request }) => {
        const body = await request.json()
        const open = db.cashSessions.find(s => s.status === 'open')
        if (!open) return HttpResponse.json({ detail: 'No open session.' }, { status: 400 })
        const s = db.cashSessions.update(open.id, {
            status: 'closed',
            closing_amount: Number(body.closing_amount) || 0,
            closed_at: new Date().toISOString(),
            ...body,
        })
        return HttpResponse.json(s)
    }),

    http.post('*/cash/sessions/:id/inflow/', async ({ params, request }) => {
        const body = await request.json()
        const rec = db.cashInflows.create({ session_id: Number(params.id), ...body, created_at: new Date().toISOString() })
        return HttpResponse.json(rec, { status: 201 })
    }),

    http.post('*/cash/sessions/:id/outflow/', async ({ params, request }) => {
        const body = await request.json()
        const rec = db.cashOutflows.create({ session_id: Number(params.id), ...body, created_at: new Date().toISOString() })
        return HttpResponse.json(rec, { status: 201 })
    }),

    // ── Expenses ─────────────────────────────────────────────────────────────
    http.get('*/cash/expenses/', ({ request }) => {
        const url = new URL(request.url)
        const { page, pageSize } = parsePagination(url)
        const status = url.searchParams.get('status') || ''
        let rows = db.expenses.all().sort((a, b) => (b.created_at || '').localeCompare(a.created_at || ''))
        if (status) rows = rows.filter(r => r.status === status)
        return HttpResponse.json(paginated(rows, page, pageSize))
    }),

    http.post('*/cash/expenses/', async ({ request }) => {
        const body = await request.json()
        const e = db.expenses.create({ status: 'pending', created_at: new Date().toISOString(), ...body })
        return HttpResponse.json(e, { status: 201 })
    }),

    http.post('*/cash/expenses/:id/approve/', ({ params }) => {
        const e = db.expenses.update(params.id, { status: 'approved', approved_at: new Date().toISOString() })
        if (!e) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(e)
    }),

    http.patch('*/cash/expenses/:id/', async ({ params, request }) => {
        const body = await request.json()
        const e = db.expenses.update(params.id, body)
        if (!e) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(e)
    }),

    http.delete('*/cash/expenses/:id/', ({ params }) => {
        db.expenses.delete(params.id)
        return new HttpResponse(null, { status: 204 })
    }),
]
