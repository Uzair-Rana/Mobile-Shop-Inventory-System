import { http, HttpResponse } from 'msw'
import { db, searchIn, parsePagination, paginated } from '../db/index.js'

export const inventoryHandlers = [

    // ── Devices (IMEI) ─────────────────────────────────────────────────────────

    http.get('*/inventory/devices/', ({ request }) => {
        const url = new URL(request.url)
        const { page, pageSize } = parsePagination(url)
        const q = url.searchParams.get('search') || ''
        const status = url.searchParams.get('lifecycle_state') || ''
        const branch = request.headers.get('X-Branch-ID')
        let rows = db.devices.all()
        if (branch) rows = rows.filter(r => String(r.branch_id) === String(branch))
        if (status) rows = rows.filter(r => r.lifecycle_state === status)
        if (q) rows = searchIn(rows, q, ['imei1', 'imei2', 'serial', 'brand', 'model'])
        return HttpResponse.json(paginated(rows, page, pageSize))
    }),

    http.get('*/inventory/devices/check_duplicate/', ({ request }) => {
        const url = new URL(request.url)
        const imei = url.searchParams.get('imei') || ''
        const dupe = db.devices.find(d => d.imei1 === imei || d.imei2 === imei)
        return HttpResponse.json({ duplicate: !!dupe, device: dupe || null })
    }),

    http.get('*/inventory/devices/:id/timeline/', ({ params }) => {
        const events = db.deviceTimelines[Number(params.id)] || []
        return HttpResponse.json(events)
    }),

    http.get('*/inventory/devices/:id/', ({ params }) => {
        const d = db.devices.get(params.id)
        if (!d) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(d)
    }),

    http.post('*/inventory/devices/', async ({ request }) => {
        const body = await request.json()
        const device = db.devices.create(body)
        return HttpResponse.json(device, { status: 201 })
    }),

    http.patch('*/inventory/devices/:id/', async ({ params, request }) => {
        const body = await request.json()
        const device = db.devices.update(params.id, body)
        if (!device) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(device)
    }),

    http.post('*/inventory/devices/:id/adjust_cost/', async ({ params, request }) => {
        const body = await request.json()
        const device = db.devices.get(params.id)
        if (!device) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        const prev = device.cost_price
        const updated = db.devices.update(params.id, { cost_price: body.new_cost })
        // Push a timeline event
        const timeline = db.deviceTimelines[Number(params.id)] || []
        timeline.push({
            id: Date.now(), device_id: Number(params.id), type: 'price_change',
            timestamp: new Date().toISOString(), actor: 'current_user',
            title: 'Cost price adjusted',
            detail: `Old: Rs. ${prev.toLocaleString()} → New: Rs. ${body.new_cost.toLocaleString()}, Reason: ${body.reason}`,
        })
        db.deviceTimelines[Number(params.id)] = timeline
        return HttpResponse.json(updated)
    }),

    // ── Accessories ────────────────────────────────────────────────────────────

    http.get('*/inventory/accessories/', ({ request }) => {
        const url = new URL(request.url)
        const { page, pageSize } = parsePagination(url)
        const q = url.searchParams.get('search') || ''
        const branch = request.headers.get('X-Branch-ID')
        let rows = db.accessories.all()
        if (branch) rows = rows.filter(r => String(r.branch_id) === String(branch))
        if (q) rows = searchIn(rows, q, ['name', 'sku', 'brand', 'category'])
        return HttpResponse.json(paginated(rows, page, pageSize))
    }),

    http.get('*/inventory/accessories/:id/movements/', ({ params, request }) => {
        const url = new URL(request.url)
        const { page, pageSize } = parsePagination(url)
        const rows = db.movements.list(m => String(m.accessory_id) === String(params.id))
        return HttpResponse.json(paginated(rows, page, pageSize))
    }),

    http.get('*/inventory/accessories/:id/', ({ params }) => {
        const a = db.accessories.get(params.id)
        if (!a) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(a)
    }),

    http.post('*/inventory/accessories/', async ({ request }) => {
        const body = await request.json()
        const acc = db.accessories.create(body)
        return HttpResponse.json(acc, { status: 201 })
    }),

    http.patch('*/inventory/accessories/:id/', async ({ params, request }) => {
        const body = await request.json()
        const acc = db.accessories.update(params.id, body)
        if (!acc) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(acc)
    }),

    http.post('*/inventory/accessories/:id/adjust_stock/', async ({ params, request }) => {
        const { qty_change, note } = await request.json()
        const acc = db.accessories.get(params.id)
        if (!acc) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        const updated = db.accessories.update(params.id, { stock_qty: acc.stock_qty + qty_change, last_movement: new Date().toISOString() })
        db.movements.create({ accessory_id: Number(params.id), date: new Date().toISOString(), type: qty_change > 0 ? 'adjustment_in' : 'adjustment_out', qty_change, reason: note || 'Manual adjustment', actor: 'current_user' })
        return HttpResponse.json(updated)
    }),

    // ── Low-stock & scan ───────────────────────────────────────────────────────

    http.get('*/inventory/low-stock/', ({ request }) => {
        const url = new URL(request.url)
        const { page, pageSize } = parsePagination(url)
        const branch = request.headers.get('X-Branch-ID')
        let rows = db.accessories.list(a => a.stock_qty <= a.reorder_level)
        if (branch) rows = rows.filter(a => String(a.branch_id) === String(branch))
        return HttpResponse.json(paginated(rows, page, pageSize))
    }),

    http.get('*/inventory/scan/', ({ request }) => {
        const url = new URL(request.url)
        const q = url.searchParams.get('q') || ''
        // Check devices first
        const device = db.devices.find(d => d.imei1 === q || d.imei2 === q || d.serial === q)
        if (device) {
            return HttpResponse.json({ type: 'unit', unit_id: device.id, product_id: device.id, name: `${device.brand} ${device.model}`, sku: device.serial, imei: device.imei1, price: device.sell_price })
        }
        // Then accessories by SKU
        const acc = db.accessories.find(a => a.sku === q || a.name.toLowerCase().includes(q.toLowerCase()))
        if (acc) {
            return HttpResponse.json({ type: 'accessory', product_id: acc.id, name: acc.name, sku: acc.sku, imei: null, price: acc.sell_price })
        }
        return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
    }),

    // ── Products (generic — used by POS product search & PO/purchase forms) ────
    http.get('*/inventory/products/', ({ request }) => {
        const url = new URL(request.url)
        const { page, pageSize } = parsePagination(url)
        const q = (url.searchParams.get('search') || '').trim().toLowerCase()
        const rows = [
            // Serialised devices — carry IMEI + unit identity so POS can add them as units.
            ...db.devices.all().map(d => ({
                id: d.id,
                product_id: d.id,
                unit_id: d.id,
                type: 'unit',
                name: `${d.brand} ${d.model}`,
                sku: d.serial,
                brand_name: d.brand,
                imei1: d.imei1,
                imei2: d.imei2,
                imei: d.imei1,
                price: d.sell_price,
                sell_price: d.sell_price,
                cost_price: d.cost_price,
                lifecycle_state: d.lifecycle_state,
                stock_qty: d.lifecycle_state === 'in_stock' ? 1 : 0,
            })),
            // Accessories — non-serialised.
            ...db.accessories.all().map(a => ({
                id: `acc_${a.id}`,
                product_id: a.id,
                unit_id: null,
                type: 'accessory',
                name: a.name,
                sku: a.sku,
                brand_name: a.brand,
                category_name: a.category,
                imei: null,
                price: a.sell_price,
                sell_price: a.sell_price,
                cost_price: a.cost_price,
                stock_qty: a.stock_qty,
            })),
        ]
        let out = rows
        if (q) {
            out = rows.filter(r =>
                (r.name || '').toLowerCase().includes(q) ||
                (r.sku || '').toLowerCase().includes(q) ||
                (r.imei1 || '').toLowerCase().includes(q) ||
                (r.imei2 || '').toLowerCase().includes(q)
            )
        }
        return HttpResponse.json(paginated(out, page, pageSize))
    }),

    // Create/update a generic product — backed by the accessories store.
    http.post('*/inventory/products/', async ({ request }) => {
        const body = await request.json()
        const acc = db.accessories.create({
            stock_qty: 0, reorder_level: 5, brand: '', category: '', ...body,
        })
        return HttpResponse.json({ ...acc, id: acc.id, product_id: acc.id }, { status: 201 })
    }),

    http.patch('*/inventory/products/:id/', async ({ params, request }) => {
        const body = await request.json()
        const id = String(params.id).replace(/^acc_/, '')
        const acc = db.accessories.update(id, body)
        if (!acc) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(acc)
    }),

    http.get('*/inventory/categories/', () => {
        const cats = [...new Set(db.accessories.all().map(a => a.category))]
        return HttpResponse.json(cats.map((c, i) => ({ id: i + 1, name: c })))
    }),

    http.get('*/inventory/brands/', () => {
        const brands = [...new Set([...db.devices.all().map(d => d.brand), ...db.accessories.all().map(a => a.brand)])]
        return HttpResponse.json(brands.map((b, i) => ({ id: i + 1, name: b })))
    }),
]
