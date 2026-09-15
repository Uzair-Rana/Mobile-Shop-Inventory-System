/**
 * v-restrict — block invalid characters as the user types.
 *
 * Usage (works on a plain <input> or on a component like <AppInput> that
 * renders an inner <input>):
 *   <input v-restrict="'digits'"  />   digits only
 *   <input v-restrict="'imei'"    />   digits only, max 15
 *   <input v-restrict="'decimal'" />   number with a single decimal point (money)
 *   <input v-restrict="'integer'" />   whole numbers only
 *
 * It sanitises the field and re-dispatches `input`, so v-model always receives
 * the cleaned value.
 */
function sanitize(mode, val) {
    const s = String(val ?? '')
    switch (mode) {
        case 'digits':
            return s.replace(/\D/g, '')
        case 'imei':
            return s.replace(/\D/g, '').slice(0, 15)
        case 'integer':
            return s.replace(/\D/g, '')
        case 'decimal': {
            let v = s.replace(/[^0-9.]/g, '')
            const i = v.indexOf('.')
            if (i !== -1) v = v.slice(0, i + 1) + v.slice(i + 1).replace(/\./g, '')
            return v
        }
        default:
            return s
    }
}

function makeHandler(mode) {
    return function (e) {
        const el = e.target
        const clean = sanitize(mode, el.value)
        if (clean !== el.value) {
            el.value = clean
            el.dispatchEvent(new Event('input', { bubbles: true }))
        }
    }
}

function targetInput(el) {
    return el.tagName === 'INPUT' ? el : el.querySelector('input')
}

export const restrict = {
    mounted(el, binding) {
        const input = targetInput(el)
        if (!input) return
        const h = makeHandler(binding.value || 'digits')
        input.__restrictHandler = h
        input.addEventListener('input', h)
    },
    unmounted(el) {
        const input = targetInput(el)
        if (input && input.__restrictHandler) {
            input.removeEventListener('input', input.__restrictHandler)
            delete input.__restrictHandler
        }
    },
}
