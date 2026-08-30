/**
 * createStore — lightweight in-memory entity store.
 * Each store supports: create, list, get, update, delete, paginate.
 * IDs are auto-incremented integers.
 */
export function createStore(initialData = []) {
    let _seq = initialData.length
        ? Math.max(...initialData.map(r => r.id ?? 0)) + 1
        : 1
    const _data = new Map(initialData.map(r => [r.id, { ...r }]))

    return {
        all() { return [..._data.values()] },

        list(filterFn = null) {
            const rows = [..._data.values()]
            return filterFn ? rows.filter(filterFn) : rows
        },

        paginate(page = 1, pageSize = 25, filterFn = null) {
            const rows = this.list(filterFn)
            const count = rows.length
            const start = (page - 1) * pageSize
            const results = rows.slice(start, start + pageSize)
            return {
                count,
                next: start + pageSize < count ? `?page=${page + 1}` : null,
                previous: page > 1 ? `?page=${page - 1}` : null,
                results,
            }
        },

        get(id) {
            return _data.get(Number(id)) ?? null
        },

        create(data) {
            const id = _seq++
            const now = new Date().toISOString()
            const record = { id, created_at: now, updated_at: now, ...data }
            _data.set(id, record)
            return record
        },

        update(id, data) {
            const existing = _data.get(Number(id))
            if (!existing) return null
            const record = { ...existing, ...data, updated_at: new Date().toISOString() }
            _data.set(Number(id), record)
            return record
        },

        delete(id) {
            return _data.delete(Number(id))
        },

        find(filterFn) {
            return [..._data.values()].find(filterFn) ?? null
        },

        count(filterFn = null) {
            return this.list(filterFn).length
        },
    }
}
