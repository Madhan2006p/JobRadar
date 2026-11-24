# Reliability plan (Weeks 5–6)

**Goal:** make JobRadar something you can run, watch, break and fix, like a real on-call engineer.

**Start this only after Weeks 2–4.** You need Celery, Redis caching and throttling working first, or there is nothing to watch or break.

You write all of this (it's backend/ops work). I add a "service degraded" banner to the dashboard in Week 6. The detailed step-by-step guide (`backend/WEEK5.md`, with ✅ checks and hidden answers) is written when Week 5 starts. This file is the scope.

---

## Week 5: run it, watch it, get alerted

### 1. Run everything in Docker

Today only Postgres and Redis run in Docker. In Week 5, **one** `docker compose up` starts the whole app.

| Service | Image / command | Notes |
|---|---|---|
| `db` | `postgres:16` | already there |
| `redis` | `redis:7` | already there from Week 2 |
| `api` | your `backend/Dockerfile` + `gunicorn jobradar.wsgi` | not `runserver` (that is for development only) |
| `worker` | same image, `celery -A jobradar worker` | |
| `beat` | same image, `celery -A jobradar beat` | **only one** beat, never scale it |
| `frontend` | `nginx:alpine` serving `frontend/` | |

What you learn: a Dockerfile, image layers and caching, env vars instead of hard-coded settings, service names as hostnames (`db`, `redis` instead of `localhost`).

### 2. Metrics with Prometheus, dashboards with Grafana

Prometheus **pulls** numbers from each service every 15 seconds. Grafana draws them.

| What to see | Where the number comes from |
|---|---|
| Request rate (requests per second) | `django-prometheus` → `/metrics` on the API |
| Errors (4xx and 5xx per second) | `django-prometheus` (status codes) |
| Latency (p50, p95, p99) | `django-prometheus` (latency histogram) |
| Celery queue length | `redis_exporter`, reading the length of the `celery` list |
| Redis memory used | `redis_exporter` |
| Postgres connections, DB size | `postgres_exporter` |
| Disk free, CPU, memory | `node_exporter` |
| Is each service up? | Prometheus's own `up` metric |

New services: `prometheus`, `grafana`, `redis-exporter`, `postgres-exporter`, `node-exporter`, `alertmanager`.

**One dashboard, 4 rows** (the "golden signals"): traffic, errors, latency, saturation (queue length, Redis memory, disk).

**Stretch:** a custom metric `jobradar_last_fetch_success_timestamp` per source, from `FetchRun`. This catches the bug "everything is up but no new jobs for 6 hours", which normal metrics miss.

### 3. Alerts

Prometheus checks the rules. **Alertmanager** sends the message to Telegram, reusing your Week 3 bot.

| Alert | Fires when | For | Severity |
|---|---|---|---|
| `ApiDown` | API `/metrics` can't be reached | 1 min | critical |
| `HighErrorRate` | more than 5% of requests are 5xx | 5 min | critical |
| `SlowApi` | p95 latency above 500 ms | 10 min | warning |
| `CeleryQueueBacklog` | more than 1000 tasks waiting | 5 min | warning |
| `WorkerDown` | no Celery worker running | 2 min | critical |
| `RedisMemoryHigh` | above 80% of `maxmemory` | 5 min | warning |
| `DiskAlmostFull` | less than 10% disk free | 5 min | critical |
| `NoNewJobs` (stretch) | no successful fetch for 3 hours | — | warning |

The `For` column is important: it stops one slow second from waking you up at 3 a.m. Every alert must link to a runbook in `ops/runbooks/`.

---

## Week 6: break it, write it down, fix it

### 4. Break it on purpose (chaos experiments)

For each experiment: **write what you expect first**, then break it, watch Grafana and the alerts, and write down what really happened. Expectation vs reality is the learning.

| # | Break it | How | Questions to answer |
|---|---|---|---|
| 1 | Kill Redis | `docker compose stop redis` | Does `GET /jobs` still work, or does the cache/throttle give a 500? What does `POST /fetch` return? Does the worker reconnect by itself when Redis is back? |
| 2 | Kill a worker in the middle of a task | start a fetch, then `docker compose kill worker` | Is the task lost? Is `FetchRun` stuck on `running` forever? |
| 3 | Kill Postgres | `docker compose stop db` | What do users see? Does the API come back by itself when the DB is back? |
| 4 | Overload the API | `hey -z 60s -c 50 http://localhost:8000/jobs` (or Locust) | When does p95 go up? Do you get 429s from throttling? How many gunicorn workers do you need? |
| 5 | Flood the queue | queue 5000 tasks from `manage.py shell` | Does `CeleryQueueBacklog` fire? How long does the queue take to drain with 1 worker vs 3? |
| 6 | Slow job site | point a source at a URL that never answers | Does the worker hang forever? |
| 7 | Redis out of memory | set `maxmemory 20mb`, then fill it | What breaks first, the cache or the Celery queue? |
| 8 | Fill the disk | see the safety note below | What fails when Postgres can't write? Does `DiskAlmostFull` fire **before** that? |

> **Safety for #8:** never fill your real C: or E: drive. Run a second Postgres on a size-limited `tmpfs` (for example `size=300m`) in a separate `docker-compose.chaos.yml`, and fill that one.

### 5. Runbooks and postmortems

- **Runbook** = "if this alert fires, do these steps". Written **before** the incident, so a tired person at 3 a.m. can follow it. One per alert. Template: [runbooks/TEMPLATE.md](runbooks/TEMPLATE.md).
- **Postmortem** = "what happened, why, and what we changed". Written **after** each experiment. Blameless: it talks about systems, not people. Template: [postmortems/TEMPLATE.md](postmortems/TEMPLATE.md).

### 6. The fixes

Each fix must point to the experiment that proved it was needed. After the fix, run that experiment again and show the better result.

| Fix | Where | Fixes experiment |
|---|---|---|
| `healthcheck:` for every service (`pg_isready`, `redis-cli ping`, API `/health/ready`) and `depends_on: condition: service_healthy` | `docker-compose.yml` | 1, 3 |
| `restart: unless-stopped` | `docker-compose.yml` | 2, 3 |
| `/health` (liveness: "the process is alive") vs `/health/ready` (readiness: "DB and Redis answer", else 503) | `jobradar/views.py` | 1, 3 |
| Timeouts everywhere: `requests` connect/read timeout, DB `connect_timeout` and `statement_timeout`, Redis socket timeout, gunicorn `--timeout`, Celery `soft_time_limit` / `time_limit` | settings, sources, tasks | 4, 6 |
| Retries with backoff **and jitter**, only for work that is safe to repeat | `tasks.py` | 1, 6 |
| `acks_late=True`, `worker_prefetch_multiplier=1`, `task_reject_on_worker_lost=True` | Celery settings | 2 |
| Mark old `running` FetchRuns as `failed` | a small Beat task | 2 |
| A cache failure falls back to the DB instead of a 500 | `jobs/cache.py`, views | 1 |
| `POST /fetch` returns 503 when the broker is down, not 500 | `jobs/views.py` | 1 |
| A separate Redis (or DB number + eviction policy) for the cache and for the Celery queue | compose + settings | 7 |
| Redis AOF persistence for the queue | `redis` command | 1, 7 |
| Redis replica + **Sentinel** | compose + `sentinel://` broker URL | 1 |
| Memory limits per container | `docker-compose.yml` | 4, 7 |
| Cleanup task that deletes jobs older than N days | Beat task | 8 |

> **Honest note on the Redis replica:** a replica alone only **copies** data. If the primary dies, nothing switches over by itself. Automatic failover needs **Redis Sentinel** (3 sentinels so they can vote), and the clients (Celery, Django cache) must connect through Sentinel. Do the replica first, see that it does **not** fail over, then add Sentinel. That's a great interview story.

### 7. Deploy

Last step: run the same compose file on one small cloud VM (or a free tier), with secrets in a `.env` that is not in git.

---

## Done when

- [ ] `docker compose up` starts all services; the dashboard works at `http://localhost:5500`
- [ ] Grafana dashboard with traffic, errors, latency and saturation
- [ ] All the alerts above, each linked to a runbook; a test alert reaches Telegram
- [ ] 8 experiments done, each with a postmortem in `ops/postmortems/`
- [ ] Each fix re-tested with the same experiment, with before/after Grafana screenshots
- [ ] README: architecture diagram including monitoring

## Why this is worth it

Most junior portfolios stop at "it works on my laptop". With this, you can answer the interview questions *"what happens when Redis goes down?"* and *"how do you know your service is healthy?"* from things you really did, with screenshots and postmortems to show.
