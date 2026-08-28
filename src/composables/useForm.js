/**
 * useForm — lightweight reactive form helper with field-level validation.
 * Intentionally thin: no schema library needed for most forms in this app.
 *
 * Usage:
 *   const { fields, errors, validate, reset, isDirty } = useForm({
 *     name: { value: '', required: true },
 *     price: { value: 0, required: true, min: 0 },
 *   })
 */
import { reactive, computed } from 'vue'

export function useForm(schema) {
    const fields = reactive({})
    const errors = reactive({})
    const touched = reactive({})

    // Initialise
    for (const [key, def] of Object.entries(schema)) {
        fields[key] = def.value ?? ''
        errors[key] = ''
        touched[key] = false
    }

    const initialValues = JSON.parse(JSON.stringify(fields))

    function validateField(key) {
        const def = schema[key]
        const value = fields[key]
        errors[key] = ''

        if (def.required && (value === '' || value === null || value === undefined)) {
            errors[key] = def.requiredMsg || 'This field is required'
            return false
        }
        if (def.min !== undefined && Number(value) < def.min) {
            errors[key] = def.minMsg || `Minimum value is ${def.min}`
            return false
        }
        if (def.max !== undefined && Number(value) > def.max) {
            errors[key] = def.maxMsg || `Maximum value is ${def.max}`
            return false
        }
        if (def.minLength && String(value).length < def.minLength) {
            errors[key] = `Minimum ${def.minLength} characters`
            return false
        }
        if (def.pattern && !def.pattern.test(value)) {
            errors[key] = def.patternMsg || 'Invalid format'
            return false
        }
        if (def.validate) {
            const msg = def.validate(value, fields)
            if (msg) { errors[key] = msg; return false }
        }
        return true
    }

    function validate() {
        let valid = true
        for (const key of Object.keys(schema)) {
            touched[key] = true
            if (!validateField(key)) valid = false
        }
        return valid
    }

    function touch(key) {
        touched[key] = true
        validateField(key)
    }

    function reset() {
        for (const key of Object.keys(schema)) {
            fields[key] = initialValues[key]
            errors[key] = ''
            touched[key] = false
        }
    }

    function setValues(values) {
        for (const [key, val] of Object.entries(values)) {
            if (key in fields) fields[key] = val
        }
    }

    const isDirty = computed(() =>
        Object.keys(schema).some(k => JSON.stringify(fields[k]) !== JSON.stringify(initialValues[k]))
    )

    const hasErrors = computed(() => Object.values(errors).some(Boolean))

    return { fields, errors, touched, isDirty, hasErrors, validate, validateField, touch, reset, setValues }
}
