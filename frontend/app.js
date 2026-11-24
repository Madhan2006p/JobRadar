// JobRadar dashboard. Talks to the backend described in docs/api-contract.md.
// If the API is not reachable, it falls back to sample data so the page still works.

const API_BASE = "http://localhost:8000";
const PAGE_SIZE = 10;

const state = {
  online: false,
  search: "",
  offset: 0,
  total: 0,
  fetching: false,
};

// ---------- Sample data (used only when the API is offline) ----------

const now = Date.now();
const hoursAgo = (h) => new Date(now - h * 3600_000).toISOString();
let sampleJobs = [
  { id: 6, title: "Backend Engineer Intern", company: "Northwind Labs", location: "Bengaluru", url: "https://example.com/jobs/6", source: "sample", skills: ["python", "fastapi", "postgresql"], posted_at: hoursAgo(3), created_at: hoursAgo(2) },
  { id: 5, title: "Data Engineer Intern", company: "Riverstone Analytics", location: "Remote", url: "https://example.com/jobs/5", source: "sample", skills: ["sql", "python", "airflow"], posted_at: hoursAgo(9), created_at: hoursAgo(8) },
  { id: 4, title: "Python Developer (Celery, Redis)", company: "Bluefin Systems", location: "Chennai", url: "https://example.com/jobs/4", source: "sample", skills: ["python", "celery", "redis"], posted_at: hoursAgo(26), created_at: hoursAgo(25) },
  { id: 3, title: "Junior DevOps Engineer", company: "Cloudnest", location: "Hyderabad", url: "https://example.com/jobs/3", source: "sample", skills: ["docker", "aws", "terraform"], posted_at: null, created_at: hoursAgo(50) },
  { id: 2, title: "Security Analyst Intern", company: "Shieldline", location: "Coimbatore", url: "https://example.com/jobs/2", source: "sample", skills: ["linux", "vulnerability assessment"], posted_at: hoursAgo(80), created_at: hoursAgo(72) },
  { id: 1, title: "Full Stack Intern", company: "Paperkite", location: "Remote", url: "https://example.com/jobs/1", source: "sample", skills: ["react", "node.js", "postgresql"], posted_at: hoursAgo(120), created_at: hoursAgo(100) },
];

function sampleList({ search, limit, offset }) {
  const q = (search || "").toLowerCase();
  const matches = sampleJobs.filter(
    (j) => !q || j.title.toLowerCase().includes(q) || j.company.toLowerCase().includes(q)
  );
  // Same shape as DRF LimitOffsetPagination
  return { count: matches.length, next: null, previous: null, results: matches.slice(offset, offset + limit) };
}

// ---------- API calls ----------

async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(2000) });
    return res.ok;
  } catch {
    return false;
  }
}

async function fetchJobs({ search, limit, offset }) {
  if (!state.online) return sampleList({ search, limit, offset });

  const params = new URLSearchParams({ limit, offset });
  if (search) params.set("search", search);
  const res = await fetch(`${API_BASE}/jobs?${params}`);
  if (!res.ok) throw new Error(`GET /jobs failed with ${res.status}`);
  return res.json();
}

async function createJob(job) {
  if (!state.online) {
    if (sampleJobs.some((j) => j.url === job.url)) {
      return { status: 400, body: { url: ["job with this url already exists."] } };
    }
    const saved = { ...job, id: Math.max(0, ...sampleJobs.map((j) => j.id)) + 1, created_at: new Date().toISOString() };
    sampleJobs = [saved, ...sampleJobs];
    return { status: 201, body: saved };
  }

  const res = await fetch(`${API_BASE}/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(job),
  });
  let body = null;
  try { body = await res.json(); } catch { /* empty body */ }
  return { status: res.status, body };
}

async function deleteJob(id) {
  if (!state.online) {
    const before = sampleJobs.length;
    sampleJobs = sampleJobs.filter((j) => j.id !== id);
    return sampleJobs.length < before ? 204 : 404;
  }
  const res = await fetch(`${API_BASE}/jobs/${encodeURIComponent(id)}`, { method: "DELETE" });
  return res.status;
}

// ---------- Week 2: sources, fetch, task polling ----------

const TASK_POLL_MS = 2000;
const TASK_TIMEOUT_MS = 120_000;
const DONE_STATES = ["SUCCESS", "FAILURE"];

let sampleSources = [
  { name: "arbeitnow", jobs: 0, last_run_at: null, last_status: null },
  { name: "remoteok", jobs: 0, last_run_at: null, last_status: null },
];
const sampleTasks = new Map(); // offline only: fake Celery tasks that finish after a few seconds

function sampleTask(id) {
  const task = sampleTasks.get(id);
  if (!task) return { task_id: id, state: "PENDING", result: null };
  const age = Date.now() - task.started;
  if (age < 1500) return { task_id: id, state: "PENDING", result: null };
  if (age < 3000) return { task_id: id, state: "STARTED", result: null };
  if (!task.done) { task.done = true; task.finish?.(); }
  return { task_id: id, state: "SUCCESS", result: task.result };
}

function startSampleFetch() {
  const childIds = sampleSources.map((s) => {
    const id = `sample-${s.name}-${Date.now()}`;
    const newJob = {
      id: Math.max(0, ...sampleJobs.map((j) => j.id)) + 1 + sampleTasks.size,
      title: `Backend Intern (from ${s.name})`, company: "Sample Co", location: "Remote",
      url: `https://example.com/${id}`, source: s.name, skills: ["python", "redis"],
      posted_at: null, created_at: new Date().toISOString(),
    };
    sampleTasks.set(id, {
      started: Date.now(),
      result: { source: s.name, found: 1, new: 1 },
      finish: () => {
        sampleJobs = [newJob, ...sampleJobs];
        Object.assign(s, { jobs: s.jobs + 1, last_run_at: new Date().toISOString(), last_status: "success" });
      },
    });
    return id;
  });
  const parentId = `sample-all-${Date.now()}`;
  sampleTasks.set(parentId, { started: Date.now() - 1500, result: childIds });
  return { status: 202, body: { task_id: parentId, source: "all" } };
}

// Returns the list, or null if the backend doesn't have /sources yet (before Week 2).
async function fetchSources() {
  if (!state.online) return sampleSources;
  const res = await fetch(`${API_BASE}/sources`);
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`GET /sources failed with ${res.status}`);
  return res.json();
}

async function startFetch(source = "all") {
  if (!state.online) return startSampleFetch();
  const res = await fetch(`${API_BASE}/fetch?source=${encodeURIComponent(source)}`, { method: "POST" });
  let body = null;
  try { body = await res.json(); } catch { /* empty body */ }
  return { status: res.status, body };
}

async function getTask(id) {
  if (!state.online) return sampleTask(id);
  const res = await fetch(`${API_BASE}/tasks/${encodeURIComponent(id)}`);
  if (!res.ok) throw new Error(`GET /tasks failed with ${res.status}`);
  return res.json();
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// Ask the backend every 2 s until the task is finished (or 2 minutes pass).
async function pollTask(id, onUpdate) {
  const deadline = Date.now() + TASK_TIMEOUT_MS;
  while (Date.now() < deadline) {
    const task = await getTask(id);
    onUpdate?.(task);
    if (DONE_STATES.includes(task.state)) return task;
    await sleep(TASK_POLL_MS);
  }
  return { task_id: id, state: "TIMEOUT", result: null };
}

// DRF 400 body: {"field": ["message", ...], ...} -> "field: message"
function firstFieldError(body) {
  if (!body || typeof body !== "object") return "Some fields are invalid.";
  const [field, messages] = Object.entries(body)[0] || [];
  if (!field) return "Some fields are invalid.";
  const msg = Array.isArray(messages) ? messages[0] : String(messages);
  return field === "non_field_errors" || field === "detail" ? msg : `${field}: ${msg}`;
}

// ---------- Rendering ----------

const $ = (id) => document.getElementById(id);

function timeAgo(iso) {
  if (!iso) return "";
  const mins = Math.round((Date.now() - new Date(iso).getTime()) / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins} min ago`;
  const hours = Math.round(mins / 60);
  if (hours < 24) return `${hours} h ago`;
  const days = Math.round(hours / 24);
  return `${days} day${days === 1 ? "" : "s"} ago`;
}

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text != null) node.textContent = text; // textContent, never innerHTML: job data could contain HTML
  return node;
}

function renderJob(job) {
  const li = el("li", "job");

  const top = el("div", "job-top");
  const link = el("a", "job-title", job.title);
  link.href = job.url;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  top.append(link, el("span", "job-when", timeAgo(job.posted_at || job.created_at)));

  const meta = el("div", "job-meta");
  meta.append(
    document.createTextNode([job.company, job.location].filter(Boolean).join(" · ") + " "),
    el("span", "source", job.source)
  );

  li.append(top, meta);

  const bottom = el("div", "job-bottom");
  const chips = el("ul", "chips");
  (job.skills || []).forEach((s) => chips.append(el("li", "chip", s)));
  const del = el("button", "job-delete", "Delete");
  del.type = "button";
  del.setAttribute("aria-label", `Delete ${job.title} at ${job.company}`);
  del.addEventListener("click", () => onDelete(job, del));
  bottom.append(chips, del);
  li.append(bottom);
  return li;
}

function renderStatus() {
  const badge = $("api-status");
  if (state.online) {
    badge.className = "badge badge-ok";
    badge.textContent = "API connected";
  } else {
    badge.className = "badge badge-warn";
    badge.textContent = "API offline · showing sample data";
  }
}

function renderSources(sources) {
  const list = $("source-list");
  const button = $("fetch-btn");
  if (sources === null) {
    list.replaceChildren(el("li", "source-note", "Available after Week 2 (GET /sources)."));
    button.disabled = true;
    button.title = "The backend has no /fetch endpoint yet";
    return;
  }
  button.title = "";
  button.disabled = state.fetching; // re-enable unless a fetch is running
  list.replaceChildren(
    ...sources.map((s) => {
      const li = el("li", "source-row");
      li.append(
        el("span", "source-name", s.name),
        el("span", "source-count", `${s.jobs} job${s.jobs === 1 ? "" : "s"}`)
      );
      const run = el("span", "source-run");
      if (s.last_run_at) {
        run.append(
          document.createTextNode(`Last run ${timeAgo(s.last_run_at)}`),
          el("span", `status status-${s.last_status}`, s.last_status)
        );
      } else {
        run.textContent = "Never run";
      }
      li.append(run);
      return li;
    })
  );
}

async function loadSources() {
  try {
    renderSources(await fetchSources());
  } catch (err) {
    $("source-list").replaceChildren(el("li", "source-note", `Could not load sources: ${err.message}`));
  }
}

async function loadJobs() {
  try {
    const data = await fetchJobs({ search: state.search, limit: PAGE_SIZE, offset: state.offset });
    state.total = data.count;

    // Deleting the last job on a page leaves it empty: step back one page.
    if (data.results.length === 0 && state.offset > 0) {
      state.offset = Math.max(0, state.offset - PAGE_SIZE);
      return loadJobs();
    }

    const list = $("job-list");
    list.replaceChildren(...data.results.map(renderJob));
    $("empty").hidden = data.results.length > 0;

    const from = data.count ? state.offset + 1 : 0;
    const to = state.offset + data.results.length;
    $("summary").textContent = `Showing ${from}–${to} of ${data.count} job${data.count === 1 ? "" : "s"}`;

    const pages = Math.max(1, Math.ceil(data.count / PAGE_SIZE));
    $("page-info").textContent = `Page ${Math.floor(state.offset / PAGE_SIZE) + 1} of ${pages}`;
    $("prev").disabled = state.offset === 0;
    $("next").disabled = state.offset + PAGE_SIZE >= data.count;
  } catch (err) {
    $("summary").textContent = `Could not load jobs: ${err.message}`;
  }
}

// ---------- Events ----------

let searchTimer;
$("search").addEventListener("input", (e) => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {   // wait until the user stops typing (debounce)
    state.search = e.target.value.trim();
    state.offset = 0;
    loadJobs();
  }, 300);
});

$("prev").addEventListener("click", () => {
  state.offset = Math.max(0, state.offset - PAGE_SIZE);
  loadJobs();
});

$("next").addEventListener("click", () => {
  state.offset += PAGE_SIZE;
  loadJobs();
});

$("add-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const msg = $("form-msg");
  const f = new FormData(form);

  const job = {
    title: f.get("title").trim(),
    company: f.get("company").trim(),
    location: f.get("location").trim(),
    url: f.get("url").trim(),
    skills: f.get("skills").split(",").map((s) => s.trim().toLowerCase()).filter(Boolean),
    posted_at: f.get("posted_at") ? new Date(f.get("posted_at")).toISOString() : null,
  };

  if (!job.title || !job.company || !job.url) {
    msg.className = "form-msg err";
    msg.textContent = "Title, company and URL are required.";
    return;
  }

  const button = form.querySelector("button");
  button.disabled = true;
  try {
    const { status, body } = await createJob(job);
    if (status === 201) {
      msg.className = "form-msg ok";
      msg.textContent = state.online ? "Saved." : "Saved in sample data only (API offline).";
      form.reset();
      state.offset = 0;
      await loadJobs();
    } else if (status === 400) {
      msg.className = "form-msg err";
      msg.textContent = firstFieldError(body);
    } else if (status === 429) {
      msg.className = "form-msg err";
      msg.textContent = "Too many requests. Wait a minute and try again.";
    } else {
      msg.className = "form-msg err";
      msg.textContent = `Server error (${status}).`;
    }
  } catch (err) {
    msg.className = "form-msg err";
    msg.textContent = `Could not reach the API: ${err.message}`;
  } finally {
    button.disabled = false;
  }
});

async function onDelete(job, button) {
  if (!confirm(`Delete "${job.title}" at ${job.company}?`)) return;
  button.disabled = true;
  try {
    const status = await deleteJob(job.id);
    if (status !== 204 && status !== 404) throw new Error(`server answered ${status}`);
    await loadJobs(); // 404 means it was already gone: just refresh
  } catch (err) {
    button.disabled = false;
    $("summary").textContent = `Could not delete: ${err.message}`;
  }
}

$("fetch-btn").addEventListener("click", async () => {
  const button = $("fetch-btn");
  const msg = $("fetch-msg");
  const say = (text, kind = "") => { msg.className = `form-msg ${kind}`; msg.textContent = text; };

  state.fetching = true;
  button.disabled = true;
  button.textContent = "Fetching…";
  say("Starting…");
  try {
    const { status, body } = await startFetch("all");
    if (status === 404) return say("The backend has no /fetch endpoint yet (Week 2).", "err");
    if (status !== 202) return say(body?.detail || `Could not start (server answered ${status}).`, "err");

    // 1. The parent task (fetch_all_sources) only starts one child task per source.
    const parent = await pollTask(body.task_id, (t) => say(`Queued · ${t.state}`));
    if (parent.state !== "SUCCESS") {
      return say(parent.state === "TIMEOUT" ? "Still running in the background. Refresh later." : "Fetch failed. Check the worker log.", "err");
    }

    // 2. Wait for every source's task. A single-source fetch has an object result, not a list.
    const childIds = Array.isArray(parent.result) ? parent.result : [];
    let finished = 0;
    say(`Fetching ${childIds.length} sources…`);
    const children = await Promise.all(
      childIds.map((id) =>
        pollTask(id).then((t) => { finished += 1; say(`Fetching… ${finished}/${childIds.length} done`); return t; })
      )
    );
    if (!childIds.length && parent.result) children.push(parent);

    const ok = children.filter((t) => t.state === "SUCCESS");
    const newJobs = ok.reduce((sum, t) => sum + (t.result?.new || 0), 0);
    const failed = children.length - ok.length;
    say(
      `Done: ${newJobs} new job${newJobs === 1 ? "" : "s"}` + (failed ? ` · ${failed} source(s) failed or still running` : "."),
      failed ? "err" : "ok"
    );
    state.offset = 0;
    await Promise.all([loadJobs(), loadSources()]);
  } catch (err) {
    say(`Could not reach the API: ${err.message}`, "err");
  } finally {
    state.fetching = false;
    button.textContent = "Fetch now";
    await loadSources(); // decides if the button is usable (disabled before Week 2)
  }
});

// ---------- Start ----------

(async function start() {
  state.online = await checkHealth();
  renderStatus();
  await Promise.all([loadJobs(), loadSources()]);
})();
