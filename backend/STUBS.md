# Backend stubs (Django REST Framework)

Every backend file already exists. Each class or function has a docstring that says exactly what it must do. Unfinished functions raise `NotImplementedError("TODO Week N: ...")`, and unfinished models and serializers say `TODO Week N` in their docstring. Your job is to replace the TODOs with real code, one at a time.

**How to work through this**
1. Pick the next unticked item in the week you are on.
2. Read its docstring and the contract in [../docs/api-contract.md](../docs/api-contract.md).
3. Write the code, then test it in the browsable API (open http://localhost:8000/jobs in the browser) or with `python manage.py test`.
4. Tick the box here and commit.

**How Django REST Framework splits the work**

| Layer | File | Job |
|---|---|---|
| Model | `models.py` | The table. Django turns it into SQL with migrations. |
| Serializer | `serializers.py` | Model ⇄ JSON, plus input validation (400 errors). |
| View / ViewSet | `views.py` | HTTP: which serializer, which queryset, status codes. |
| URLs | `urls.py` | Path → view. A router builds the `/jobs` and `/jobs/{id}` paths. |
| Task | `tasks.py` | Background work with Celery (Week 2+). |

---

## Files

```text
backend/
├── STUBS.md               ← this file
├── WEEK1.md               ← step-by-step guide for Week 1
├── requirements.txt       ← Week 2+ packages are commented out
├── manage.py              ← runserver, makemigrations, migrate, test, shell
├── jobradar/              ← project config
│   ├── settings.py        ← done: DB, DRF, CORS from env vars (Week 2–3 parts commented)
│   ├── urls.py            ← includes each app (Week 3–4 commented)
│   ├── views.py           ← /health
│   ├── celery.py          ← Week 2
│   └── wsgi.py
├── jobs/                  ← Week 1–3
│   ├── models.py          ← Job (Week 1), FetchRun (Week 2)
│   ├── serializers.py     ← JobSerializer
│   ├── views.py           ← JobViewSet (Week 1), fetch views (Week 2)
│   ├── urls.py
│   ├── admin.py           ← optional admin page
│   ├── tasks.py           ← Week 2 Celery tasks
│   ├── sources/           ← Week 2 (arbeitnow.py, remoteok.py)
│   ├── skills.py          ← Week 2
│   ├── cache.py           ← Week 3 Redis cache
│   └── tests.py
├── alerts/                ← Week 3
│   ├── models.py  serializers.py  views.py  urls.py
│   ├── tasks.py           ← match_new_jobs, send_alert
│   └── notify.py          ← Telegram / email
└── reports/               ← Week 4 (raw SQL on purpose)
    ├── queries.py  views.py  urls.py

ops/                       ← Weeks 5–6 (in the JobRadar root, next to backend/)
├── RELIABILITY.md         ← the plan: metrics, alerts, experiments, fixes
├── runbooks/TEMPLATE.md   ← "if this alert fires, do this"
└── postmortems/TEMPLATE.md← "what broke, why, what we changed"
```

In Week 5 you also add `backend/Dockerfile`, and `ops/prometheus.yml`, `ops/alerts.yml`, `ops/alertmanager.yml` and `ops/grafana/`.

`docker-compose.yml` is not created on purpose: you write it in WEEK1.md Step 1. There is no `schema.sql`: Django **migrations** create the tables.

---

## All endpoints

| Week | Method | Path | Code | Success | Errors |
|---|---|---|---|---|---|
| 1 | GET | `/health` | `jobradar/views.health` | 200 | |
| 1 | GET | `/jobs?search=&limit=&offset=&ordering=` | `JobViewSet` (list) | 200 | |
| 1 | GET | `/jobs/{id}` | `JobViewSet` (retrieve) | 200 | 404 |
| 1 | POST | `/jobs` | `JobViewSet` (create) | 201 | 400 (also duplicate url) |
| 1 | DELETE | `/jobs/{id}` | `JobViewSet` (destroy) | 204 | 404 |
| 2 | POST | `/fetch?source=all` | `jobs/views.start_fetch` | 202 | 400 unknown source |
| 2 | GET | `/tasks/{task_id}` | `jobs/views.task_status` | 200 | |
| 2 | GET | `/sources` | `jobs/views.list_sources` | 200 | |
| 3 | GET | `/alerts` | `AlertViewSet` (list) | 200 | |
| 3 | POST | `/alerts` | `AlertViewSet` (create) | 201 | 400 |
| 3 | DELETE | `/alerts/{id}` | `AlertViewSet` (destroy) | 204 | 404 |
| 3 | GET | `/alerts/{id}/matches` | `AlertViewSet.matches` (@action) | 200 | 404 |
| 3 | all | (every endpoint) | DRF throttling in Redis | | 429 |
| 4 | GET | `/stats/summary` | `reports/views.summary` | 200 | |
| 4 | GET | `/stats/jobs-per-day?days=14` | `reports/views.jobs_per_day` | 200 | 400 |
| 4 | GET | `/stats/top-skills?limit=10` | `reports/views.top_skills` | 200 | 400 |
| 4 | GET | `/stats/top-companies?limit=10` | `reports/views.top_companies` | 200 | 400 |
| 5 | GET | `/metrics` | `django-prometheus` (Prometheus reads it) | 200 | |
| 6 | GET | `/health/ready` | `jobradar/views.ready` (checks DB + Redis) | 200 | 503 |

---

## Week 1: Django + DRF + PostgreSQL

Guide: [WEEK1.md](WEEK1.md)

**Setup**
- [ ] `docker-compose.yml`: PostgreSQL service (Step 1)
- [ ] venv + `pip install -r requirements.txt` + `python manage.py check` (Step 2)

**Model** (`jobs/models.py`)
- [ ] `Job`: 9 fields, `Meta` (ordering + index), `__str__`
- [ ] `makemigrations` → read the SQL with `sqlmigrate jobs 0001` → `migrate`
- [ ] (optional) `jobs/admin.py`: register Job, `createsuperuser`

**API**
- [ ] `jobradar/views.health` → `GET /health`
- [ ] `JobSerializer`: `Meta` + `validate_skills`
- [ ] `JobViewSet`: `queryset`, `serializer_class`, `search_fields`, `ordering_fields`

**Tests** (`jobs/tests.py`, class `JobApiTests`)
- [ ] Replace the 8 `skipTest` lines with real tests → `python manage.py test jobs`

---

## Week 2: Celery + Redis background fetching

Add Redis to `docker-compose.yml` (`image: redis:7`, port 6379). Uncomment the Week 2 packages in `requirements.txt`, and the Celery parts of `jobradar/__init__.py`, `jobradar/celery.py` and `settings.py`.

**Model**
- [ ] `FetchRun` (uncomment in `jobs/models.py`) + migrate

**Sources and skills**
- [ ] `skills.normalize_skill`, `skills.extract_skills` (+ 4 `SkillTests`)
- [ ] `sources/arbeitnow.py`: `fetch_raw`, `normalize`, `fetch`
- [ ] `sources/remoteok.py`: `fetch_raw` (skip first item), `normalize`, `fetch`

**Celery** (`jobs/tasks.py`)
- [ ] `fetch_source(source_name)`: `bulk_create(ignore_conflicts=True)`, FetchRun log, retries
- [ ] `fetch_all_sources()`: one task per source (`group`), run hourly by Beat

**Endpoints** (`jobs/views.py`, then uncomment the paths in `jobs/urls.py`)
- [ ] `start_fetch` → `POST /fetch` (202)
- [ ] `task_status` → `GET /tasks/{task_id}`
- [ ] `list_sources` → `GET /sources` (`SourceSerializer`)

---

## Week 3: Redis cache, throttling, alerts

**Redis cache and throttling**
- [ ] `settings.py`: uncomment `CACHES` (Redis) and the throttle settings
- [ ] `jobs/cache.py`: `jobs_version`, `bump_jobs_version`, `cache_key`
- [ ] `JobViewSet.list` uses the cache; `perform_create` / `perform_destroy` bump the version
- [ ] `fetch_source` bumps the version when it saves new jobs

**Alerts app** (uncomment `alerts.urls` in `jobradar/urls.py`)
- [ ] `alerts/models.py`: `Alert`, `AlertMatch` (+ `GinIndex` on `Job.skills`) + migrate
- [ ] `AlertSerializer` (+ `validate`), `AlertMatchSerializer`
- [ ] `AlertViewSet` + `@action matches` (with `select_related`)
- [ ] `alerts/tasks.py`: `match_new_jobs` (idempotent with `get_or_create`), `send_alert` (retries)
- [ ] `alerts/notify.py`: `format_job_message`, `send_telegram`, `send_email` (log-only without keys)

---

## Week 4: raw SQL stats + polish

Uncomment `reports.urls` in `jobradar/urls.py`.

- [ ] `reports/queries.py`: `summary` (`FILTER`), `jobs_per_day` (`generate_series` + `LEFT JOIN`), `top_skills` (`unnest`), `top_companies`
- [ ] `reports/views.py`: 4 views, validate `days` / `limit` (400 if bad)
- [ ] `settings.py`: `CONN_MAX_AGE` (reuse DB connections)
- [ ] Find and fix one N+1 query with `select_related` / `prefetch_related`
- [ ] README: architecture diagram + how to run everything

---

## Weeks 5–6: reliability (Docker, monitoring, chaos, fixes)

Plan and details: [../ops/RELIABILITY.md](../ops/RELIABILITY.md)

**Week 5: run it, watch it, get alerted**
- [ ] `backend/Dockerfile` + compose services `api` (gunicorn), `worker`, `beat`, `frontend`
- [ ] `django-prometheus` → `GET /metrics`
- [ ] Prometheus + exporters (redis, postgres, node) + Grafana dashboard: traffic, errors, latency, saturation
- [ ] Alert rules + Alertmanager → Telegram; one runbook per alert

**Week 6: break it, write it down, fix it**
- [ ] 8 experiments (kill Redis, kill worker, kill Postgres, overload, flood queue, slow site, Redis OOM, full disk), each with a postmortem
- [ ] Fixes: healthchecks, restart policy, `/health/ready`, timeouts, retries + jitter, `acks_late`, Redis replica + Sentinel, memory limits
- [ ] Re-run each experiment after its fix, with before/after screenshots
- [ ] Deploy to one cloud VM

---

## Frontend status (Claude)

| Endpoint | Dashboard |
|---|---|
| `GET /health`, `GET /jobs`, `POST /jobs`, `DELETE /jobs/{id}` | Done, in DRF format (uses sample data until your API is up) |
| `POST /fetch`, `GET /tasks/{id}`, `GET /sources` | Done: **Fetch now** button + **Sources** panel (shows "Available after Week 2" until `/sources` exists) |
| Week 3–4 endpoints | Built when you start each week |
| `GET /health/ready` (Week 6) | "Service degraded" banner when it returns 503 |
