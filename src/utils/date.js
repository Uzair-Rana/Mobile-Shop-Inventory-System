/**
 * Date/time formatting utilities
 */

const LOCALE = 'en-PK'

export function formatDate(value) {
    if (!value) return '—'
    try {
        return new Intl.DateTimeFormat(LOCALE, { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(value))
    } catch { return String(value) }
}

export function formatDateTime(value) {
    if (!value) return '—'
    try {
        return new Intl.DateTimeFormat(LOCALE, {
            day: '2-digit', month: 'short', year: 'numeric',
            hour: '2-digit', minute: '2-digit', hour12: true
        }).format(new Date(value))
    } catch { return String(value) }
}

export function formatTime(value) {
    if (!value) return '—'
    try {
        return new Intl.DateTimeFormat(LOCALE, { hour: '2-digit', minute: '2-digit', hour12: true }).format(new Date(value))
    } catch { return String(value) }
}

export function toISODate(value) {
    if (!value) return null
    try { return new Date(value).toISOString().slice(0, 10) } catch { return null }
}

export function daysUntil(value) {
    if (!value) return null
    const diff = new Date(value) - new Date()
    return Math.ceil(diff / (1000 * 60 * 60 * 24))
}
