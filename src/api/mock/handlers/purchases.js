import { http, HttpResponse } from 'msw'
import { db, searchIn, parsePagination, paginated } from '../db/index.js'

let _poSeq = 100
let _acqSeq = 100

export const purchasesHandlers = [
    // ── Purchase orders ──────────────────────────────────────────────────────
    http.get('*/purchases/orders/', ({ request }) => {
        const url = new URL(request.url)
        const { page, pageSize } = parsePagination(url)
        const q = url.searchParams.get('search') || ''
        let rows = db.purchaseOrders.all().sort((a, b) => (b.created_at || '').localeCompare(a.created_at || ''))
        if (q) rows = searchIn(rows, q, ['order_number', 'supplier_name'])
        return HttpResponse.json(paginated(rows, page, pageSize))
    }),

    http.get('*/purchases/orders/:id/', ({ params }) => {
        const po = db.purchaseOrders.get(params.id)
        if (!po) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json({ ...po, lines: db.poLines?.[Number(params.id)] || po.lines || [] })
    }),

    http.post('*/purchases/orders/', async ({ request }) => {
        const body = await request.json()
        const po = db.purchaseOrders.create({
            order_number: `PO-${String(_poSeq++).padStart(4, '0')}`,
            status: 'draft',
            ...body,
        })
        return HttpResponse.json(po, { status: 201 })
    }),

    http.patch('*/purchases/orders/:id/', async ({ params, request }) => {
        const body = await request.json()
        const po = db.purchaseOrders.update(params.id, body)
        if (!po) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(po)
    }),

    http.post('*/purchases/orders/:id/receive/', async ({ params }) => {
        const po = db.purchaseOrders.update(params.id, { status: 'received', received_at: new Date().toISOString() })
        if (!po) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(po)
    }),

    // ── Acquisitions (used-phone intake) ─────────────────────────────────────
    http.get('*/purchases/acquisitions/', ({ request }) => {
        const url = new URL(request.url)
        const { page, pageSize } = parsePagination(url)
        const rows = (db.acquisitions?.all?.() || [])
        return HttpResponse.json(paginated(rows, page, pageSize))
    }),

    http.post('*/purchases/acquisitions/', async ({ request }) => {
        const body = await request.json()
        // Acquisitions store may not exist; return the echoed record so UI proceeds.
        const rec = { id: _acqSeq++, acquisition_number: `ACQ-${_acqSeq}`, status: 'acquired', ...body }
        return HttpResponse.json(rec, { status: 201 })
    }),

    http.get('*/purchases/acquisitions/:id/', ({ params }) => {
        return HttpResponse.json({ id: Number(params.id) })
    }),
]
