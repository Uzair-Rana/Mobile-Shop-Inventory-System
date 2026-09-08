/**
 * Central Axios instance for DEVNEST SYSTEM.
 * - Attaches auth token to every request
 * - Injects X-Branch-ID from branchStore
 * - Handles 401 → logout redirect
 * - Normalises DRF paginated responses
 * - Broadcasts pending-request count so SyncIndicator can show activity
 */

import axios from 'axios'

export const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export const client = axios.create({
    baseURL: BASE_URL,
    headers: { 'Content-Type': 'application/json' },
    timeout: 30_000,
})

// Pending-request counter; components can subscribe via useSyncStore
let _pendingRequests = 0
const _listeners = new Set()

export function onPendingChange(cb) { _listeners.add(cb); return () => _listeners.delete(cb) }
function notifyPending() { _listeners.forEach(cb => cb(_pendingRequests)) }

// ── Request interceptor ────────────────────────────────────────────────────────
client.interceptors.request.use((config) => {
    // Auth token
    const token = localStorage.getItem('devnest_token')
    if (token) config.headers.Authorization = `Token ${token}`

    // Branch scoping — read active branch from localStorage to avoid circular Pinia imports
    const branchId = localStorage.getItem('devnest_branch_id')
    if (branchId) config.headers['X-Branch-ID'] = branchId

    _pendingRequests++
    notifyPending()
    return config
}, (error) => {
    _pendingRequests = Math.max(0, _pendingRequests - 1)
    notifyPending()
    return Promise.reject(error)
})

// ── Response interceptor ───────────────────────────────────────────────────────
client.interceptors.response.use(
    (response) => {
        _pendingRequests = Math.max(0, _pendingRequests - 1)
        notifyPending()
        return response
    },
    (error) => {
        _pendingRequests = Math.max(0, _pendingRequests - 1)
        notifyPending()

        if (error.response?.status === 401) {
            localStorage.removeItem('devnest_token')
            localStorage.removeItem('devnest_user')
            localStorage.removeItem('devnest_branch_id')
            if (!window.location.pathname.includes('/login')) {
                window.location.href = '/login'
            }
        }
        return Promise.reject(normaliseError(error))
    }
)

function normaliseError(error) {
    if (error.response?.data) {
        const data = error.response.data
        if (typeof data === 'string') {
            error.displayMessage = data
        } else if (data.detail) {
            error.displayMessage = data.detail
        } else {
            const msgs = Object.entries(data)
                .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
            error.displayMessage = msgs.join(' | ')
        }
    } else if (error.code === 'ECONNABORTED') {
        error.displayMessage = 'Request timed out. Check your connection.'
    } else if (!error.response) {
        error.displayMessage = 'Network error. You may be offline.'
    }
    return error
}

export default client
