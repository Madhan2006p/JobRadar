# Week 2: Redis + Celery background fetching

**Goal:** every hour, a Celery worker fetches new jobs from 2 public job APIs, tags their skills, and saves only the new ones. Redis is the queue in between. You can also start a fetch by hand with `POST /fetch` and watch it with `GET /tasks/{id}`.

These are exactly the topics you got stuck on in the data engineer interview: Redis commands, Celery, and web data. After this week, you'll answer them from your own code.

**Same rules as Week 1:** you type the code, every step has a ✅ **Check**, and answers are hidden under "Show answer". You said you'll write the tests yourself from now on, so Step 10 gives only test ideas and hints.

**How the pieces fit**

```text
                 POST /fetch ──┐                    every hour
                               ▼                        │
 Django (runserver) ──.delay()──► Redis (queue) ◄── Celery Beat
                                     │
                                     ▼
                              Celery worker ──► Arbeitnow / Remote OK APIs
                                     │
                                     ▼
                     PostgreSQL (jobs_job, jobs_fetchrun)
```

- **Django** never does the slow work. It only puts a message in Redis and answers **202** at once.
- **The worker** is a separate process that takes messages from Redis and runs the task.
- **Beat** is a third process: a clock that adds a message to the queue every hour.

---

## Step 1: Redis in Docker + your first Redis commands

Add Redis to `JobRadar/docker-compose.yml`, under `services:` and next to `db:`:

```yaml
  redis:
    image: redis:7
    ports:
      - "6379:6379"
```

```bash
docker compose up -d
```

✅ **Check:** `docker compose exec redis redis-cli ping` prints `PONG`.

**Practise the commands you were asked about** (10 minutes). Open the Redis shell:
```bash
docker compose exec redis redis-cli
```
```text
SET user:1 "Madhan"          # store a string
GET user:1                   # read it
EXPIRE user:1 30             # delete it after 30 seconds
TTL user:1                   # seconds left (-1 = no expiry, -2 = gone)
INCR page_views              # +1, atomic (safe with many users at once)
LPUSH jobs "a" "b"           # push to a list (this is how a queue works)
RPOP jobs                    # take from the other end
LLEN jobs                    # list length
HSET job:1 title "Dev" company "Acme"   # a hash = small dict
HGETALL job:1
KEYS *                       # OK here, but NEVER in production (it blocks Redis)
SCAN 0                       # the safe way to list keys, a few at a time
FLUSHALL                     # delete everything (local only!)
```

**Learn:** Redis keeps everything **in memory**, so it's very fast, but RAM is limited. That's why we use `EXPIRE`. Celery uses a Redis **list** as its queue: `LPUSH` on one side, worker pops on the other.

---

## Step 2: Install the Week 2 packages

In `backend/requirements.txt`, uncomment `celery`, `redis` and `requests`. Then:
```bash
pip install -r requirements.txt
```

---

## Step 3: Connect Celery to Django

Three small changes. The code is already written as comments, so you uncomment it and read it.

1. `jobradar/celery.py`: uncomment the code in the docstring and make it real code.
2. `jobradar/__init__.py`: uncomment the 2 lines. This loads Celery when Django starts.
3. `jobradar/settings.py`: uncomment the `CELERY_...` block.

Then add a tiny test task at the end of `jobs/tasks.py`:
```python
@shared_task
def ping():
    return "pong"
```

Start a worker in a **new terminal** (from `backend`, venv on):
```bash
celery -A jobradar worker -l info
```
On native Windows (not WSL), add `--pool=solo`. In WSL you don't need it.

✅ **Check:** the worker prints `[tasks]` with `jobs.tasks.ping` in the list, then `ready`.

Now send it a task from the Django shell (another terminal):
```bash
python manage.py shell
```
```python
from jobs.tasks import ping
r = ping.delay()      # puts a message in Redis, returns at once
r.id                  # the task id
r.status              # 'SUCCESS' after a moment
r.get(timeout=5)      # 'pong'
```

**See the queue with your own eyes:**
1. Stop the worker (Ctrl+C).
2. Run `ping.delay()` 3 times in the shell.
3. In `redis-cli`, run `LLEN celery`. It shows **3**: three messages waiting.
4. Start the worker again. It runs all 3, and `LLEN celery` is **0**.

That's what a message queue is.

**Learn:**
- **Broker** = where messages wait (Redis list `celery`).
- **Result backend** = where results are stored (Redis keys `celery-task-meta-<id>`).
- `.delay()` only **sends**. `.get()` **waits** for the result, so never call `.get()` inside a web request: it would block the request, which defeats the point.

---

## Step 4: The `FetchRun` model

In `jobs/models.py`, uncomment `FetchRun` and read every line. Then:
```bash
python manage.py makemigrations jobs
```
```bash
python manage.py sqlmigrate jobs 0002
```
```bash
python manage.py migrate
```

**Learn:** `TextChoices` limits `status` to 3 values. The index on `(source, -started_at)` makes "latest run per source" fast, and you'll need that in Step 9.

Optional: register `FetchRun` in `jobs/admin.py` so you can watch runs appear in `/admin`.

---

## Step 5: `skills.py` (find skills in text)

Open `jobs/skills.py`. Write `normalize_skill` and `extract_skills`.

**Try it yourself** in the Django shell as you go:
```python
from jobs.skills import extract_skills
extract_skills("Python and Redis developer, good with Postgres")   # ['postgresql', 'python', 'redis']
extract_skills("good communication")                              # []   ('go' must NOT match 'good')
extract_skills("C++ and Node.js")                                 # ['c++', 'node.js']
```

Hints:
- `normalize_skill`: lowercase, strip, then `ALIASES.get(...)`.
- `extract_skills`: loop over every name in `KNOWN_SKILLS` **and** `ALIASES`. If it appears as a **whole word** in the text, add `normalize_skill(name)` to a set.
- `\b` (word boundary) fails for `c++` and `node.js`, because `+` and `.` aren't word characters. Use **lookarounds** instead: "not preceded by a letter, digit, `+` or `.`" and "not followed by a letter, digit or `+`".

<details>
<summary>Show answer</summary>

```python
import re


def normalize_skill(name: str) -> str:
    s = name.strip().lower()
    return ALIASES.get(s, s)


def _pattern(name: str) -> re.Pattern:
    return re.compile(rf"(?<![\w+.]){re.escape(name)}(?![\w+])", re.IGNORECASE)


_PATTERNS = {name: _pattern(name) for name in KNOWN_SKILLS | set(ALIASES)}


def extract_skills(text: str) -> list[str]:
    if not text:
        return []
    found = {normalize_skill(name) for name, pat in _PATTERNS.items() if pat.search(text)}
    return sorted(found)
```
Building the patterns once, outside the function, is faster: there are 40 patterns and thousands of jobs.
</details>

---

## Step 6: The job sources (real web data)

### 6a. Look before you code
Open https://www.arbeitnow.com/api/job-board-api in your browser. Find:
- Where the list of jobs is (key `data`).
- The field names: `title`, `company_name`, `location`, `url`, `tags`, `description`, `created_at`.
- The type of `created_at`. It's a **number** (Unix seconds), not a date string.

Do the same for https://remoteok.com/api. Notice that the **first item is a legal notice**, not a job.

### 6b. `sources/arbeitnow.py`
Write `fetch_raw`, `normalize` and `fetch`. Test each one in the shell:
```python
from jobs.sources import arbeitnow
raw = arbeitnow.fetch_raw()
len(raw), raw[0].keys()
arbeitnow.normalize(raw[0])
```

**Data-quality trap 1:** Arbeitnow's `tags` mix skills with other words like "Remote" or "Marketing". Don't save them directly as skills. Run them through `extract_skills` with the title and description, so only real skills survive.

**Data-quality trap 2:** in Step 7 we save with `bulk_create`, which **skips Django's validation**. If a title is longer than `max_length=300`, PostgreSQL throws an error and the whole batch fails. So `normalize` must **cut** every text to its max length: `title[:300]`, `company[:200]`, `location[:200]`, `url[:500]`, and each skill `[:50]`.

<details>
<summary>Show answer (arbeitnow.py)</summary>

```python
from datetime import datetime, timezone

import requests

from ..skills import extract_skills

API_URL = "https://www.arbeitnow.com/api/job-board-api"
SOURCE = "arbeitnow"


def fetch_raw(page: int = 1) -> list[dict]:
    resp = requests.get(API_URL, params={"page": page}, timeout=10)
    resp.raise_for_status()
    return resp.json().get("data", [])


def normalize(raw: dict) -> dict:
    # Tags are mixed ("Python", "Remote", "Marketing"), so pass them through
    # extract_skills too: only real skills survive.
    tags = " ".join(raw.get("tags", []))
    skills = extract_skills(f"{raw.get('title', '')} {tags} {raw.get('description', '')}")
    created = raw.get("created_at")
    return {
        "title": (raw.get("title") or "")[:300],
        "company": (raw.get("company_name") or "")[:200],
        "location": (raw.get("location") or "")[:200],
        "url": (raw.get("url") or "")[:500],
        "source": SOURCE,
        "skills": [s[:50] for s in skills],
        "posted_at": datetime.fromtimestamp(created, tz=timezone.utc) if created else None,
    }


def fetch() -> list[dict]:
    jobs = [normalize(r) for r in fetch_raw(page=1)]
    return [j for j in jobs if j["url"] and j["title"]]   # skip broken items
```
</details>

### 6c. `sources/remoteok.py`
Do the same on your own. Differences: skip `raw_list[0]`, `position` is the title, and `date` is an ISO string. Use `datetime.fromisoformat(...)`. Send the `HEADERS`: their API rejects requests without a User-Agent.

---

## Step 7: The Celery tasks

Open `jobs/tasks.py` and write `fetch_source` and `fetch_all_sources`. Read their docstrings first.

**Try it yourself** (the hard part of this week). Hints:
- Get the function with `SOURCES[source_name]` (import `SOURCES` from `.sources`).
- To know which jobs are **new**: collect all urls, ask the database which already exist (`Job.objects.filter(url__in=urls).values_list("url", flat=True)`), and save only the others.
- Save them in **one** query with `bulk_create`. Use `ignore_conflicts=True` too: if two fetches run at the same moment, the database `UNIQUE` still stops duplicates.
- Always finish the `FetchRun`, even on error: use `try / except / raise`.
- Use `timezone.now()` from `django.utils`, never `datetime.now()`, because the settings have `USE_TZ = True`.

<details>
<summary>Show answer</summary>

```python
import requests
from celery import group, shared_task
from django.utils import timezone

from .models import FetchRun, Job
from .sources import SOURCES


@shared_task(bind=True, autoretry_for=(requests.RequestException,),
             retry_backoff=True, max_retries=3)
def fetch_source(self, source_name: str) -> dict:
    run = FetchRun.objects.create(source=source_name)
    try:
        items = SOURCES[source_name]()
        urls = [i["url"] for i in items]
        existing = set(Job.objects.filter(url__in=urls).values_list("url", flat=True))

        new_items, seen = [], set()
        for i in items:
            if i["url"] not in existing and i["url"] not in seen:   # also skip duplicates inside the batch
                seen.add(i["url"])
                new_items.append(i)

        Job.objects.bulk_create([Job(**i) for i in new_items], ignore_conflicts=True)

        run.status = FetchRun.Status.SUCCESS
        run.jobs_found, run.jobs_new = len(items), len(new_items)
        return {"source": source_name, "found": len(items), "new": len(new_items)}
    except Exception as e:
        run.status = FetchRun.Status.FAILED
        run.error = str(e)[:1000]
        raise
    finally:
        run.finished_at = timezone.now()
        run.save()


@shared_task
def fetch_all_sources() -> list[str]:
    result = group(fetch_source.s(name) for name in SOURCES).apply_async()
    return [child.id for child in result.children]
```
</details>

**Restart the worker** (it only loads code at start), then in the shell:
```python
from jobs.tasks import fetch_source
r = fetch_source.delay("arbeitnow")
r.get(timeout=60)        # {'source': 'arbeitnow', 'found': 100, 'new': 100}
r = fetch_source.delay("arbeitnow")
r.get(timeout=60)        # second time: 'new': 0 (no duplicates!)
```

✅ **Check:**
- Watch the worker terminal: you see `received` → `succeeded`.
- http://localhost:8000/jobs now has real jobs.
- `/admin` (or the shell) shows `FetchRun` rows.
- Turn off Wi-Fi and run it again: you should see the **retries** in the worker log, and then a `failed` FetchRun.

---

## Step 8: Celery Beat (run every hour by itself)

The schedule is in `settings.py` (`CELERY_BEAT_SCHEDULE`). To test it quickly, set the environment variable before starting Beat:
```bash
FETCH_EVERY_MINUTES=1 celery -A jobradar beat -l info
```
Keep the worker running in its own terminal.

✅ **Check:** every minute, Beat prints `Scheduler: Sending due task fetch-all-sources`, the worker runs both sources, and new `FetchRun` rows appear.

Then stop Beat and start it normally (hourly). Beat creates a file called `celerybeat-schedule`. It's already in `.gitignore`.

**Learn:** there must be **only one Beat** running. With two, every task would be scheduled twice. Workers, on the other hand, you can run as many as you like.

---

## Step 9: The 3 endpoints

In `jobs/views.py`, write `start_fetch`, `task_status` and `list_sources`. In `jobs/serializers.py`, uncomment `SourceSerializer`. In `jobs/urls.py`, uncomment the 3 paths. Follow [docs/api-contract.md](../docs/api-contract.md) exactly: the frontend depends on it.

Hints:
- `start_fetch`: read `request.query_params.get("source", "all")`. Return `Response({...}, status=202)`.
- `task_status`: `AsyncResult(task_id)`. Return `result` only when `state == "SUCCESS"`.
- `list_sources`: build a dict per source name. Fill in counts with `Job.objects.values("source").annotate(jobs=Count("id"))`. Get the latest run per source with `FetchRun.objects.order_by("source", "-started_at").distinct("source")`. Then run it through `SourceSerializer(items, many=True).data`.

<details>
<summary>Show answer (list_sources only)</summary>

```python
from django.db.models import Count
from rest_framework.response import Response

from .models import FetchRun, Job
from .serializers import SourceSerializer
from .sources import SOURCES


@api_view(["GET"])
def list_sources(request):
    counts = dict(Job.objects.values_list("source").annotate(n=Count("id")))
    latest = {
        r.source: r
        for r in FetchRun.objects.order_by("source", "-started_at").distinct("source")
    }
    items = [
        {
            "name": name,
            "jobs": counts.get(name, 0),
            "last_run_at": latest[name].started_at if name in latest else None,
            "last_status": latest[name].status if name in latest else None,
        }
        for name in SOURCES
    ]
    return Response(SourceSerializer(items, many=True).data)
```
`.distinct("source")` becomes `SELECT DISTINCT ON (source)`, which is PostgreSQL-only. MySQL can't do this, another point for the MySQL vs PostgreSQL question.
</details>

✅ **Check** in the browsable API:
- `POST /fetch` → **202** with a `task_id`.
- `GET /tasks/<that id>` → `PENDING`, then `SUCCESS` with a result.
- `POST /fetch?source=linkedin` → **400**.
- `GET /sources` → both sources with counts and the last run.

---

## Step 10: Connect the frontend

The dashboard now has a **Fetch now** button and a **Sources** panel (my part, already built). With `runserver`, the worker and the frontend all running:
1. Click **Fetch now**. The button shows the task state while it runs.
2. When it finishes, the job list refreshes and the Sources panel shows the new counts and the run time.

---

## Step 11: Tests (you write them)

Run them with `python manage.py test jobs`. Ideas, from easy to harder:

| Test | How |
|---|---|
| `SkillTests`: the 4 stubs | Call `extract_skills(...)` and `assertEqual` |
| `normalize` cuts long titles | Give `arbeitnow.normalize` a dict with a 1000-char title, check `len(result["title"]) == 300` |
| `fetch_source` saves only new jobs | Call the task **directly** (`fetch_source("fake")`, no `.delay`, so it runs right here with no worker). Use `patch.dict("jobs.sources.SOURCES", {"fake": lambda: [...]})` to avoid calling the real internet. Run it twice and check `new` is 0 the second time. |
| `fetch_source` failure saves a `failed` run | A fake source that raises an error. Use `assertRaises`, then check the `FetchRun` status. |
| `POST /fetch` returns 202 | `with patch("jobs.tasks.fetch_all_sources.delay") as m:` so no Redis is needed. Then `m.assert_called_once()`. |
| `POST /fetch?source=bad` → 400 | No patch needed |
| `GET /sources` | Create a few `Job` and `FetchRun` rows by hand, then check the counts and `last_status` |

**Rule:** unit tests must **never** call the real internet or need a running worker. That's why we use `patch`. If they did, tests would fail whenever Wi-Fi is off or a website changes.

---

## ✅ Week 2 done when

- [ ] `docker compose up -d` starts PostgreSQL **and** Redis
- [ ] You've used `SET / GET / EXPIRE / TTL / INCR / LPUSH / LLEN` yourself, and watched `LLEN celery` go up and down
- [ ] `FetchRun` migration applied
- [ ] `extract_skills` passes the 3 shell examples in Step 5
- [ ] Both sources normalise real data (lengths cut, dates parsed)
- [ ] `fetch_source` saves only new jobs, logs every run, and retries on network errors
- [ ] Beat runs `fetch_all_sources` on schedule
- [ ] `POST /fetch`, `GET /tasks/{id}` and `GET /sources` match the contract
- [ ] The dashboard's **Fetch now** works end to end
- [ ] Your tests pass with Wi-Fi **off**
- [ ] The Week 2 boxes in [STUBS.md](STUBS.md) are ticked

Then tell me **"Week 2 done"** for the review and quiz.

---

## Week 2 interview quiz (the questions from your interview, and more)

1. What is Redis? Why is it fast, and what's the risk of keeping data only in memory?
2. Explain `SET`, `GET`, `EXPIRE`, `TTL`, `INCR`. Why is `INCR` safe when 100 users call it at the same time?
3. Why should you never run `KEYS *` in production? What do you use instead?
4. What is Celery? Explain broker, worker, result backend and Beat.
5. What happens step by step when you call `fetch_source.delay("arbeitnow")`?
6. Why does `POST /fetch` return **202** and not 200? Why must you never call `.get()` inside a view?
7. A worker crashes in the middle of a task. What happens to the task? What do `acks_late` and idempotent mean?
8. Why did we use `bulk_create` instead of `Job.objects.create` in a loop? What does it skip?
9. How did you avoid duplicate jobs? Give two levels of protection.
10. What is retry with exponential backoff, and why not retry immediately?
11. Web scraping vs a public API: which is better and why? What must you check before scraping a site?
12. Why do unit tests mock the network and the Celery queue?
