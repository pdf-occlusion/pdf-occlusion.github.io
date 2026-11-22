// Signed in, each quiz's practice (practice.js) is kept on the account too,
// so it follows the student to every device. Changes are sent at most once
// every 10 seconds per quiz, and when the page is hidden or closed; a quiz's
// copy is fetched when it is opened, and every copy when the quiz home
// opens. Offline or failing, everything stays in this browser and goes with
// the next change. Signed out, nothing is sent; what was done then goes up
// the next time someone signs in here.
import { api, API } from "/assets/app.js";
import * as P from "/assets/practice.js";

const EVERY_MS = 10_000;
const LIMIT = 950_000;                 // the server takes 1,000,000 characters
const KEEPALIVE = 60_000;              // a request sent while the page closes is capped at 64 KB
const enc = encodeURIComponent;

let user = null, token = "";
const base = new Map();                // quiz id -> the account copy's version last seen
const last = new Map();                // quiz id -> when it was last sent
const timers = new Map();
const busy = new Map();

// po-sync: { uid: who this browser last synced for, dirty: { quiz id: change count } }
function state() {
  try {
    const s = JSON.parse(localStorage.getItem("po-sync") || "null");
    if (s && s.dirty) return s;
  } catch {}
  // first time here: everything already played is still to send
  return { uid: "", dirty: Object.fromEntries(P.syncedQuizzes().map((id) => [id, 1])) };
}
function store(s) { try { localStorage.setItem("po-sync", JSON.stringify(s)); } catch {} }
const dirty = () => state().dirty;
function markDirty(id) { const s = state(); s.dirty[id] = (s.dirty[id] || 0) + 1; store(s); }
function markClean(id, count) { const s = state(); if (s.dirty[id] === count) { delete s.dirty[id]; store(s); } }

P.onChange((id) => { markDirty(id); schedule(id); });

const q = (id) => { const t = P.tokenOf(id); return t ? `?t=${enc(t)}` : ""; };
const url = (id) => `/v1/quiz/${enc(id)}/progress${q(id)}`;

async function freshToken() {
  try { token = await user.getIdToken(); } catch {}
  return token;
}

// Who is signed in (or null). Call before reading practice.js.
export function setUser(u) {
  user = u || null;
  if (!user) return;
  freshToken();
  const s = state();
  if (s.uid && s.uid !== user.uid) P.forgetExcept(new Set(Object.keys(s.dirty)));
  if (s.uid !== user.uid) { s.uid = user.uid; store(s); }
}

// The account's copy of a quiz, brought into this browser.
async function pullOne(id) {
  const r = await api(url(id), { user });
  base.set(id, r.updated_at || 0);
  return P.mergeQuiz(id, r.data);
}

// These quizzes' copies, before a quiz opens; at most `wait` ms.
export async function pull(ids, wait = 4000) {
  if (!user) return;
  const go = Promise.all(ids.map((id) => pullOne(id).then((more) => { if (more) { markDirty(id); schedule(id); } }, () => {})));
  await Promise.race([go, new Promise((r) => setTimeout(r, wait))]);
}

// Every copy on the account, without the tests' answers (they come when a
// test opens), then whatever is still to send.
export async function pullAll() {
  if (!user) return;
  try {
    const { progress = [] } = await api("/v1/progress", { user });
    for (const row of progress) if (P.mergeQuiz(row.quiz_id, row.data)) markDirty(row.quiz_id);
  } catch {}
  flushAll();
}

function schedule(id) {
  if (!user || timers.has(id)) return;
  const wait = Math.max(0, (last.get(id) || 0) + EVERY_MS - Date.now());
  timers.set(id, setTimeout(() => { timers.delete(id); push(id); }, Math.max(wait, 1500)));
}

// Send one quiz now (a finished test, say).
export function pushNow(id) { clearTimeout(timers.get(id)); timers.delete(id); return push(id); }

export function flushAll() { for (const id of Object.keys(dirty())) schedule(id); }

async function push(id) {
  if (!user) return;
  if (busy.get(id)) { busy.set(id, "again"); return; }
  busy.set(id, true);
  try {
    const count = dirty()[id];
    if (count === undefined) return;
    if (!base.has(id) && !(await pullOne(id))) { markClean(id, count); return; }
    last.set(id, Date.now());
    await freshToken();
    for (let k = 0; k < 3; k++) {
      const data = P.exportQuiz(id, LIMIT);
      if (!data) { markClean(id, count); return; }
      try {
        const r = await api(url(id), { method: "PUT", body: { data, base: base.get(id) || 0 }, user });
        base.set(id, r.updated_at);
        markClean(id, count);
        return;
      } catch (e) {
        if (e.status === 409 && e.data && "updated_at" in e.data) {
          base.set(id, e.data.updated_at);
          if (!P.mergeQuiz(id, e.data.data)) { markClean(id, count); return; }
          continue;
        }
        // no longer allowed (the link changed, the quiz is gone) or too big: stays here only
        if (e.status === 404 || e.status === 413 || e.status === 400) markClean(id, count);
        return;
      }
    }
  } catch {
    // offline: kept, and sent with the next change
  } finally {
    const again = busy.get(id) === "again";
    busy.delete(id);
    if (again) schedule(id);
  }
}

// Closing or hiding the page: whatever is waiting goes now, in a request
// that outlives the page, if it is small enough.
function leaving() {
  if (!user || !token) return;
  for (const id of Object.keys(dirty())) {
    if (!base.has(id) || busy.get(id)) continue;
    const data = P.exportQuiz(id, LIMIT);
    if (!data) continue;
    const body = JSON.stringify({ data, base: base.get(id) || 0 });
    if (body.length > KEEPALIVE) { push(id); continue; }
    clearTimeout(timers.get(id)); timers.delete(id);
    const count = dirty()[id];
    last.set(id, Date.now());
    busy.set(id, true);
    fetch(API + url(id), { method: "PUT", keepalive: true, headers: { "content-type": "application/json", authorization: `Bearer ${token}` }, body })
      .then((r) => (r.ok ? r.json() : Promise.reject(r)))
      .then((r) => { base.set(id, r.updated_at); markClean(id, count); }, () => {})
      .finally(() => { const again = busy.get(id) === "again"; busy.delete(id); if (again) schedule(id); });
  }
}
addEventListener("pagehide", leaving);
document.addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") leaving(); });
