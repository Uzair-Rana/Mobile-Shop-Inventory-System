import { http, HttpResponse } from 'msw'
import { db, searchIn, parsePagination, paginated } from '../db/index.js'

export const suppliersHandlers = [
    http.get('*/suppliers/', ({ request }) => {
        const url = new URL(request.url)
        const { page, pageSize } = parsePagination(url)
        const q = url.searchParams.get('search') || url.searchParams.get('q') || ''
        let rows = db.suppliers.all()
        if (q) rows = searchIn(rows, q, ['name', 'phone', 'email', 'company'])
        return HttpResponse.json(paginated(rows, page, pageSize))
    }),

    http.get('*/suppliers/:id/ledger/', ({ params }) => {
        // Minimal ledger placeholder keyed by supplier
        const s = db.suppliers.get(params.id)
        if (!s) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json({ supplier: s, entries: [] })
    }),

    http.get('*/suppliers/:id/', ({ params }) => {
        const s = db.suppliers.get(params.id)
        if (!s) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(s)
    }),

    http.post('*/suppliers/', async ({ request }) => {
        const body = await request.json()
        const s = db.suppliers.create({ outstanding_balance: 0, total_purchased: 0, ...body })
        return HttpResponse.json(s, { status: 201 })
    }),

    http.patch('*/suppliers/:id/', async ({ params, request }) => {
        const body = await request.json()
        const s = db.suppliers.update(params.id, body)
        if (!s) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(s)
    }),
]
