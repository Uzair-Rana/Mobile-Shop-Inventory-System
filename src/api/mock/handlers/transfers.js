import { http, HttpResponse } from 'msw'
import { db, parsePagination, paginated } from '../db/index.js'

let _txSeq = 100

export const transfersHandlers = [
    http.get('*/transfers/', ({ request }) => {
        const url = new URL(request.url)
        const { page, pageSize } = parsePagination(url)
        const rows = db.transfers.all().sort((a, b) => (b.created_at || '').localeCompare(a.created_at || ''))
        return HttpResponse.json(paginated(rows, page, pageSize))
    }),

    http.get('*/transfers/:id/', ({ params }) => {
        const t = db.transfers.get(params.id)
        if (!t) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(t)
    }),

    http.post('*/transfers/', async ({ request }) => {
        const body = await request.json()
        const t = db.transfers.create({
            transfer_number: `TR-${String(_txSeq++).padStart(4, '0')}`,
            status: 'draft',
            ...body,
        })
        return HttpResponse.json(t, { status: 201 })
    }),

    http.post('*/transfers/:id/dispatch/', ({ params }) => {
        const t = db.transfers.update(params.id, { status: 'dispatched', dispatched_at: new Date().toISOString() })
        if (!t) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(t)
    }),

    http.post('*/transfers/:id/receive/', ({ params }) => {
        const t = db.transfers.update(params.id, { status: 'received', received_at: new Date().toISOString() })
        if (!t) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(t)
    }),
]
