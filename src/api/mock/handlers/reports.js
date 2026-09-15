import { http, HttpResponse } from 'msw'
import { db } from '../db/index.js'

const money = (n) => Math.round((Number(n) || 0) * 100) / 100

function soldInvoices() {
    return db.invoices.list(i => ['finalized', 'paid', 'partially_paid'].includes(i.status))
}

export const reportsHandlers = [
    http.get('*/reports/sales-summary/', () => {
        const invs = soldInvoices()
        const total_sales = money(invs.reduce((s, i) => s + (Number(i.grand_total) || 0), 0))
        const cash_collected = money(invs.reduce((s, i) => s + (Number(i.amount_paid) || 0), 0))
        const invoice_count = invs.length
        return HttpResponse.json({
            total_sales,
            invoice_count,
            avg_invoice: invoice_count ? money(total_sales / invoice_count) : 0,
            cash_collected,
            periods: invs.slice(0, 30).map(i => ({
                period: (i.created_at || '').slice(0, 10),
                invoice_count: 1,
                total: Number(i.grand_total) || 0,
            })),
        })
    }),

    http.get('*/reports/profit-loss/', () => {
        const invs = soldInvoices()
        const revenue = money(invs.reduce((s, i) => s + (Number(i.grand_total) || 0), 0))
        const cogs = money(revenue * 0.72)
        const expenses = money(db.expenses.all().reduce((s, e) => s + (Number(e.amount) || 0), 0))
        const gross_profit = money(revenue - cogs)
        return HttpResponse.json({
            revenue, cost_of_goods: cogs, gross_profit,
            total_expenses: expenses,
            net_profit: money(gross_profit - expenses),
            gross_margin_pct: revenue ? money(gross_profit / revenue * 100) : 0,
        })
    }),

    http.get('*/reports/inventory-valuation/', () => {
        const devices = db.devices.list(d => d.lifecycle_state === 'in_stock')
        const acc = db.accessories.all()
        const cost = money(
            devices.reduce((s, d) => s + (Number(d.cost_price) || 0), 0) +
            acc.reduce((s, a) => s + (Number(a.cost_price) || 0) * (Number(a.stock_qty) || 0), 0)
        )
        const retail = money(
            devices.reduce((s, d) => s + (Number(d.sell_price) || 0), 0) +
            acc.reduce((s, a) => s + (Number(a.sell_price) || 0) * (Number(a.stock_qty) || 0), 0)
        )
        return HttpResponse.json({
            total_cost: cost, total_retail: retail,
            potential_profit: money(retail - cost),
            device_count: devices.length, accessory_count: acc.length,
            items: [
                ...devices.map(d => ({ name: `${d.brand} ${d.model}`, sku: d.serial, qty: 1, cost: d.cost_price, retail: d.sell_price })),
                ...acc.map(a => ({ name: a.name, sku: a.sku, qty: a.stock_qty, cost: a.cost_price, retail: a.sell_price })),
            ],
        })
    }),

    http.get('*/reports/cash/', () => {
        const inflows = money(db.cashInflows.all().reduce((s, r) => s + (Number(r.amount) || 0), 0))
        const outflows = money(db.cashOutflows.all().reduce((s, r) => s + (Number(r.amount) || 0), 0))
        const expenses = money(db.expenses.all().reduce((s, e) => s + (Number(e.amount) || 0), 0))
        return HttpResponse.json({
            total_inflows: inflows, total_outflows: outflows, total_expenses: expenses,
            net_cash: money(inflows - outflows - expenses),
            session_count: db.cashSessions.count(),
        })
    }),

    http.get('*/reports/imei-history/', () => HttpResponse.json({ results: [] })),
    http.get('*/reports/repairs/', () => HttpResponse.json({
        total: db.repairs.count(),
        completed: db.repairs.count(r => r.status === 'delivered'),
        pending: db.repairs.count(r => !['delivered', 'cancelled'].includes(r.status)),
        results: db.repairs.all(),
    })),
    http.get('*/reports/installments/', () => HttpResponse.json({ results: db.plans.all() })),
    http.get('*/reports/customer-ledger/', () => HttpResponse.json({ results: db.customers.all() })),
    http.get('*/reports/staff-performance/', () => HttpResponse.json({ results: [] })),
    http.get('*/reports/dead-stock/', () => HttpResponse.json({
        results: db.devices.list(d => d.lifecycle_state === 'in_stock'),
    })),

    // CSV export — return a tiny CSV blob so the download works.
    http.get('*/reports/:slug/export/', ({ params }) => {
        const csv = `report,generated\n${params.slug},${new Date().toISOString()}\n`
        return new HttpResponse(csv, { headers: { 'Content-Type': 'text/csv' } })
    }),
]
