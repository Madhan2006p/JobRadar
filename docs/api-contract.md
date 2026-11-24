# API contract

The frontend and backend agree on this. Change this file first if an endpoint needs to change.

- Backend: **Django REST Framework**, at `http://localhost:8000` (`python manage.py runserver`)
- All bodies are JSON. Paths have **no trailing slash** (`/jobs`, not `/jobs/`).
- The backend allows CORS from `http://localhost:5500` (the frontend).

## Error format (DRF default)

| Status | When | Body |
|---|---|---|
| `400` | Invalid input | One list of messages per field: `{ "title": ["This field is required."], "url": ["job with this url already exists."] }` |
| `404` | Object not found | `{ "detail": "No Job matches the given query." }` |
| `429` | Too many requests (Week 3) | `{ "detail": "Request was throttled. Expected available in 30 seconds." }` |

The frontend shows the first message of the first field for a 400, and only checks the status code for 404 and 429.

## The Job object

```json
{
  "id": 1,
  "title": "Backend Engineer Intern",
  "company": "Acme",
  "location": "Remote",
  "url": "https://example.com/jobs/123",
  "source": "manual",
  "skills": ["python", "postgresql"],
  "posted_at": "2026-11-14T09:30:00Z",
  "created_at": "2026-11-14T10:00:00Z"
}
```

| Field | Type | Required on create | Notes |
|---|---|---|---|
| `id` | integer | no (read-only) | |
| `title` | string | yes | Max 300 chars |
| `company` | string | yes | Max 200 chars |
| `location` | string | no | `""` when unknown |
| `url` | string (URL) | yes | Unique. A duplicate returns `400` with a `url` error. |
| `source` | string | no | Default `"manual"`. Later: `"arbeitnow"`, `"remoteok"`. |
| `skills` | list of strings | no | Default `[]`. The server lowercases, trims and removes duplicates. |
| `posted_at` | ISO 8601 datetime or null | no | When the company posted it |
| `created_at` | ISO 8601 datetime | no (read-only) | When we saved it |

## Week 1 endpoints

### `GET /health`
`200` → `{ "status": "ok" }`

### `GET /jobs`
| Query param | Default | Meaning |
|---|---|---|
| `search` | (none) | Case-insensitive match on `title` or `company` |
| `limit` | `20` | Page size |
| `offset` | `0` | Items to skip |
| `ordering` | `-created_at` | Also allowed: `created_at`, `posted_at`, `-posted_at` |

`200`, newest first (DRF `LimitOffsetPagination`):
```json
{
  "count": 42,
  "next": "http://localhost:8000/jobs?limit=20&offset=20",
  "previous": null,
  "results": [ /* Job objects */ ]
}
```
`count` is the number of all matching jobs, not just this page.

### `GET /jobs/{id}`
`200` → Job · `404` if it doesn't exist

### `POST /jobs`
Body: a Job object without `id` and `created_at`.
`201` → the saved Job · `400` → field errors (including a duplicate `url`)

### `DELETE /jobs/{id}`
`204` (empty body) · `404` if it doesn't exist

## Week 2 endpoints (Celery background fetching)

Source names: `arbeitnow`, `remoteok`. `all` means every source.

### `POST /fetch?source=all`
Starts a background fetch and returns **at once**, without waiting for it.

| Result | Status | Body |
|---|---|---|
| Started | `202` | `{ "task_id": "2f1c…", "source": "all" }` |
| Unknown source | `400` | `{ "detail": "Unknown source" }` |

No request body. `source` is a query parameter (default `all`).

### `GET /tasks/{task_id}`
`200` →
```json
{ "task_id": "2f1c…", "state": "SUCCESS", "result": { "source": "arbeitnow", "found": 100, "new": 12 } }
```
| Field | Notes |
|---|---|
| `state` | `PENDING` · `STARTED` · `RETRY` · `SUCCESS` · `FAILURE` (Celery's names). An unknown id also shows `PENDING`. |
| `result` | Only when `state` is `SUCCESS`, otherwise `null`. For `source=all` it's the list of child task ids. Never contains error details. |

The frontend polls this every 2 seconds until `SUCCESS` or `FAILURE`, for at most 2 minutes. For `source=all`, the parent task finishes as soon as it has queued the children, so the frontend then polls **each child id** from `result` and adds up their `new` counts.

### `GET /sources`
`200`, one item per source (even with 0 jobs and no runs):
```json
[
  { "name": "arbeitnow", "jobs": 120, "last_run_at": "2026-11-23T10:00:05Z", "last_status": "success" },
  { "name": "remoteok",  "jobs": 0,   "last_run_at": null,                   "last_status": null }
]
```
`last_status`: `running` · `success` · `failed` · `null` (never run). Not paginated.

## Weeks 3–4 (draft)

The planned endpoints are listed in [backend/STUBS.md](../backend/STUBS.md) and in the docstrings of each app's `views.py`. Each one moves into this file, with full details, when its week starts.
