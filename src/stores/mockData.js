/**
 * Master mock data store — loads all fixtures and exposes them reactively.
 * All Pinia stores that need data should import from here.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

import { userFixtures } from '@/api/mock/db/fixtures/users'
import { branchFixtures } from '@/api/mock/db/fixtures/branches'
import { deviceFixtures, deviceTimelineFixtures } from '@/api/mock/db/fixtures/devices'
import { accessoryFixtures, movementFixtures } from '@/api/mock/db/fixtures/accessories'
import { customerFixtures, ledgerFixtures } from '@/api/mock/db/fixtures/customers'
import { invoiceFixtures, invoiceLineFixtures } from '@/api/mock/db/fixtures/invoices'
import { repairFixtures, repairStatusLogFixtures } from '@/api/mock/db/fixtures/repairs'
import { installmentPlanFixtures, installmentScheduleFixtures } from '@/api/mock/db/fixtures/installments'
import { purchaseOrderFixtures, poLineFixtures } from '@/api/mock/db/fixtures/purchases'
import { cashSessionFixtures, cashInflowFixtures, cashOutflowFixtures, expenseFixtures } from '@/api/mock/db/fixtures/cash'
import { transferFixtures } from '@/api/mock/db/fixtures/transfers'
import { roleFixtures, auditLogFixtures } from '@/api/mock/db/fixtures/admin'

export const useMockDataStore = defineStore('mockData', () => {
    // ── Reactive data collections ──────────────────────────────────────────────
    const users = ref(userFixtures.map(u => ({ ...u })))
    const branches = ref(branchFixtures.map(b => ({ ...b })))
    const devices = ref(deviceFixtures.map(d => ({ ...d })))
    const deviceTimelines = ref({ ...deviceTimelineFixtures })
    const accessories = ref(accessoryFixtures.map(a => ({ ...a })))
    const movements = ref(movementFixtures.map(m => ({ ...m })))
    const customers = ref(customerFixtures.map(c => ({ ...c })))
    const ledgers = ref({ ...ledgerFixtures })
    const invoices = ref(invoiceFixtures.map(i => ({ ...i })))
    const invoiceLines = ref({ ...invoiceLineFixtures })
    const repairs = ref(repairFixtures.map(r => ({ ...r })))
    const repairLogs = ref({ ...repairStatusLogFixtures })
    const plans = ref(installmentPlanFixtures.map(p => ({ ...p })))
    const schedules = ref({ ...installmentScheduleFixtures })
    const purchaseOrders = ref(purchaseOrderFixtures.map(o => ({ ...o })))
    const poLines = ref({ ...poLineFixtures })
    const cashSessions = ref(cashSessionFixtures.map(s => ({ ...s })))
    const cashInflows = ref(cashInflowFixtures.map(i => ({ ...i })))
    const cashOutflows = ref(cashOutflowFixtures.map(o => ({ ...o })))
    const expenses = ref(expenseFixtures.map(e => ({ ...e })))
    const transfers = ref(transferFixtures.map(t => ({ ...t })))
    const roles = ref(roleFixtures.map(r => ({ ...r, permissions: [...r.permissions] })))
    const auditLogs = ref(auditLogFixtures.map(l => ({ ...l })))

    // ── Sequence counters ──────────────────────────────────────────────────────
    let nextId = {
        invoice: 100,
        repair: 200,
        device: 50,
        accessory: 50,
        expense: 50,
        transfer: 50,
    }

    // ── Helper: find device by IMEI ──────────────────────────────────────────
    function findDevice(imei) {
        if (!imei) return null
        const q = imei.trim()
        return devices.value.find(d =>
            d.imei1 === q || d.imei2 === q || d.serial === q
        ) || null
    }

    function getCustomer(id) {
        return customers.value.find(c => c.id === Number(id)) || null
    }

    function getDevice(id) {
        return devices.value.find(d => d.id === Number(id)) || null
    }

    function getAccessory(id) {
        return accessories.value.find(a => a.id === Number(id)) || null
    }

    function getInvoice(id) {
        return invoices.value.find(i => i.id === Number(id)) || null
    }

    function getInvoiceLines(invoiceId) {
        return invoiceLines.value[Number(invoiceId)] || []
    }

    function getRepair(id) {
        return repairs.value.find(r => r.id === Number(id)) || null
    }

    function getRepairLogs(repairId) {
        return repairLogs.value[Number(repairId)] || []
    }

    function getPlan(id) {
        return plans.value.find(p => p.id === Number(id)) || null
    }

    function getSchedule(planId) {
        return schedules.value[Number(planId)] || []
    }

    function getPurchaseOrder(id) {
        return purchaseOrders.value.find(o => o.id === Number(id)) || null
    }

    function getPOLines(poId) {
        return poLines.value[Number(poId)] || []
    }

    function getTransfer(id) {
        return transfers.value.find(t => t.id === Number(id)) || null
    }

    function getLedger(customerId) {
        return ledgers.value[Number(customerId)] || []
    }

    function getDeviceTimeline(deviceId) {
        return deviceTimelines.value[Number(deviceId)] || []
    }

    // ── Scan lookup: IMEI → device or sku → accessory ───────────────────────
    function scanItem(query) {
        if (!query) return null
        const q = query.trim().toLowerCase()

        // Try IMEI match (devices in stock)
        const device = devices.value.find(d =>
            d.lifecycle_state === 'in_stock' &&
            (d.imei1?.toLowerCase() === q || d.imei2?.toLowerCase() === q || d.serial?.toLowerCase() === q)
        )
        if (device) {
            return {
                type: 'unit',
                product_id: device.id,
                unit_id: device.id,
                name: `${device.brand} ${device.model}`,
                sku: device.imei1,
                imei: device.imei1,
                price: device.sell_price,
            }
        }

        // Try accessory SKU or name
        const acc = accessories.value.find(a =>
            a.sku?.toLowerCase() === q ||
            a.name?.toLowerCase().includes(q)
        )
        if (acc) {
            return {
                type: 'accessory',
                product_id: acc.id,
                unit_id: null,
                name: acc.name,
                sku: acc.sku,
                imei: null,
                price: acc.sell_price,
            }
        }

        return null
    }

    // ── Mutations ─────────────────────────────────────────────────────────────

    function addInvoice(invoice) {
        const id = ++nextId.invoice
        const newInv = { ...invoice, id }
        invoices.value.unshift(newInv)
        return newInv
    }

    function addInvoiceLines(invoiceId, lines) {
        invoiceLines.value[invoiceId] = lines
    }

    function voidInvoice(id) {
        const inv = invoices.value.find(i => i.id === Number(id))
        if (inv) inv.status = 'voided'
    }

    function addDevice(device) {
        const id = ++nextId.device
        const newDev = { ...device, id, lifecycle_state: 'in_stock', created_at: new Date().toISOString() }
        devices.value.unshift(newDev)
        return newDev
    }

    function updateDevice(id, data) {
        const dev = devices.value.find(d => d.id === Number(id))
        if (dev) Object.assign(dev, data)
    }

    function addExpense(expense) {
        const id = ++nextId.expense
        const newExp = { ...expense, id, created_at: new Date().toISOString() }
        expenses.value.unshift(newExp)
        return newExp
    }

    function addTransfer(transfer) {
        const id = ++nextId.transfer
        const newTrf = { ...transfer, id, created_at: new Date().toISOString() }
        transfers.value.unshift(newTrf)
        return newTrf
    }

    function updateTransfer(id, data) {
        const trf = transfers.value.find(t => t.id === Number(id))
        if (trf) Object.assign(trf, data)
    }

    function updateRepair(id, data) {
        const rep = repairs.value.find(r => r.id === Number(id))
        if (rep) Object.assign(rep, data)
    }

    function addRepairLog(repairId, log) {
        const id = repairId
        if (!repairLogs.value[id]) repairLogs.value[id] = []
        repairLogs.value[id].push({ ...log, id: Date.now() })
    }

    function addAuditLog(entry) {
        auditLogs.value.unshift({
            ...entry,
            id: Date.now(),
            timestamp: new Date().toISOString(),
        })
    }

    function updateUser(id, data) {
        const user = users.value.find(u => u.id === Number(id))
        if (user) Object.assign(user, data)
    }

    function updateRole(id, data) {
        const role = roles.value.find(r => r.id === Number(id))
        if (role) Object.assign(role, data)
    }

    // Computed stats for dashboard
    const todaySummary = computed(() => {
        const today = new Date().toISOString().slice(0, 10)
        const todayInvoices = invoices.value.filter(i => i.created_at?.startsWith(today))
        const totalSales = todayInvoices.reduce((sum, i) => sum + (i.grand_total || 0), 0)
        const cashReceived = todayInvoices
            .filter(i => i.payment_method === 'cash')
            .reduce((sum, i) => sum + (i.amount_paid || 0), 0)
        const openRepairs = repairs.value.filter(r => !['delivered', 'cancelled', 'unrepairable'].includes(r.status)).length
        const readyRepairs = repairs.value.filter(r => r.status === 'ready').length
        const overdueCount = plans.value.filter(p => p.status === 'overdue').length

        return {
            total_sales: totalSales,
            invoice_count: todayInvoices.length,
            cash_received: cashReceived,
            gross_profit: totalSales * 0.18,
            gross_margin: 18,
            open_repairs: openRepairs,
            repairs_ready: readyRepairs,
            overdue_plans: overdueCount,
        }
    })

    return {
        // Data
        users, branches, devices, deviceTimelines,
        accessories, movements, customers, ledgers,
        invoices, invoiceLines, repairs, repairLogs,
        plans, schedules, purchaseOrders, poLines,
        cashSessions, cashInflows, cashOutflows, expenses,
        transfers, roles, auditLogs,

        // Getters
        findDevice, getCustomer, getDevice, getAccessory,
        getInvoice, getInvoiceLines, getRepair, getRepairLogs,
        getPlan, getSchedule, getPurchaseOrder, getPOLines,
        getTransfer, getLedger, getDeviceTimeline,
        scanItem, todaySummary,

        // Mutations
        addInvoice, addInvoiceLines, voidInvoice,
        addDevice, updateDevice, addExpense,
        addTransfer, updateTransfer,
        updateRepair, addRepairLog,
        addAuditLog, updateUser, updateRole,
    }
})
