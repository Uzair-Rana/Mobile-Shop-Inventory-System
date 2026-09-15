import { http, HttpResponse } from 'msw'
import { db, searchIn, parsePagination, paginated } from '../db/index.js'

export const customersHandlers = [

    // Customer quick-search (used by POS) — matches name, phone, cnic, email.
    // NOTE: must be registered BEFORE '*/customers/:id/' so 'search' isn't
    // captured as an :id param.
    http.get('*/customers/search/', ({ request }) => {
        const url = new URL(request.url)
        const q = url.searchParams.get('q') || url.searchParams.get('search') || ''
        let rows = db.customers.all()
        if (q) rows = searchIn(rows, q, ['name', 'phone', 'cnic', 'email'])
        return HttpResponse.json({ results: rows.slice(0, 10) })
    }),

    // Customer list (paginated + optional search)
    http.get('*/customers/', ({ request }) => {
        const url = new URL(request.url)
        const { page, pageSize } = parsePagination(url)
        const q = url.searchParams.get('search') || url.searchParams.get('q') || ''
        let rows = db.customers.all()
        if (q) rows = searchIn(rows, q, ['name', 'phone', 'cnic', 'email'])
        return HttpResponse.json(paginated(rows, page, pageSize))
    }),

    http.get('*/customers/:id/', ({ params }) => {
        const c = db.customers.get(params.id)
        if (!c) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(c)
    }),

    http.post('*/customers/', async ({ request }) => {
        const body = await request.json()
        const c = db.customers.create({
            outstanding_balance: 0, total_spent: 0, invoice_count: 0, repair_count: 0,
            ...body,
        })
        return HttpResponse.json(c, { status: 201 })
    }),

    http.patch('*/customers/:id/', async ({ params, request }) => {
        const body = await request.json()
        const c = db.customers.update(params.id, body)
        if (!c) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(c)
    }),
]
