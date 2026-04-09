# ChurchOS — Church Management System

A complete, production-ready church management platform built with **Django 5**, **Django REST Framework**, **Vue 3**, and **Bootstrap 5**.

---

## 🏗️ Architecture

| Layer | Technology |
|-------|-----------|
| Backend API | Django 5, Django REST Framework, SimpleJWT |
| Frontend SPA | Vue 3 (Composition API), Pinia, Vue Router 4 |
| UI Framework | Bootstrap 5, Bootstrap Icons |
| Charts | Chart.js + vue-chartjs |
| Database | PostgreSQL 16 |
| Cache / Broker | Redis 7 |
| Async Tasks | Celery + Celery Beat |
| AI Features | Anthropic Claude API, OpenAI Whisper |
| Messaging | Twilio (SMS), WhatsApp Cloud API, SendGrid |
| Payments | Paystack |

---

## 📦 Modules

1. **Member Management** — Registration, profiles, family links, ID cards
2. **Finance & Payments** — Tithes, offerings, donations, causes, pledges, receipts
3. **Communication** — Email, SMS, WhatsApp broadcasts and birthday automation
4. **Events** — Registration, QR ticket check-in, attendance tracking
5. **Member Follow-Up** — Pastoral care CRM with contact logs
6. **Sermons & Media** — Archive with AI transcription & summary
7. **Workers & Payroll** — Staff HR, salary, leave, payslips
8. **Inventory** — Asset registry, movements, depreciation
9. **Procurement** — Purchase requests → PO workflow with approvals
10. **Budget** — Annual budgeting, variance tracking, amendments
11. **Prayer Requests** — Submit, track, close with privacy tiers
12. **Discipleship** — Tracks, classes, enrollments, certificates
13. **Facility Management** — Room bookings, maintenance requests
14. **Self-Audit Engine** — Automated financial & data integrity checks
15. **AI Assistant** — Insights, forecasts, weekly briefings, sermon summaries
16. **Communication Hub** — Broadcast manager with delivery tracking
17. **Reports** — PDF/Excel export for all modules
18. **System Settings** — Branding, colors, logo, integrations — all configurable

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- PostgreSQL 16
- Redis 7

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials and API keys

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load initial audit checks
python manage.py shell -c "
from apps.audit.models import AuditCheck
checks = [
    {'name': 'Unreceipted Transactions', 'category': 'finance', 'severity': 'warning', 'check_function': 'run_check_unreceipted_transactions', 'description': 'Transactions older than 7 days with no receipt PDF.'},
    {'name': 'Unverified Expenses', 'category': 'finance', 'severity': 'critical', 'check_function': 'run_check_unverified_transactions', 'description': 'High-value expenses with no secondary verification.'},
    {'name': 'Members Without Contact Info', 'category': 'data', 'severity': 'warning', 'check_function': 'run_check_members_no_contact', 'description': 'Active members with no phone or email.'},
    {'name': 'Workers Without Payroll', 'category': 'compliance', 'severity': 'warning', 'check_function': 'run_check_workers_no_payroll', 'description': 'Active workers missing payslips for 60+ days.'},
    {'name': 'Stale Purchase Orders', 'category': 'finance', 'severity': 'warning', 'check_function': 'run_check_open_procurement', 'description': 'Purchase orders open for more than 30 days.'},
    {'name': 'Duplicate Transactions', 'category': 'finance', 'severity': 'critical', 'check_function': 'run_check_duplicate_transactions', 'description': 'Potential duplicate transaction entries.'},
]
for c in checks:
    AuditCheck.objects.get_or_create(check_function=c['check_function'], defaults=c)
print('Audit checks created.')
"

# Start development server
python manage.py runserver

# In another terminal — start Celery worker
celery -A churchos worker -l INFO

# In another terminal — start Celery beat
celery -A churchos beat -l INFO
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server (proxies API to localhost:8000)
npm run dev

# Build for production
npm run build
```

### Docker (Full Stack)

```bash
# From project root
cp backend/.env.example backend/.env
# Edit backend/.env

docker compose up -d

# The app will be available at http://localhost
# Django admin at http://localhost/admin
# API docs at http://localhost/api/docs
```

---

## 👥 User Roles

| Role | Level | Access |
|------|-------|--------|
| Super Admin | 7 | Full system access |
| Administrator | 6 | All modules except system config |
| Finance Officer | 5 | Finance, budget, payroll |
| Pastor | 5 | Members, follow-up, sermons, events |
| Secretary | 4 | Members, events, communication |
| Cell Leader | 3 | Own cell group only |
| Data Entry Clerk | 2 | Record transactions, register members |

---

## 🤖 AI Features

Set `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` in your `.env`, then enable AI in Settings → Integrations.

- **Sermon Transcription** — Upload audio → Whisper transcription
- **Sermon Summary** — AI generates key points and scripture list
- **Weekly Briefing** — Monday morning email digest for pastors
- **Financial Insights** — Natural language data queries
- **Giving Forecast** — AI-powered income predictions
- **Audit Explanations** — Plain-language anomaly descriptions

---

## 🔔 Automated Tasks (Celery Beat)

| Task | Schedule |
|------|----------|
| Birthday greetings | Daily 6:00 AM |
| Pledge reminders | Daily 8:00 AM |
| Event reminders | Every hour |
| Absentee detection | Every Monday 7:00 AM |
| Daily audit checks | Daily 2:00 AM |
| AI weekly briefing | Monday 7:30 AM |

---

## 📁 Project Structure

```
churchos/
├── backend/
│   ├── apps/
│   │   ├── core/          # ChurchSettings, BaseModel, permissions
│   │   ├── accounts/      # Custom User, JWT auth, roles
│   │   ├── members/       # Member management
│   │   ├── finance/       # Transactions, causes, pledges
│   │   ├── communication/ # Email, SMS, WhatsApp
│   │   ├── events/        # Events, registration, attendance
│   │   ├── workers/       # Staff, payroll, leave
│   │   ├── sermons/       # Sermon archive, AI features
│   │   ├── budget/        # Annual budgets, variance
│   │   ├── inventory/     # Asset registry
│   │   ├── procurement/   # Purchase workflow
│   │   ├── followup/      # Pastoral care CRM
│   │   ├── prayer/        # Prayer requests
│   │   ├── discipleship/  # Tracks, classes
│   │   ├── facility/      # Room bookings, maintenance
│   │   └── audit/         # Self-audit engine
│   ├── churchos/          # Django project config
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/           # Axios API client
│   │   ├── assets/        # CSS, global styles
│   │   ├── components/    # Layout, common components
│   │   ├── router/        # Vue Router
│   │   ├── stores/        # Pinia stores (auth, settings)
│   │   └── views/         # All page views (18 modules)
│   └── package.json
└── docker-compose.yml
```

---

## 🌐 API Documentation

- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI schema: `http://localhost:8000/api/schema/`

---

## 📄 License

MIT License — free to use and modify for your church.
