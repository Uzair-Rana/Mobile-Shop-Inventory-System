import { http, HttpResponse } from 'msw'
import { db, searchIn, parsePagination, paginated } from '../db/index.js'

export const installmentsHandlers = [

    http.get('*/installments/plans/', ({ request }) => {
        const url = new URL(request.url)
        const { page, pageSize } = parsePagination(url)
        const q = url.searchParams.get('search') || ''
        const status = url.searchParams.get('status') || ''
        let rows = db.plans.all().sort((a, b) => b.created_at.localeCompare(a.created_at))
        if (status) rows = rows.filter(r => r.status === status)
        if (q) rows = searchIn(rows, q, ['plan_number', 'customer_name'])
        return HttpResponse.json(paginated(rows, page, pageSize))
    }),

    http.get('*/installments/overdue/', ({ request }) => {
        const url = new URL(request.url)
        const { page, pageSize } = parsePagination(url)
        const rows = db.plans.list(p => p.status === 'overdue')
        return HttpResponse.json(paginated(rows, page, pageSize))
    }),

    http.get('*/installments/plans/:id/', ({ params }) => {
        const plan = db.plans.get(params.id)
        if (!plan) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json({ ...plan, schedule: db.schedules[Number(params.id)] || [] })
    }),

    http.post('*/installments/plans/', async ({ request }) => {
        const body = await request.json()
        const num = `PLAN-${String(db.plans.count() + 1).padStart(4, '0')}`
        const plan = db.plans.create({ ...body, plan_number: num, status: 'active' })
        return HttpResponse.json(plan, { status: 201 })
    }),

    http.post('*/installments/plans/:id/record_payment/', async ({ params, request }) => {
        const body = await request.json()
        const plan = db.plans.get(params.id)
        if (!plan) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        const updated = db.plans.update(params.id, {
            amount_paid: (plan.amount_paid || 0) + body.amount,
            updated_at: new Date().toISOString(),
        })
        return HttpResponse.json(updated)
    }),
]
