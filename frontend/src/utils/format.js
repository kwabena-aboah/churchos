import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)

export function formatDate(date, fmt = 'DD MMM YYYY') {
  if (!date) return '—'
  return dayjs(date).format(fmt)
}

export function formatDateTime(date) {
  if (!date) return '—'
  return dayjs(date).format('DD MMM YYYY, h:mm A')
}

export function formatRelative(date) {
  if (!date) return '—'
  return dayjs(date).fromNow()
}

export function formatCurrency(amount, symbol = '₵') {
  const num = parseFloat(amount || 0)
  return `${symbol}${num.toLocaleString('en-GH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

export function initials(name) {
  if (!name) return '?'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

export function statusBadgeClass(status) {
  const map = {
    active: 'badge-active',
    approved: 'badge-active',
    paid: 'badge-active',
    pass: 'badge-active',
    completed: 'badge-active',
    answered: 'badge-active',
    inactive: 'badge-inactive',
    rejected: 'badge-inactive',
    fail: 'badge-inactive',
    terminated: 'badge-inactive',
    pending: 'badge-pending',
    draft: 'badge-pending',
    warning: 'badge-pending',
    open: 'badge-pending',
    visitor: 'badge-visitor',
    info: 'badge-visitor',
    in_progress: 'badge-visitor',
    sent: 'badge-active',
    failed: 'badge-inactive',
  }
  return map[status?.toLowerCase()] || 'badge-visitor'
}

export function debounce(fn, delay = 300) {
  let timer
  return (...args) => {
    clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delay)
  }
}

export function truncate(str, len = 100) {
  if (!str) return ''
  return str.length > len ? str.slice(0, len) + '…' : str
}

export const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]

export function monthName(num) {
  return MONTHS[(num - 1) % 12] || ''
}
