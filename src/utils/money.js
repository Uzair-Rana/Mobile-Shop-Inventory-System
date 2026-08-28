/**
 * Money formatting utilities.
 * All display of monetary values MUST go through these helpers —
 * never render raw floats in the UI.
 */

const DEFAULT_CURRENCY = 'PKR'
const DEFAULT_LOCALE = 'en-PK'

/**
 * Format a number as a currency string.
 * @param {number|string|null} value
 * @param {object} opts
 * @param {string} [opts.currency]
 * @param {string} [opts.locale]
 * @param {boolean} [opts.symbol] - include currency symbol/code
 * @returns {string}
 */
export function formatMoney(value, { currency = DEFAULT_CURRENCY, locale = DEFAULT_LOCALE, symbol = true } = {}) {
    const num = parseFloat(value)
    if (value === null || value === undefined || isNaN(num)) return symbol ? `${currency} —` : '—'
    try {
        return new Intl.NumberFormat(locale, {
            style: symbol ? 'currency' : 'decimal',
            currency,
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        }).format(num)
    } catch {
        // fallback: manual formatting so floats never show raw precision artifacts
        return `${symbol ? currency + ' ' : ''}${num.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`
    }
}

/**
 * Format money without symbol (for table columns etc.)
 */
export function formatAmount(value) {
    return formatMoney(value, { symbol: false })
}

/**
 * Parse a string like "12,345.67" → 12345.67
 */
export function parseMoney(str) {
    if (str === null || str === undefined || str === '') return null
    const cleaned = String(str).replace(/[^0-9.\-]/g, '')
    const num = parseFloat(cleaned)
    return isNaN(num) ? null : num
}

/**
 * Returns true if value rounds to zero (avoids floating-point surprise)
 */
export function isZero(value) {
    return Math.abs(parseFloat(value) || 0) < 0.005
}
