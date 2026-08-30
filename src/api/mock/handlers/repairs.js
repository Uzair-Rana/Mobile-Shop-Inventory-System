import { http, HttpResponse } from 'msw'
import { db, searchIn, parsePagination, paginated } from '../db/index.js'

let _jobSeq = 20

export const repairsHandlers = [

    http.get('*/repairs/jobs/', ({ request }) => {
        const url = new URL(request.url)
        const { page, pageSize } = parsePagination(url)
        const q = url.searchParams.get('search') || ''
        const statusParam = url.searchParams.get('status') || ''
        const statuses = statusParam ? statusParam.split(',') : []
        let rows = db.repairs.all().sort((a, b) => b.created_at.localeCompare(a.created_at))
        if (statuses.length) rows = rows.filter(r => statuses.includes(r.status))
        if (q) rows = searchIn(rows, q, ['job_number', 'customer_name', 'device_model'])
        return HttpResponse.json(paginated(rows, page, pageSize))
    }),

    http.get('*/repairs/jobs/:id/', ({ params }) => {
        const job = db.repairs.get(params.id)
        if (!job) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json({ ...job, logs: db.repairLogs[Number(params.id)] || [] })
    }),

    http.post('*/repairs/jobs/', async ({ request }) => {
        const body = await request.json()
        const num = `JOB-${String(_jobSeq++).padStart(4, '0')}`
        const job = db.repairs.create({ ...body, job_number: num, status: 'received' })
        return HttpResponse.json(job, { status: 201 })
    }),

    http.patch('*/repairs/jobs/:id/', async ({ params, request }) => {
        const body = await request.json()
        const job = db.repairs.update(params.id, body)
        if (!job) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        return HttpResponse.json(job)
    }),

    http.post('*/repairs/jobs/:id/update_status/', async ({ params, request }) => {
        const { status, note } = await request.json()
        const job = db.repairs.update(params.id, { status, updated_at: new Date().toISOString() })
        if (!job) return HttpResponse.json({ detail: 'Not found.' }, { status: 404 })
        const logs = db.repairLogs[Number(params.id)] || []
        logs.push({ id: Date.now(), repair_id: Number(params.id), status, note: note || '', timestamp: new Date().toISOString(), actor: 'current_user' })
        db.repairLogs[Number(params.id)] = logs
        return HttpResponse.json(job)
    }),
]
