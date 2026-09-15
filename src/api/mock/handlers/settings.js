import { http, HttpResponse } from 'msw'
import { db } from '../db/index.js'

function safeUser(u) {
    if (!u) return u
    const { password, ...rest } = u
    return rest
}

export const settingsHandlers = [
    // ── Company ──────────────────────────────────────────────────────────────
    http.get('*/settings/company/', () => HttpResponse.json(db.company)),
    http.patch('*/settings/company/', async ({ request }) => {
        const body = await request.json()
        Object.assign(db.company, body)
        return HttpResponse.json(db.company)
    }),

    // ── Taxes ────────────────────────────────────────────────────────────────
    http.get('*/settings/taxes/', () => HttpResponse.json(db.taxes.all())),
    http.patch('*/settings/taxes/:id/', async ({ params, request }) => {
        const body = await request.json()
        const t = db.taxes.update(params.id, body)
        if (!t) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(t)
    }),

    // ── Receipt config ───────────────────────────────────────────────────────
    http.get('*/settings/receipt/', () => HttpResponse.json(db.receiptConfig)),
    http.patch('*/settings/receipt/', async ({ request }) => {
        const body = await request.json()
        Object.assign(db.receiptConfig, body)
        return HttpResponse.json(db.receiptConfig)
    }),

    // ── Users ────────────────────────────────────────────────────────────────
    http.get('*/settings/users/', () => HttpResponse.json(db.users.all().map(safeUser))),
    http.get('*/settings/users/:id/', ({ params }) => {
        const u = db.users.get(params.id)
        if (!u) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(safeUser(u))
    }),
    http.post('*/settings/users/', async ({ request }) => {
        const body = await request.json()
        const u = db.users.create({ is_active: true, ...body })
        return HttpResponse.json(safeUser(u), { status: 201 })
    }),
    http.post('*/settings/users/:id/deactivate/', ({ params }) => {
        const u = db.users.update(params.id, { is_active: false })
        if (!u) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(safeUser(u))
    }),
    http.patch('*/settings/users/:id/', async ({ params, request }) => {
        const body = await request.json()
        const u = db.users.update(params.id, body)
        if (!u) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(safeUser(u))
    }),

    // ── Roles ────────────────────────────────────────────────────────────────
    http.get('*/settings/roles/', () => HttpResponse.json(db.roles.all())),
    http.get('*/settings/roles/:id/', ({ params }) => {
        const r = db.roles.get(params.id)
        if (!r) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(r)
    }),
    http.post('*/settings/roles/', async ({ request }) => {
        const body = await request.json()
        const r = db.roles.create(body)
        return HttpResponse.json(r, { status: 201 })
    }),
    http.patch('*/settings/roles/:id/', async ({ params, request }) => {
        const body = await request.json()
        const r = db.roles.update(params.id, body)
        if (!r) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(r)
    }),
]
