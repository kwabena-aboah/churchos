# ChurchOS — Render.com Deployment Guide

This guide walks you through deploying ChurchOS on [Render.com](https://render.com) using the included `render.yaml` blueprint. The entire stack — backend API, Celery workers, database, Redis, and frontend — deploys automatically.

---

## Architecture on Render

```
┌─────────────────────────────────────────────────────────────┐
│                        Render.com                           │
│                                                             │
│  ┌──────────────────┐     ┌──────────────────────────────┐  │
│  │  Static Site     │────▶│  Web Service (Django API)    │  │
│  │  churchos-       │     │  churchos-api                │  │
│  │  frontend        │     │  gunicorn + whitenoise       │  │
│  └──────────────────┘     └──────────┬───────────────────┘  │
│                                      │                       │
│                            ┌─────────▼──────────┐           │
│  ┌──────────────────┐      │  PostgreSQL         │           │
│  │  Worker          │      │  churchos-db        │           │
│  │  Celery Worker   │      └────────────────────-┘           │
│  └──────────────────┘                                        │
│  ┌──────────────────┐      ┌────────────────────┐           │
│  │  Worker          │      │  Redis              │           │
│  │  Celery Beat     │      │  churchos-redis     │           │
│  └──────────────────┘      └────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

**Monthly cost on free tier:** $0 (with limitations — see notes below)  
**Monthly cost on paid tier:** ~$31/month (3× $7 web/worker + $7 Redis + $7 Postgres)

---

## Prerequisites

1. A [Render.com](https://render.com) account (free)
2. This codebase pushed to a **GitHub** or **GitLab** repository
3. (Optional but recommended) A SendGrid account for email
4. (Optional) Anthropic API key for AI features

---

## Step 1 — Push to GitHub

```bash
cd churchos
git init
git add .
git commit -m "Initial ChurchOS deployment"
git remote add origin https://github.com/YOUR_USERNAME/churchos.git
git push -u origin main
```

---

## Step 2 — Deploy via Blueprint

1. Log in to [dashboard.render.com](https://dashboard.render.com)
2. Click **New +** → **Blueprint**
3. Connect your GitHub/GitLab account if not already connected
4. Select your `churchos` repository
5. Render detects `render.yaml` automatically
6. Click **Apply** — Render creates all services in dependency order:
   - PostgreSQL database first
   - Redis instance
   - Django API web service
   - Celery worker
   - Celery beat scheduler
   - Vue 3 frontend static site

---

## Step 3 — Set Secret Environment Variables

After the blueprint applies, some variables are marked `sync: false` — you must set these manually.

Go to each service → **Environment** tab → add:

### churchos-api (and copy to celery-worker):

| Variable | Value | Where to get it |
|---|---|---|
| `EMAIL_HOST_PASSWORD` | `SG.xxxxxxxx` | [SendGrid](https://sendgrid.com) → Settings → API Keys |
| `DEFAULT_FROM_EMAIL` | `noreply@yourchurch.org` | Your church email |
| `ANTHROPIC_API_KEY` | `sk-ant-xxxxx` | [console.anthropic.com](https://console.anthropic.com) |
| `OPENAI_API_KEY` | `sk-xxxxx` | [platform.openai.com](https://platform.openai.com) (for Whisper) |
| `TWILIO_ACCOUNT_SID` | `ACxxxxx` | [twilio.com/console](https://twilio.com/console) |
| `TWILIO_AUTH_TOKEN` | `xxxxx` | Twilio Console |
| `WHATSAPP_API_TOKEN` | `xxxxx` | Meta Business → WhatsApp |
| `PAYSTACK_SECRET_KEY` | `sk_live_xxxxx` | [paystack.com](https://paystack.com) |

> **Tip:** Use Render's **Environment Groups** (Settings → Environment Groups) to share variables across services without duplicating them.

---

## Step 4 — Update CORS and Frontend URL

After the first deploy, Render assigns URLs like:
- API: `https://churchos-api.onrender.com`
- Frontend: `https://churchos-frontend.onrender.com`

Update the **churchos-api** service environment:
```
CORS_ALLOWED_ORIGINS = https://churchos-frontend.onrender.com
```

Update the **churchos-frontend** service environment:
```
VITE_API_BASE_URL = https://churchos-api.onrender.com/api/v1
```

Then **manually deploy** both services (or push a commit to trigger redeploy).

---

## Step 5 — Create Superuser

After the API service is running, open a **Shell** in the Render dashboard (churchos-api → Shell tab):

```bash
DJANGO_ENV=render python manage.py createsuperuser
```

Enter your email, first name, last name, and password. This is your initial admin account.

---

## Step 6 — Configure Church Settings

1. Open your frontend: `https://churchos-frontend.onrender.com`
2. Log in with the superuser credentials
3. Go to **Settings** (bottom of sidebar)
4. Fill in:
   - Church Name, Address, Phone
   - Upload Logo
   - Set Primary/Accent Colors
   - Configure Email, SMS, WhatsApp credentials
   - Enable AI features if you have API keys
5. Click **Save Changes**
6. Go to **Settings → Users** → create accounts for your team

---

## Custom Domain (Optional)

### Backend (API)
1. churchos-api → Settings → Custom Domains
2. Add your API domain e.g. `api.yourchurch.org`
3. Add a CNAME record in your DNS: `api.yourchurch.org → churchos-api.onrender.com`
4. Update `ALLOWED_HOSTS` env var: `api.yourchurch.org,.onrender.com`
5. Update `CORS_ALLOWED_ORIGINS` with your frontend custom domain

### Frontend
1. churchos-frontend → Settings → Custom Domains
2. Add e.g. `app.yourchurch.org`
3. Add CNAME in DNS: `app.yourchurch.org → churchos-frontend.onrender.com`
4. Update `VITE_API_BASE_URL` to point to your backend custom domain

---

## Persistent Media Files (Important)

Render's free and starter plans have **ephemeral storage** — files uploaded by users (member photos, sermon audio, documents) are lost when the service restarts.

**Solution: Enable S3 storage**

1. Create an AWS S3 bucket (or use Cloudflare R2 — cheaper)
2. Add these env vars to `churchos-api`:
```
AWS_ACCESS_KEY_ID=xxxx
AWS_SECRET_ACCESS_KEY=xxxx
AWS_STORAGE_BUCKET_NAME=churchos-media
AWS_S3_REGION_NAME=us-east-1
```
3. Uncomment the S3 block in `backend/churchos/settings/render.py`
4. Redeploy

---

## Free Tier Limitations

| Service | Free Tier Limit | Impact |
|---|---|---|
| Web services | Spin down after 15 min inactivity | First request takes ~30s to wake |
| PostgreSQL | 256MB storage, deleted after 90 days | Upgrade to Starter ($7/mo) |
| Redis | 25MB, no persistence | Sessions lost on restart |
| Workers | 750 hours/month total across all services | Celery may not run 24/7 |

**For production use**, upgrade at minimum:
- `churchos-api` → Starter ($7/mo) — always-on, no spin-down
- `churchos-db` → Starter ($7/mo) — persistent, no expiry
- `churchos-redis` → Starter ($10/mo) — persistent

Total: ~$24/month for a reliable production deployment.

---

## Monitoring & Logs

- **Logs:** Each service → Logs tab (real-time streaming)
- **Metrics:** Each service → Metrics tab (CPU, memory, requests)
- **Alerts:** Account Settings → Notifications (email on deploy fail, high error rate)
- **Django Admin:** `https://churchos-api.onrender.com/admin/`
- **API Docs:** `https://churchos-api.onrender.com/api/docs/`

---

## Redeploy on Code Change

Render automatically redeploys when you push to your connected branch:
```bash
git add .
git commit -m "Your change"
git push origin main
```

The `render_build.sh` script runs on every deploy:
1. Installs dependencies
2. Collects static files
3. Runs migrations (safe — only applies new ones)
4. Seeds initial data (idempotent — safe to run repeatedly)

---

## Troubleshooting

**Build fails with `ModuleNotFoundError`**
→ Check `requirements.txt` includes all packages. Redeploy.

**`ALLOWED_HOSTS` error**
→ Add your Render URL to the `ALLOWED_HOSTS` env var: `.onrender.com`

**Frontend shows "Network Error" / API calls fail**
→ Check `VITE_API_BASE_URL` is set to the correct backend URL
→ Check `CORS_ALLOWED_ORIGINS` includes your frontend URL

**Celery tasks not running**
→ Check the `churchos-celery-worker` and `churchos-celery-beat` services are running
→ Check `REDIS_URL` is set on both worker services

**Media files not loading after redeploy**
→ Set up S3 storage (see above) — ephemeral disk is wiped on redeploy

**Database migration failed**
→ Shell into `churchos-api` → run `DJANGO_ENV=render python manage.py migrate --no-input`
