// Practice history, kept only in this browser (localStorage), shared by the
// quiz player and the account page. Nothing here is sent to the server.
//
//   po-qh-<quiz id>  one quiz: { name, n, q, a: { index: [{ p, ok, t, r }] },
//                                m: { index: { f, h } } }
//                    `a` is every answer ever submitted to each question (`r`
//                    is the test it was made in), `m` the question's flag and
//                    highlights, `q` the query that reopens the quiz.
//   po-tests         every test: { id: { scope, q, where, label, n, right,
//                                 wrong, done, started, updated, ended?, quizzes } }
//   po-run-<test>    one test's answers: { v, current, all, order, redo, responses }
//   po-qids          short question id -> quiz id, for starting a quiz by ids

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

// What the account page needs to list and reopen a quiz played here.
export function noteQuiz(id, info) {
  const d = doc(id);
  Object.assign(d, info);
  put(QH(id), d);
}

export function attempts(id, i) { return doc(id).a[i] || []; }

export function addAttempt(id, i, p, ok, r) {
  const d = doc(id);
  (d.a[i] = d.a[i] || []).push({ p, ok, t: Date.now(), ...(r ? { r } : {}) });
  put(QH(id), d);
}

export function mark(id, i) {
  const m = doc(id).m[i];
  return m ? { flagged: !!m.f, highlights: m.h || {} } : null;
}

export function setMark(id, i, flagged, highlights) {
  const d = doc(id);
  const h = highlights && Object.keys(highlights).length ? highlights : null;
  if (!flagged && !h) delete d.m[i];
  else d.m[i] = { f: !!flagged, ...(h ? { h } : {}) };
  put(QH(id), d);
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

export function saveRun(id, run, line) {
  put(`po-run-${id}`, run);
  const all = tests();
  all[id] = { ...(all[id] || {}), ...line, updated: Date.now() };
  put("po-tests", all);
}

export function endTest(id) {
  const all = tests();
  if (!all[id]) return;
  all[id].ended = Date.now();
  put("po-tests", all);
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
    put(QH(quizId), d);
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
