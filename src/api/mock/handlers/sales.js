import { http, HttpResponse } from 'msw'
import { db, searchIn, parsePagination, paginated } from '../db/index.js'

let _invSeq = 11

export const salesHandlers = [

    http.get('*/sales/invoices/', ({ request }) => {
        const url = new URL(request.url)
        const { page, pageSize } = parsePagination(url)
        const q = url.searchParams.get('search') || ''
        const status = url.searchParams.get('status') || ''
        const from = url.searchParams.get('date_from') || ''
        const to = url.searchParams.get('date_to') || ''
        let rows = db.invoices.all().sort((a, b) => b.created_at.localeCompare(a.created_at))
        if (status) rows = rows.filter(r => r.status === status)
        if (q) rows = searchIn(rows, q, ['invoice_number', 'customer_name'])
        if (from) rows = rows.filter(r => r.created_at >= from)
        if (to) rows = rows.filter(r => r.created_at <= to + 'T23:59:59Z')
        return HttpResponse.json(paginated(rows, page, pageSize))
    }),

    http.get('*/sales/invoices/:id/', ({ params }) => {
        const inv = db.invoices.get(params.id)
        if (!inv) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json({ ...inv, lines: db.invoiceLines[Number(params.id)] || [] })
    }),

    http.post('*/sales/invoices/', async ({ request }) => {
        const body = await request.json()
        const num = `INV-${String(_invSeq++).padStart(4, '0')}`
        const inv = db.invoices.create({ ...body, invoice_number: num, status: 'draft', amount_paid: 0, balance_due: body.grand_total ?? 0 })
        return HttpResponse.json(inv, { status: 201 })
    }),

    http.patch('*/sales/invoices/:id/', async ({ params, request }) => {
        const body = await request.json()
        const inv = db.invoices.update(params.id, body)
        if (!inv) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(inv)
    }),

    http.post('*/sales/invoices/:id/finalize/', ({ params }) => {
        const inv = db.invoices.update(params.id, { status: 'finalized' })
        if (!inv) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(inv)
    }),

    http.post('*/sales/invoices/:id/void/', async ({ params, request }) => {
        const { reason } = await request.json()
        const inv = db.invoices.update(params.id, { status: 'voided', void_reason: reason, voided_at: new Date().toISOString() })
        if (!inv) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(inv)
    }),

    http.post('*/sales/invoices/:id/correct/', async ({ params, request }) => {
        const body = await request.json()
        const orig = db.invoices.get(params.id)
        if (!orig) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        const num = `INV-${String(_invSeq++).padStart(4, '0')}-COR`
        const correction = db.invoices.create({
            ...body,
            invoice_number: num,
            status: 'finalized',
            correction_type: body.type,
            original_invoice_id: Number(params.id),
            grand_total: 0, amount_paid: 0, balance_due: 0,
        })
        // Update original
        db.invoices.update(params.id, { status: body.type === 'void' ? 'voided' : 'returned', correction_id: correction.id })
        return HttpResponse.json(correction, { status: 201 })
    }),

    http.get('*/sales/daily-summary/', ({ request }) => {
        const url = new URL(request.url)
        const date = url.searchParams.get('date') || new Date().toISOString().slice(0, 10)
        const todayInvs = db.invoices.list(i => i.created_at.startsWith(date) && ['finalized', 'paid', 'partially_paid'].includes(i.status))
        const total_sales = todayInvs.reduce((s, i) => s + i.grand_total, 0)
        const cash_received = todayInvs.reduce((s, i) => s + i.amount_paid, 0)
        const gross_profit = Math.round(total_sales * 0.18)
        const gross_margin = total_sales > 0 ? (gross_profit / total_sales) * 100 : 0
        const overdueCount = db.plans.list(p => p.status === 'overdue').length
        const openRepairs = db.repairs.list(r => !['delivered', 'cancelled'].includes(r.status)).length
        const readyRepairs = db.repairs.list(r => r.status === 'ready').length
        return HttpResponse.json({
            date, total_sales, cash_received, gross_profit,
            gross_margin: parseFloat(gross_margin.toFixed(1)),
            invoice_count: todayInvs.length,
            expected_cash: cash_received + 500,   // simulate minor variance
            overdue_plans: overdueCount,
            open_repairs: openRepairs,
            repairs_ready: readyRepairs,
            repairs_completed: db.repairs.list(r => r.status === 'delivered').length,
        })
    }),
]
