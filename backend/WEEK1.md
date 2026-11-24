# Week 1: Django REST Framework + PostgreSQL

**Goal:** by the end of this week, `/jobs` supports list (with search and paging), get one, create and delete. Data is saved in PostgreSQL running in Docker, and the frontend dashboard shows your real data.

**Rules**
- You type every line. Copy-paste makes you forget; typing makes you remember.
- Each step has a ✅ **Check**. Don't move on until it passes.
- **Try it yourself** parts have the answer hidden under "Show answer". Try first, then compare.
- Stuck for more than 20 minutes? Ask me with the exact error message.

All files already exist as **stubs**. The full list is in [STUBS.md](STUBS.md). Week 1 touches these:

```text
JobRadar/
├── docker-compose.yml        ← you create this (Step 1)
└── backend/
    ├── manage.py             ← done
    ├── jobradar/settings.py  ← done (read it once!)
    ├── jobradar/views.py     ← Step 5: health
    └── jobs/
        ├── models.py         ← Step 3: Job
        ├── admin.py          ← Step 4 (optional)
        ├── serializers.py    ← Step 6: JobSerializer
        ├── views.py          ← Step 7: JobViewSet
        ├── urls.py           ← done (router)
        └── tests.py          ← Step 9
```

---

## Step 0: Install Docker Desktop

Docker runs PostgreSQL (this week) and Redis (Week 2) in containers.

1. Install Docker Desktop: https://docs.docker.com/desktop/setup/install/windows-install/
2. Turn on **WSL 2** when it asks. Restart if asked.
3. Open Docker Desktop and wait for "Engine running".

✅ **Check:** both print a version:
```bash
docker --version
```
```bash
docker compose version
```

**Learn:** an *image* is a template (`postgres:16`). A *container* is a running copy of it. A *volume* keeps data after the container is deleted.

---

## Step 1: Start PostgreSQL with Docker Compose

Create `JobRadar/docker-compose.yml`:

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: jobradar
      POSTGRES_PASSWORD: jobradar
      POSTGRES_DB: jobradar
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

From the `JobRadar` folder:
```bash
docker compose up -d
```

✅ **Check:** `docker compose ps` shows `db` as running.

These are local-only passwords. `settings.py` reads the same values from environment variables (`POSTGRES_USER`, and so on) and uses these as defaults.

---

## Step 2: Python setup

From the `backend` folder:
```bash
python -m venv .venv
```
```bash
.venv\Scripts\activate
```
```bash
pip install -r requirements.txt
```

Now let Django check the project, and create its built-in tables (users, sessions, admin):
```bash
python manage.py check
```
```bash
python manage.py migrate
```

✅ **Check:** `check` says "System check identified no issues", and `migrate` prints a list of `OK`s. That means Django reached PostgreSQL in Docker.

Read `jobradar/settings.py` once, top to bottom. Find where these are set: the database, `INSTALLED_APPS`, CORS, and `REST_FRAMEWORK` (pagination and search). You'll be asked about them.

---

## Step 3: The `Job` model and your first migration

Open `jobs/models.py`.

**Try it yourself.** Write the `Job` model from the docstring:
- 9 fields
- `class Meta` with `ordering` and an index on `-created_at`
- `__str__`

<details>
<summary>Show answer</summary>

```python
from django.contrib.postgres.fields import ArrayField
from django.db import models


class Job(models.Model):
    title = models.CharField(max_length=300)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True, default="")
    url = models.URLField(max_length=500, unique=True)
    source = models.CharField(max_length=50, default="manual")
    skills = ArrayField(models.CharField(max_length=50), default=list, blank=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["-created_at"])]

    def __str__(self):
        return f"{self.title} at {self.company}"
```
</details>

Create the migration, **read the SQL Django wrote**, then apply it:
```bash
python manage.py makemigrations jobs
```
```bash
python manage.py sqlmigrate jobs 0001
```
```bash
python manage.py migrate
```

**Learn:**
- A **migration** is a versioned change to the database. It's saved in `jobs/migrations/` and committed to Git, so every developer and server gets the same tables.
- `sqlmigrate` shows the real SQL: `CREATE TABLE "jobs_job"`, `UNIQUE` on `url`, `varchar(50)[]` for skills. Read it. Interviewers ask "what SQL does the ORM run?"
- `ArrayField` works only with PostgreSQL. MySQL has no array type, which is a good point for the "MySQL vs PostgreSQL" question.
- `null=True` affects the database; `blank=True` affects validation. Know the difference.

✅ **Check:** add a job with the Django shell (the ORM by hand):
```bash
python manage.py shell
```
```python
from jobs.models import Job
Job.objects.create(title="Test Job", company="Test Co", url="https://example.com/1", skills=["python"])
Job.objects.filter(title__icontains="test").count()     # 1
print(Job.objects.filter(title__icontains="test").query) # the SQL it runs
exit()
```

---

## Step 4 (optional, 5 minutes): Django admin

Uncomment the code in `jobs/admin.py`, then:
```bash
python manage.py createsuperuser
```
```bash
python manage.py runserver
```
Open http://localhost:8000/admin, log in, and see your test job. Admin is a free internal tool that companies use a lot.

---

## Step 5: `GET /health`

In `jobradar/views.py`, make `health` return `Response({"status": "ok"})`.

```bash
python manage.py runserver
```

✅ **Check:** http://localhost:8000/health shows `{"status": "ok"}` on DRF's browsable API page.

---

## Step 6: `JobSerializer`

Open `jobs/serializers.py`.

**Try it yourself.** Add `class Meta` (model, fields, read-only fields) and `validate_skills` from the docstring.

<details>
<summary>Show answer</summary>

```python
from rest_framework import serializers

from .models import Job


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ["id", "title", "company", "location", "url", "source",
                  "skills", "posted_at", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_skills(self, value):
        cleaned = []
        for skill in value:
            s = skill.strip().lower()
            if s and s not in cleaned:
                cleaned.append(s)
        return cleaned
```
</details>

**Learn:** DRF runs `validate_<field>` automatically for each field. A `ValidationError` raised inside becomes a **400** with that field's message.

---

## Step 7: `JobViewSet` (the whole `/jobs` API)

Open `jobs/views.py`. The class already inherits the 4 mixins (list, retrieve, create, destroy).

**Try it yourself.** Set the 4 class attributes from the docstring. That's all: the mixins handle status codes, pagination comes from `settings.py`, and `jobs/urls.py` already registers the router.

<details>
<summary>Show answer</summary>

```python
from .models import Job
from .serializers import JobSerializer


class JobViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                 mixins.CreateModelMixin, mixins.DestroyModelMixin,
                 viewsets.GenericViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    search_fields = ["title", "company"]
    ordering_fields = ["created_at", "posted_at"]
```
</details>

✅ **Check** in the browser (DRF's browsable API):
1. http://localhost:8000/jobs: a list with `count`, `next`, `previous`, `results`.
2. http://localhost:8000/jobs?search=test and http://localhost:8000/jobs?limit=1: search and paging work.
3. Use the form at the bottom of `/jobs` to POST a new job → **201**.
4. POST the same `url` again → **400** with a `url` error. Leave `title` empty → **400** with a `title` error.
5. http://localhost:8000/jobs/1 → **200**. http://localhost:8000/jobs/99999 → **404**.
6. On `/jobs/1`, click **DELETE** → **204**, then reload → **404**.

**Learn:** open `ListModelMixin` in your editor (Ctrl+click) and read the code. It's about 10 lines. Knowing what the framework does for you is what separates a backend engineer from a copy-paster.

---

## Step 8: Connect to the frontend

Keep `runserver` running. In a second terminal, from the `JobRadar` folder:
```bash
python -m http.server 5500 --directory frontend
```
Open http://localhost:5500. The badge turns green ("API connected") and your jobs appear. Add one with the form, then delete one with its **Delete** button.

If the badge stays yellow, open the browser console (F12). A **CORS** error means `CORS_ALLOWED_ORIGINS` in `settings.py` doesn't match the page address.

---

## Step 9: Tests

Open `jobs/tests.py`, class `JobApiTests`. Replace each `self.skipTest(...)` with a real test. Example:

```python
def test_create_job_returns_201(self):
    res = self.client.post("/jobs", {"title": "Dev", "company": "Acme",
                                     "url": "https://example.com/a"}, format="json")
    self.assertEqual(res.status_code, 201)
    self.assertEqual(res.data["title"], "Dev")
```

```bash
python manage.py test jobs
```

✅ All 8 `JobApiTests` pass. (The `SkillTests` stay skipped until Week 2.)

---

## ✅ Week 1 done when

- [ ] `docker compose up -d` starts PostgreSQL
- [ ] The `Job` migration is applied, and you've read its SQL
- [ ] `/health` and all 4 `/jobs` operations match the [API contract](../docs/api-contract.md)
- [ ] 200 / 201 / 204 / 400 / 404 all work
- [ ] The dashboard shows "API connected", and add and delete work there
- [ ] `python manage.py test jobs` passes
- [ ] The Week 1 boxes in [STUBS.md](STUBS.md) are ticked

Then tell me **"Week 1 done"**. I'll review your code and run the quiz below like an interviewer.

---

## Week 1 interview quiz (answer these to me in chat)

1. What is a migration? Why do we commit migration files to Git?
2. Show the SQL Django created for `Job`. Where is the unique constraint?
3. `null=True` vs `blank=True`: what is the difference?
4. What does a serializer do? Where does a 400 error come from?
5. ViewSet vs APIView vs `@api_view`: when do you use each?
6. What is `LimitOffsetPagination`? What's the problem with OFFSET on millions of rows, and what is cursor pagination?
7. Two people POST the same `url` at the same moment. Both pass the serializer check. What stops the duplicate, and what error would the second one get?
8. What is CORS, and why did the browser need it here?
9. What is the N+1 query problem in an ORM? How do `select_related` and `prefetch_related` fix it?
10. Why did we add an index on `created_at`? How would you check the index is used? (`EXPLAIN`)
