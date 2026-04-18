import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  // baseURL: 'http://127.0.0.1:8000/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

// ── Request interceptor — attach JWT ─────────────────────────────────────────
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
  },
  (error) => Promise.reject(error)
)

// ── Response interceptor — handle 401, refresh token ─────────────────────────
let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(p => error ? p.reject(error) : p.resolve(token))
  failedQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return api(originalRequest)
        }).catch(err => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) {
        isRefreshing = false
        window.location.href = '/login'
        return Promise.reject(error)
      }

      try {
        const { data } = await axios.post('/api/v1/auth/token/refresh/', { refresh: refreshToken })
        localStorage.setItem('access_token', data.access)
        api.defaults.headers.common.Authorization = `Bearer ${data.access}`
        processQueue(null, data.access)
        originalRequest.headers.Authorization = `Bearer ${data.access}`
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }
    return Promise.reject(error)
  }
)

export default api

// ── Resource helpers ──────────────────────────────────────────────────────────
export const authApi = {
  login: (data) => api.post('/auth/token/', data),
  logout: (refresh) => api.post('/auth/logout/', { refresh }),
  me: () => api.get('/auth/me/'),
  changePassword: (data) => api.post('/auth/change-password/', data),
  getUsers: (params) => api.get('/auth/users/', { params }),
  createUser: (data) => api.post('/auth/users/', data),
  updateUser: (id, data) => api.patch(`/auth/users/${id}/`, data),
  deleteUser: (id) => api.delete(`/auth/users/${id}/`),
}

export const settingsApi = {
  getPublic: () => api.get('/core/settings/public/'),
  get: () => api.get('/core/settings/'),
  update: (data) => api.patch('/core/settings/', data, { headers: { 'Content-Type': 'multipart/form-data' } }),
  getZones: () => api.get('/core/zones/'),
  getCellGroups: (params) => api.get('/core/cell-groups/', { params }),
  getServiceTypes: () => api.get('/core/service-types/'),
}

export const membersApi = {
  list: (params) => api.get('/members/', { params }),
  get: (id) => api.get(`/members/${id}/`),
  // create: (data) => api.post('/members/', data, { headers: { 'Content-Type': 'multipart/form-data' } }),
  update: (id, data) => api.patch(`/members/${id}/`, data, { headers: { 'Content-Type': 'multipart/form-data' } }),
  create: (data) => api.post('/members/', data),
  // update: (id, data) => api.patch(`/members/${id}/`, data),
  delete: (id) => api.delete(`/members/${id}/`),
  birthdaysToday: () => api.get('/members/birthdays_today/'),
  givingStatement: (id, year) => api.get(`/members/${id}/giving_statement/`, { params: { year }, responseType: 'blob' }),
}

export const discipleshipApi = {
  getTracks: () => api.get('/discipleship/tracks/'),
  getClasses: (params) => api.get('/discipleship/classes/', { params }),
  getEnrollments: (params) => api.get('/discipleship/enrollments/', { params }),
  enroll: (data) => api.post('/discipleship/enrollments/', data),
}

export const financeApi = {
  listTransactions: (params) => api.get('/finance/transactions/', { params }),
  getTransaction: (id) => api.get(`/finance/transactions/${id}/`),
  createTransaction: (data) => api.post('/finance/transactions/', data),
  summary: (params) => api.get('/finance/transactions/summary/', { params }),
  monthlyChart: (params) => api.get('/finance/transactions/monthly_chart/', { params }),
  getCategories: () => api.get('/finance/categories/'),
  getCauses: (params) => api.get('/finance/causes/', { params }),
  createCause: (data) => api.post('/finance/causes/', data),
  updateCause: (id, data) => api.patch(`/finance/causes/${id}/`, data),
  getPledges: (params) => api.get('/finance/pledges/', { params }),
  createPledge: (data) => api.post('/finance/pledges/', data),
  getBankAccounts: () => api.get('/finance/bank-accounts/'),
  downloadReceipt: (id) => api.get(`/finance/transactions/${id}/receipt/`, { responseType: 'blob' }),
  titheReport: (params) => api.get('/finance/transactions/tithe_report/', { params }),
}

export const eventsApi = {
  list: (params) => api.get('/events/', { params }),
  get: (id) => api.get(`/events/${id}/`),
  // create: (data) => api.post('/events/', data, { headers: { 'Content-Type': 'multipart/form-data' } }),
  // update: (id, data) => api.patch(`/events/${id}/`, data, { headers: { 'Content-Type': 'multipart/form-data' } }),
  create: (data) => api.post('/events/', data),
  update: (id, data) => api.patch(`/events/${id}/`, data),
  upcoming: () => api.get('/events/upcoming/'),
  getRegistrations: (params) => api.get('/events/registrations/', { params }),
  register: (data) => api.post('/events/registrations/', data),
  checkinByTicket: (ticket_ref) => api.post('/events/registrations/checkin-by-ticket/', { ticket_ref }),
  getAttendance: (params) => api.get('/events/attendance/', { params }),
  recordAttendance: (data) => api.post('/events/attendance/', data),
}

export const workersApi = {
  list: (params) => api.get('/workers/', { params }),
  get: (id) => api.get(`/workers/${id}/`),
  create: (data) => api.post('/workers/', data),
  update: (id, data) => api.patch(`/workers/${id}/`, data),
  getDepartments: () => api.get('/workers/departments/'),
  getPayrollRuns: (params) => api.get('/workers/payroll-runs/', { params }),
  createPayrollRun: (data) => api.post('/workers/payroll-runs/', data),
  generatePayroll: (id) => api.post(`/workers/payroll-runs/${id}/generate/`),
  approvePayroll: (id) => api.post(`/workers/payroll-runs/${id}/approve/`),
  getPayslips: (params) => api.get('/workers/payslips/', { params }),
  getLeaveRequests: (params) => api.get('/workers/leave-requests/', { params }),
  createLeaveRequest: (data) => api.post('/workers/leave-requests/', data),
  approveLeave: (id) => api.post(`/workers/leave-requests/${id}/approve/`),
  rejectLeave: (id, reason) => api.post(`/workers/leave-requests/${id}/reject/`, { reason }),
}

export const sermonsApi = {
  list: (params) => api.get('/sermons/', { params }),
  get: (id) => api.get(`/sermons/${id}/`),
  create: (data) => api.post('/sermons/', data, { headers: { 'Content-Type': 'multipart/form-data' } }),
  update: (id, data) => api.patch(`/sermons/${id}/`, data, { headers: { 'Content-Type': 'multipart/form-data' } }),
  getSeries: () => api.get('/sermons/series/'),
  getSpeakers: () => api.get('/sermons/speakers/'),
  generateSummary: (id) => api.post(`/sermons/${id}/generate-summary/`),
  transcribe: (id) => api.post(`/sermons/${id}/transcribe/`),
}

export const budgetApi = {
  getYears: () => api.get('/budget/years/'),
  getYear: (id) => api.get(`/budget/years/${id}/`),
  createYear: (data) => api.post('/budget/years/', data),
  approveYear: (id) => api.post(`/budget/years/${id}/approve/`),
  getCategories: () => api.get('/budget/categories/'),
  getLines: (params) => api.get('/budget/lines/', { params }),
  createLine: (data) => api.post('/budget/lines/', data),
  updateLine: (id, data) => api.patch(`/budget/lines/${id}/`, data),
}

export const inventoryApi = {
  list: (params) => api.get('/inventory/', { params }),
  get: (id) => api.get(`/inventory/${id}/`),
  create: (data) => api.post('/inventory/', data),
  update: (id, data) => api.patch(`/inventory/${id}/`, data),
  summary: () => api.get('/inventory/summary/'),
  getCategories: () => api.get('/inventory/categories/'),
  logMovement: (id, data) => api.post(`/inventory/${id}/log-movement/`, data),
}

export const procurementApi = {
  getVendors: (params) => api.get('/procurement/vendors/', { params }),
  createVendor: (data) => api.post('/procurement/vendors/', data),
  getRequests: (params) => api.get('/procurement/requests/', { params }),
  createRequest: (data) => api.post('/procurement/requests/', data),
  approveRequest: (id) => api.post(`/procurement/requests/${id}/approve/`),
  rejectRequest: (id, reason) => api.post(`/procurement/requests/${id}/reject/`, { reason }),
  getOrders: (params) => api.get('/procurement/orders/', { params }),
  createOrder: (data) => api.post('/procurement/orders/', data),
  markReceived: (id) => api.post(`/procurement/orders/${id}/mark-received/`),
}

export const communicationApi = {
  getTemplates: () => api.get('/communication/templates/'),
  getLogs: (params) => api.get('/communication/logs/', { params }),
  getBroadcasts: () => api.get('/communication/broadcasts/'),
  createBroadcast: (data) => api.post('/communication/broadcasts/', data),
  sendBroadcast: (id) => api.post(`/communication/broadcasts/${id}/send/`),
  retryLog: (id) => api.post(`/communication/logs/${id}/retry/`),
}

export const followupApi = {
  list: (params) => api.get('/followup/', { params }),
  get: (id) => api.get(`/followup/${id}/`),
  create: (data) => api.post('/followup/', data),
  update: (id, data) => api.patch(`/followup/${id}/`, data),
  close: (id, notes) => api.post(`/followup/${id}/close/`, { closure_notes: notes }),
  addLog: (id, data) => api.post(`/followup/${id}/add-log/`, data),
}

export const prayerApi = {
  list: (params) => api.get('/prayer/', { params }),
  create: (data) => api.post('/prayer/', data),
  update: (id, data) => api.patch(`/prayer/${id}/`, data),
  addUpdate: (id, text) => api.post(`/prayer/${id}/add-update/`, { update_text: text }),
  markAnswered: (id, testimony) => api.post(`/prayer/${id}/mark-answered/`, { testimony }),
  pray: (id) => api.post(`/prayer/${id}/pray/`),
}

export const auditApi = {
  getChecks: () => api.get('/audit/checks/'),
  dashboard: () => api.get('/audit/checks/dashboard/'),
  runAll: () => api.post('/audit/checks/run-all/'),
  runCheck: (id) => api.post(`/audit/checks/${id}/run/`),
  getReports: (params) => api.get('/audit/reports/', { params }),
  resolveReport: (id) => api.post(`/audit/reports/${id}/resolve/`),
}

export const facilityApi = {
  getRooms: () => api.get('/facility/rooms/'),
  getBookings: (params) => api.get('/facility/bookings/', { params }),
  createBooking: (data) => api.post('/facility/bookings/', data),
  approveBooking: (id) => api.post(`/facility/bookings/${id}/approve/`),
  getMaintenance: (params) => api.get('/facility/maintenance/', { params }),
  createMaintenance: (data) => api.post('/facility/maintenance/', data),
}

export const reportsApi = {
  finance: (params) => api.get('/reports/finance/', { params }),
  members: (params) => api.get('/reports/members/', { params }),
  attendance: (params) => api.get('/reports/attendance/', { params }),
  payroll: (params) => api.get('/reports/payroll/', { params }),
  tithes: (params) => api.get('/reports/tithes/', { params }),
  inventory: (params) => api.get('/reports/inventory/', { params }),
  audit: (params) => api.get('/reports/audit/', { params }),
  financeExcel: (params) => api.get('/reports/finance/', { params: { ...params, format: 'excel' }, responseType: 'blob' }),
  membersExcel: (params) => api.get('/reports/members/', { params: { ...params, format: 'excel' }, responseType: 'blob' }),
  payrollExcel: (params) => api.get('/reports/payroll/', { params: { ...params, format: 'excel' }, responseType: 'blob' }),
}
