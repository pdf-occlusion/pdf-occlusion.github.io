// Practice history in this browser (localStorage), shared by the quiz player
// and the quiz home. Signed in, sync.js copies each quiz's part to the
// account so it follows the student to other devices (exportQuiz, mergeQuiz).
//
//   po-qh-<quiz id>  one quiz: { name, n, q, a: { index: [{ p, ok, t, r }] },
//                                m: { index: { f, h, u } }, x: { test: time } }
//                    `a` is every answer ever submitted to each question (`r`
//                    is the test it was made in), `m` the question's flag and
//                    highlights (`u` when last changed; cleared ones stay as
//                    { u }), `x` tests deleted, `q` the query that reopens it.
//   po-tests         every test: { id: { scope, q, where, label, n, right,
//                                 wrong, done, started, updated, ended?, quizzes } }
//   po-run-<test>    one test's answers: { v, current, all, order, redo,
//                                 responses: { "quiz:index": { ..., u } } }
//   po-qids          short question id -> quiz id, for starting a quiz by ids
//
// A test is synced with its first quiz (homeOf), sorted by id.

// Told the quiz id whenever a quiz's synced part changes.
let changed = () => {};
export function onChange(fn) { changed = fn; }

function get(key, fallback) {
  try { const v = localStorage.getItem(key); return v ? JSON.parse(v) : fallback; } catch { return fallback; }
}
function put(key, value) {
  try { localStorage.setItem(key, JSON.stringify(value)); } catch {}
}
function drop(key) {
  try { localStorage.removeItem(key); } catch {}
}
function keys(prefix) {
  const out = [];
  try { for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); if (k && k.startsWith(prefix)) out.push(k); } } catch {}
  return out;
}

// Short and stable.
export function hash(text) {
  let h = 5381;
  for (let i = 0; i < text.length; i++) h = ((h * 33) ^ text.charCodeAt(i)) >>> 0;
  return h.toString(36);
}

// A question's short id, stirred so neighbours do not look alike.
export function qid(quizId, i) {
  let h = parseInt(hash(`${quizId}:${i}`), 36);
  h = Math.imul(h ^ (h >>> 16), 0x45d9f3b) >>> 0;
  return ((h ^ (h >>> 16)) >>> 0).toString(36);
}

// ------------------------------------------------ one quiz's history
const QH = (id) => `po-qh-${id}`;
function doc(id) {
  const d = get(QH(id), null) || {};
  if (!d.a) d.a = {};
  if (!d.m) d.m = {};
  return d;
}

function save(id, d) { put(QH(id), d); changed(id); }

// What the quiz home needs to list and reopen a quiz played here.
export function noteQuiz(id, info) {
  const d = doc(id);
  // keep the share token a link to this quiz came with
  if (info.q && !/(^|&)t=/.test(info.q) && /(^|&)t=/.test(d.q || "")) info = { ...info, q: d.q };
  if (Object.keys(info).every((k) => d[k] === info[k])) return;
  Object.assign(d, info);
  save(id, d);
}

export function attempts(id, i) { return doc(id).a[i] || []; }

export function addAttempt(id, i, p, ok, r) {
  const d = doc(id);
  (d.a[i] = d.a[i] || []).push({ p, ok, t: Date.now(), ...(r ? { r } : {}) });
  save(id, d);
}

export function mark(id, i) {
  const m = doc(id).m[i];
  return m ? { flagged: !!m.f, highlights: m.h || {} } : null;
}

export function setMark(id, i, flagged, highlights) {
  const d = doc(id);
  const h = highlights && Object.keys(highlights).length ? highlights : null;
  d.m[i] = { ...(flagged ? { f: true } : {}), ...(h ? { h } : {}), u: Date.now() };
  save(id, d);
}

// How many questions have been tried, how many were right on the last try,
// and how many are flagged.
export function stats(id, n) {
  const d = doc(id);
  let seen = 0, right = 0, flagged = 0;
  for (const [i, list] of Object.entries(d.a)) {
    if (!list.length || (n && Number(i) >= n)) continue;
    seen++;
    if (list[list.length - 1].ok) right++;
  }
  for (const m of Object.values(d.m)) if (m.f) flagged++;
  return { seen, right, flagged };
}

// Every quiz played in this browser.
export function quizzesPlayed() {
  return keys("po-qh-").map((k) => {
    const id = k.slice(6), d = doc(id);
    return { id, name: d.name, n: d.n, q: d.q, ...stats(id, d.n) };
  });
}

// ------------------------------------------------ tests
export const tests = () => get("po-tests", {});
export const test = (id) => tests()[id] || null;

export function listTests() {
  return Object.entries(tests()).map(([id, t]) => ({ id, ...t })).sort((a, b) => (b.updated || 0) - (a.updated || 0));
}

// The unfinished test for this scope, if there is one.
export function openTest(scope) {
  const t = listTests().find((x) => x.scope === scope && !x.done && !x.ended);
  return t ? t.id : null;
}

export const readRun = (id) => get(`po-run-${id}`, null);

export const homeOf = (line) => (line && Array.isArray(line.quizzes) && line.quizzes.length ? line.quizzes.slice().sort()[0] : null);
const testChanged = (line) => { const h = homeOf(line); if (h) changed(h); };

export function saveRun(id, run, line) {
  const all = tests();
  // nothing new (a question shown again): not saved, nor sent
  const was = all[id];
  if (was && JSON.stringify(readRun(id)) === JSON.stringify(run) && Object.keys(line).every((k) => JSON.stringify(was[k]) === JSON.stringify(line[k]))) return;
  put(`po-run-${id}`, run);
  all[id] = { ...(all[id] || {}), ...line, updated: Date.now() };
  put("po-tests", all);
  testChanged(all[id]);
}

export function endTest(id) {
  const all = tests();
  if (!all[id]) return;
  all[id].ended = all[id].updated = Date.now();
  put("po-tests", all);
  testChanged(all[id]);
}

// A deleted test takes its answers with it, out of each question's history.
export function deleteTest(id) {
  const all = tests();
  const line = all[id];
  for (const quizId of (line && line.quizzes) || []) {
    const d = doc(quizId);
    for (const i of Object.keys(d.a)) {
      d.a[i] = d.a[i].filter((a) => a.r !== id);
      if (!d.a[i].length) delete d.a[i];
    }
    // remembered, so another device's copy of the test goes too
    (d.x = d.x || {})[id] = Date.now();
    save(quizId, d);
  }
  delete all[id];
  put("po-tests", all);
  drop(`po-run-${id}`);
}

// ------------------------------------------------ question ids
export function rememberQids(quizId, n) {
  const map = get("po-qids", {});
  for (let i = 0; i < n; i++) map[qid(quizId, i)] = quizId;
  put("po-qids", map);
}
export const whereQid = (id) => get("po-qids", {})[id] || null;

// Progress saved by the earlier player ({ resp, order, cur } per quiz), once.
export function takeOldProgress(quizId) {
  const old = get(`po-quiz-${quizId}`, null);
  if (old) drop(`po-quiz-${quizId}`);
  return old;
}

// ------------------------------------------------ sync
// One quiz's part, as kept on the account: its doc, and its tests with their
// answers. Over `limit` characters, the oldest finished tests go without
// their answers (they stay here).
export function exportQuiz(id, limit = Infinity) {
  if (!localStorage.getItem(QH(id)) && !listTests().some((t) => homeOf(t) === id)) return null;
  const d = doc(id), t = {};
  const mine = listTests().filter((x) => homeOf(x) === id);
  for (const x of mine) {
    const { id: tid, ...line } = x;
    const run = readRun(tid);
    t[tid] = run ? { line, run } : { line };
  }
  const out = { v: 1, ...d, t };
  let text = JSON.stringify(out);
  const finished = mine.filter((x) => (x.done || x.ended) && t[x.id].run).sort((a, b) => (a.updated || 0) - (b.updated || 0));
  while (text.length > limit && finished.length) {
    delete t[finished.shift().id].run;
    text = JSON.stringify(out);
  }
  return text.length > limit ? null : out;
}

const tryKey = (a) => `${a.t || 0}|${a.p}|${a.ok ? 1 : 0}|${a.r || ""}`;
const newer = (a, b) => ((a && a.u) || 0) >= ((b && b.u) || 0) ? a : b;

// Two copies of one question's flag and highlights: the later one. Older
// copies without a time (u) are combined instead.
function mergeMark(a, b) {
  if (!a || !b) return a || b;
  if (!a.u && !b.u) {
    const h = a.h || b.h;
    return { ...(a.f || b.f ? { f: true } : {}), ...(h ? { h } : {}) };
  }
  return newer(a, b);
}

// One test's answers from two copies: each question's later answer, the
// rest (order, where it is) from the copy saved last.
function mergeRun(a, b, aFirst) {
  if (!a || !b) return a || b;
  const [main, other] = aFirst ? [a, b] : [b, a];
  const responses = { ...(other.responses || {}) };
  for (const [k, r] of Object.entries(main.responses || {})) responses[k] = responses[k] ? newer(r, responses[k]) : r;
  return { ...main, responses };
}

function mergeLine(a, b) {
  if (!a || !b) return a || b;
  const main = (a.updated || 0) >= (b.updated || 0) ? a : b;
  const out = { ...main };
  const ended = Math.max(a.ended || 0, b.ended || 0);
  if (ended) out.ended = ended;
  if (a.started && b.started) out.started = Math.min(a.started, b.started);
  return out;
}

// Brings the account's copy of a quiz (`remote`, as exportQuiz makes it, its
// tests' answers possibly left out) into this browser. No try is lost:
// tries are joined; flags, highlights and each question's answer in a test
// keep the later change; deleted tests stay deleted. Returns whether the
// result has anything the remote copy lacks (so it should be sent back).
export function mergeQuiz(id, remote) {
  if (!remote || typeof remote !== "object") return !!exportQuiz(id);
  const d = doc(id);
  for (const k of ["name", "n", "q"]) if (d[k] == null && remote[k] != null) d[k] = remote[k];
  // a link with the share token in it opens the quiz on any device
  if (remote.q && /(^|&)t=/.test(remote.q) && !/(^|&)t=/.test(d.q || "")) d.q = remote.q;
  if (remote.n > (d.n || 0)) d.n = remote.n;
  const x = { ...(remote.x || {}) };
  for (const [k, v] of Object.entries(d.x || {})) x[k] = Math.max(x[k] || 0, v);
  if (Object.keys(x).length) d.x = x;
  const a = {};
  for (const i of new Set([...Object.keys(d.a), ...Object.keys(remote.a || {})])) {
    const seen = new Map();
    for (const t of [...(d.a[i] || []), ...((remote.a || {})[i] || [])]) if (!(t.r && x[t.r])) seen.set(tryKey(t), t);
    const list = [...seen.values()].sort((p, q) => (p.t || 0) - (q.t || 0));
    if (list.length) a[i] = list;
  }
  d.a = a;
  for (const [i, m] of Object.entries(remote.m || {})) d.m[i] = mergeMark(d.m[i], m);
  put(QH(id), d);

  const all = tests();
  for (const [tid, rt] of Object.entries(remote.t || {})) {
    if (x[tid] || !rt || !rt.line) continue;
    const mine = all[tid];
    const line = mergeLine(mine, rt.line);
    const run = mergeRun(readRun(tid), rt.run, !mine || (rt.line.updated || 0) <= (mine.updated || 0));
    all[tid] = line;
    if (run) put(`po-run-${tid}`, run);
  }
  for (const tid of Object.keys(x)) if (all[tid]) { delete all[tid]; drop(`po-run-${tid}`); }
  put("po-tests", all);
  if (d.n) rememberQids(id, d.n);

  const mineNow = exportQuiz(id);
  return !!mineNow && !sameAs(mineNow, remote);
}

// Whether the account's copy already has everything this one has.
function sameAs(local, remote) {
  const strip = (o) => {
    const c = { ...o, t: {} };
    for (const [k, v] of Object.entries(o.t || {})) c.t[k] = v.line;
    return c;
  };
  const stable = (v) => (Array.isArray(v) ? `[${v.map(stable).join(",")}]` : v && typeof v === "object" ? `{${Object.keys(v).sort().map((k) => `${k}:${stable(v[k])}`).join(",")}}` : JSON.stringify(v));
  if (stable(strip(local)) !== stable(strip(remote))) return false;
  // answers this browser has for a test the remote copy keeps without them
  return Object.entries(local.t || {}).every(([k, v]) => !v.run || (remote.t?.[k]?.run && stable(v.run) === stable(remote.t[k].run)));
}

// Every quiz with something here to sync.
export function syncedQuizzes() {
  const ids = new Set(keys("po-qh-").map((k) => k.slice(6)));
  for (const t of listTests()) { const h = homeOf(t); if (h) ids.add(h); }
  return [...ids];
}

// The share token a quiz was opened with, if any.
export function tokenOf(id) {
  try { return new URLSearchParams(doc(id).q || "").get("t") || ""; } catch { return ""; }
}

// Another account signed in on this browser: what the last one synced goes
// (it is on that account), except quizzes with changes not yet sent.
export function forgetExcept(keep) {
  const all = tests();
  for (const id of syncedQuizzes()) {
    if (keep.has(id)) continue;
    drop(QH(id));
    for (const [tid, line] of Object.entries(all)) if (homeOf(line) === id) { delete all[tid]; drop(`po-run-${tid}`); }
  }
  put("po-tests", all);
}

// A deleted quiz: its practice here and the tests made from it go.
export function forgetQuiz(id) {
  const all = tests();
  drop(QH(id));
  for (const [tid, line] of Object.entries(all)) if (homeOf(line) === id) { delete all[tid]; drop(`po-run-${tid}`); }
  put("po-tests", all);
}
