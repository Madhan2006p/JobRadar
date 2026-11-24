# Postmortem: <short title>

Copy this file to `ops/postmortems/YYYY-MM-DD-<short-title>.md`.

**Blameless:** describe what the system did and why. Never "X made a mistake". Ask "why did the system let this happen?"

| | |
|---|---|
| Date | YYYY-MM-DD |
| Experiment | #<n> from [../RELIABILITY.md](../RELIABILITY.md), or "real incident" |
| Duration | <from start to recovery, in minutes> |
| Impact | <what users could not do, for example "no new jobs for 20 min; GET /jobs gave 500 for 3 min"> |
| Detected by | <which alert, and how long after the start> |

## What I expected

<Write this BEFORE breaking it.>

## What really happened

<Short and honest. Where reality was different from what you expected, say so.>

## Timeline

| Time | What happened |
|---|---|
| 10:00 | Stopped Redis (`docker compose stop redis`) |
| 10:01 | `GET /jobs` started returning 500 |
| 10:02 | `HighErrorRate` alert reached Telegram |
| 10:05 | Started Redis again; API recovered at 10:05:20 |

## Root cause

<Ask "why?" until you reach something you can change. For example: 500 → the cache call raised an error → nothing caught it → the view had no fallback.>

## What went well

- <for example "the alert fired within 1 minute">

## What went badly

- <for example "the error message in the logs didn't say Redis">

## Fixes

| Fix | Status | Proof |
|---|---|---|
| <for example "cache errors fall back to the DB"> | done / todo | <re-ran the experiment: no 500s; screenshot `img/...png`> |

## Graphs

<Before/after Grafana screenshots.>
