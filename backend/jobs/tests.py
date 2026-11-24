"""Tests for the jobs app. Run from the backend folder:
    python manage.py test jobs

Django creates a separate empty test database, so your real data is safe.
Replace each self.skipTest with a real test when that feature works.
"""

from rest_framework.test import APITestCase

from .models import Job


def job_data(**overrides):
    """A valid POST /jobs body. Pass keyword arguments to change any field."""
    data = {
        "title": "Backend Engineer Intern",
        "company": "Acme",
        "location": "Remote",
        "url": "https://example.com/jobs/1",
        "skills": ["python", "django"],
    }
    data.update(overrides)
    return data


class JobApiTests(APITestCase):
    """Week 1. Each test starts with an EMPTY test database (Django resets it)."""

    # ---------- /health ----------

    def test_health_returns_ok(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, {"status": "ok"})

    # ---------- POST /jobs ----------

    def test_create_job_returns_201(self):
        res = self.client.post("/jobs", job_data(), format="json")

        # 1. The HTTP answer is right
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["title"], "Backend Engineer Intern")
        self.assertEqual(res.data["source"], "manual")       # default from the model
        self.assertIn("id", res.data)                        # server set it
        self.assertIn("created_at", res.data)                # server set it

        # 2. It was REALLY saved in the database (don't trust the response alone)
        self.assertEqual(Job.objects.count(), 1)
        self.assertEqual(Job.objects.get().company, "Acme")

    def test_duplicate_url_returns_400(self):
        first = self.client.post("/jobs", job_data(), format="json")
        self.assertEqual(first.status_code, 201)

        second = self.client.post("/jobs", job_data(title="Other title"), format="json")
        self.assertEqual(second.status_code, 400)
        self.assertIn("url", second.data)                    # the error is about the url field
        self.assertEqual(Job.objects.count(), 1)             # the duplicate was NOT saved

    def test_missing_title_returns_400(self):
        body = job_data()
        del body["title"]

        res = self.client.post("/jobs", body, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("title", res.data)
        self.assertEqual(Job.objects.count(), 0)

    def test_skills_are_cleaned(self):
        res = self.client.post(
            "/jobs", job_data(skills=[" Python ", "python", "", "Redis"]), format="json"
        )
        self.assertEqual(res.status_code, 201)
        # strip + lowercase + drop empty + remove duplicates, order kept
        self.assertEqual(res.data["skills"], ["python", "redis"])

    # ---------- GET /jobs ----------

    def test_list_search_and_paging(self):
        # Arrange: 3 jobs straight into the database (faster than 3 POSTs)
        Job.objects.create(title="Python Developer", company="Acme", url="https://example.com/a")
        Job.objects.create(title="Java Developer", company="Python Labs", url="https://example.com/b")
        Job.objects.create(title="Designer", company="Paperkite", url="https://example.com/c")

        # No filter: all 3, in the DRF page shape
        res = self.client.get("/jobs")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["count"], 3)
        self.assertEqual(len(res.data["results"]), 3)

        # search matches title OR company, case-insensitive -> 2 jobs
        res = self.client.get("/jobs", {"search": "PYTHON"})
        self.assertEqual(res.data["count"], 2)

        # paging: limit=1 gives 1 result, but count is still the total
        res = self.client.get("/jobs", {"search": "python", "limit": 1})
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["count"], 2)
        self.assertIsNotNone(res.data["next"])               # there is a next page

    def test_list_newest_first(self):
        old = Job.objects.create(title="Old", company="A", url="https://example.com/old")
        new = Job.objects.create(title="New", company="B", url="https://example.com/new")

        res = self.client.get("/jobs")
        ids = [job["id"] for job in res.data["results"]]
        self.assertEqual(ids, [new.id, old.id])

    # ---------- GET /jobs/{id} ----------

    def test_get_one_job(self):
        job = Job.objects.create(title="Dev", company="Acme", url="https://example.com/x")

        res = self.client.get(f"/jobs/{job.id}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["id"], job.id)

    def test_get_missing_job_returns_404(self):
        res = self.client.get("/jobs/999999")
        self.assertEqual(res.status_code, 404)

    # ---------- DELETE /jobs/{id} ----------

    def test_delete_job_then_404(self):
        job = Job.objects.create(title="Dev", company="Acme", url="https://example.com/x")

        res = self.client.delete(f"/jobs/{job.id}")
        self.assertEqual(res.status_code, 204)
        self.assertFalse(Job.objects.filter(id=job.id).exists())

        # Deleting or reading it again -> 404
        self.assertEqual(self.client.get(f"/jobs/{job.id}").status_code, 404)
        self.assertEqual(self.client.delete(f"/jobs/{job.id}").status_code, 404)

    # ---------- Things the API must NOT allow ----------

    def test_client_cannot_set_id_or_created_at(self):
        res = self.client.post(
            "/jobs", job_data(id=12345, created_at="2000-01-01T00:00:00Z"), format="json"
        )
        self.assertEqual(res.status_code, 201)
        self.assertNotEqual(res.data["id"], 12345)            # read-only fields are ignored
        self.assertFalse(res.data["created_at"].startswith("2000"))

    def test_update_is_not_allowed(self):
        job = Job.objects.create(title="Dev", company="Acme", url="https://example.com/x")
        res = self.client.put(f"/jobs/{job.id}", job_data(), format="json")
        self.assertEqual(res.status_code, 405)               # Method Not Allowed: no UpdateModelMixin


class SkillTests(APITestCase):
    """Week 2. Plain unit tests for skills.extract_skills (no HTTP needed)."""

    def test_simple(self):
        self.skipTest("TODO Week 2: 'Python and Redis developer' -> ['python', 'redis']")

    def test_go_does_not_match_good(self):
        self.skipTest("TODO Week 2: 'good communication' -> []")

    def test_symbols(self):
        self.skipTest("TODO Week 2: 'C++ and Node.js' -> ['c++', 'node.js']")

    def test_aliases(self):
        self.skipTest("TODO Week 2: 'Postgres, k8s' -> ['kubernetes', 'postgresql']")
