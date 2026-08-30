import { http, HttpResponse } from 'msw'
import { db } from '../db/index.js'

export const branchHandlers = [
    http.get('*/branches/', () => {
        return HttpResponse.json(db.branches.all())
    }),
]
