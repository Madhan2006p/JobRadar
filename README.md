# JobRadar

JobRadar collects new job posts every hour, saves them in PostgreSQL, and alerts you when a job matches your skills.

## Team

| Role | Engineer | Folder |
|---|---|---|
| Backend (API, database, Redis, Celery) | Madhan | `backend/` |
| Ops (Docker, monitoring, alerts, runbooks) | Madhan | `ops/` |
| Frontend (dashboard) | Claude | `frontend/` |

The two sides talk only through the API described in [docs/api-contract.md](docs/api-contract.md). If either side wants to change an endpoint, update the contract first.

## Plan

| Week | Goal | Status |
|---|---|---|
| 1 | Django REST Framework + PostgreSQL in Docker: `/jobs` list, get, create, delete | Done |
| 2 | Celery + Redis: fetch jobs every hour, retries ([backend/WEEK2.md](backend/WEEK2.md)) | In progress |
| 3 | Redis caching, rate limiting, match alerts | Not started |
| 4 | SQL stats, dashboard charts, README diagram | Not started |
| 5 | Run everything in Docker, Prometheus + Grafana dashboards, alerts | Not started |
| 6 | Break it on purpose, runbooks + postmortems, add the fixes, deploy | Not started |

Week 1 steps for the backend: [backend/WEEK1.md](backend/WEEK1.md)
Weeks 5–6 plan (reliability): [ops/RELIABILITY.md](ops/RELIABILITY.md)

## Run the frontend

```bash
python -m http.server 5500 --directory frontend
```

Then open http://localhost:5500. If the backend is not running, the dashboard shows sample data and says so at the top.
