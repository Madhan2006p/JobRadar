# Runbook: <AlertName>

Copy this file to `ops/runbooks/<alert-name>.md` (for example `api-down.md`). Link it from the alert rule's `runbook_url` annotation.

**Severity:** critical / warning
**Alert fires when:** <the rule in plain words, for example "the API has not answered Prometheus for 1 minute">

## What users see

<For example: "The dashboard shows sample data and the 'API offline' banner.">

## Check first (2 minutes)

1. `docker compose ps`: is the service running, restarting, or unhealthy?
2. `docker compose logs --tail=100 <service>`: what is the last error?
3. Grafana panel: <which panel to look at, and what "bad" looks like>

## Fix

| If you see | Do this |
|---|---|
| <for example "container exited"> | <for example `docker compose up -d api`> |
| <for example "too many DB connections"> | <steps> |

## Check it's fixed

- <for example `curl -i http://localhost:8000/health/ready` returns 200>
- The alert turns to "resolved" in Alertmanager.

## If none of this works

<Who or what is next: restart everything, restore a backup, and so on.>

## Afterwards

Write a postmortem in `ops/postmortems/` using [../postmortems/TEMPLATE.md](../postmortems/TEMPLATE.md).
