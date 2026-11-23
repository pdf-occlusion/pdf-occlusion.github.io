// The quiz player: /quiz/?id=<quiz>[&t=<share token>] plays one quiz, signed
// in or not. Signed in, ?set=<id>,<id> plays several of your quizzes shuffled
// together and ?q=<question ids> plays questions picked by id. ?only=missed,
// unseen or flagged narrows any of them by your history here; ?test=<id>
// reopens one test from the quiz home. Answers, flags, highlights and the
// history of every try are kept in this browser (practice.js) and, signed
// in, on the account so they follow you to other devices (sync.js).
import { watchUser, signIn, api, quizImage } from "/assets/app.js";
import * as P from "/assets/practice.js";
import * as S from "/assets/sync.js";

const $ = (id) => document.getElementById(id);
const params = new URLSearchParams(location.search);
const quizId = params.get("id") || "";
const token = params.get("t") || "";
const setIds = [...new Set((params.get("set") || "").split(",").map((s) => s.trim()).filter(Boolean))];
const qids = [...new Set((params.get("q") || "").toLowerCase().split(/[^a-z0-9]+/).filter(Boolean))];
const only = ["missed", "unseen", "flagged"].includes(params.get("only")) ? params.get("only") : "";
const enc = encodeURIComponent;

const show = (id) => { for (const k of ["q-loading", "q-out", "q-play"]) $(k).classList.toggle("hidden", k !== id); };
const err = (m) => { $("q-error").textContent = m; $("q-error").classList.remove("hidden"); };
const message = (m) => { show(""); $("q-loading").textContent = m; $("q-loading").classList.remove("hidden"); };

let user = null, begun = false;
$("sign-in").addEventListener("click", () => signIn().catch((e) => err(e.message)));

// ------------------------------------------------ what is in play
// Every question loaded, in play order: { ...question, _quiz, _i, _lecture }.
let questions = [];
// Which of them are in view (indices into `questions`) and where we are in it.
let view = [], current = 0;
// A redo narrows the view to the questions missed, cleared to answer again;
// `showAll` widens it back onto the rest, which keep their answers.
let redo = null, showAll = false;
// One record per question: { selected, answered, struck, flagged, skipped,
// highlights, u }; `u` is when its answer last changed, so two devices'
// copies of a test keep each question's later answer.
let responses = [];
let resultsOpen = false;
let owner = false;

const syncView = () => { view = redo && !showAll ? redo.slice() : questions.map((_, i) => i); };
const cur = () => view[current];
const qKey = (q) => `${q._quiz}:${q._i}`;
function response(i) {
  if (!responses[i]) responses[i] = { selected: null, answered: false, struck: [], flagged: false, skipped: false, highlights: {} };
  return responses[i];
}
const bump = (r) => { r.u = Date.now(); return r; };

// ------------------------------------------------ tests
const SCOPE = (quizId ? `quiz-${quizId}` : setIds.length ? `set-${P.hash(setIds.slice().sort().join(","))}` : `ids-${P.hash(qids.slice().sort().join(","))}`) + (only ? `-${only}` : "");
const SCOPE_QUERY = ["id", "t", "set", "q", "only"].filter((k) => params.get(k)).map((k) => `${k}=${enc(params.get(k))}`).join("&");
let RUN_KEY = SCOPE, startedAt = Date.now();
const newTestId = () => `${SCOPE}-${Date.now().toString(36)}`;

function settleTest() {
  const asked = params.get("test");
  if (asked) RUN_KEY = asked.replace(/[^\w-]/g, "_");
  else RUN_KEY = P.openTest(SCOPE) || newTestId();
  const line = P.test(RUN_KEY);
  if (line && line.started) startedAt = line.started;
}

function touched(r) { return !!(r && (r.selected || r.answered || r.skipped || r.struck.length)); }

function tally() {
  let correct = 0, wrong = 0, flagged = 0, skipped = 0;
  for (const i of view) {
    const r = responses[i];
    if (!r) continue;
    if (r.flagged) flagged++;
    if (r.answered) r.selected === questions[i].correct ? correct++ : wrong++;
    else if (r.skipped) skipped++;
  }
  return { correct, wrong, total: correct + wrong, flagged, skipped };
}

function saveSession() {
  const byKey = {};
  // only what is set; a question put back to untouched keeps its time (u)
  responses.forEach((r, i) => {
    if (!r || !(touched(r) || r.u)) return;
    const o = {};
    if (r.selected) o.selected = r.selected;
    if (r.answered) o.answered = true;
    if (r.struck.length) o.struck = r.struck;
    if (r.skipped) o.skipped = true;
    if (r.u) o.u = r.u;
    byKey[qKey(questions[i])] = o;
  });
  // an untouched test is not worth keeping; a touched one is, even reset
  if (!Object.keys(byKey).length && !P.test(RUN_KEY)) return;
  let right = 0, wrong = 0;
  responses.forEach((r, i) => { if (r && r.answered) r.selected === questions[i].correct ? right++ : wrong++; });
  P.saveRun(RUN_KEY, {
    v: 1, current, all: showAll,
    order: questions.map(qKey),
    redo: redo && redo.map((i) => qKey(questions[i])),
    responses: byKey,
  }, {
    scope: SCOPE, q: SCOPE_QUERY,
    where: $("q-title").textContent, label: $("q-sub").textContent,
    n: questions.length, right, wrong, done: right + wrong === questions.length,
    started: startedAt, quizzes: [...new Set(questions.map((q) => q._quiz))],
  });
}

const saveMark = (i) => { const r = response(i), q = questions[i]; P.setMark(q._quiz, q._i, r.flagged, r.highlights); };

// Progress the earlier player kept ({ resp, order, cur }), brought into a test.
function importOld() {
  const old = P.takeOldProgress(quizId);
  if (!old || !Array.isArray(old.order) || !old.order.length) return null;
  const n = questions.length;
  const responses = {};
  for (const [i, r] of Object.entries(old.resp || {})) {
    if (Number(i) < n && r) responses[`${quizId}:${i}`] = { selected: r.selected || null, answered: !!r.answered, struck: r.struck || [], skipped: false };
  }
  return { v: 1, current: old.cur || 0, all: false, order: old.order.filter((i) => i < n).map((i) => `${quizId}:${i}`), redo: null, responses };
}

function readSession() {
  const saved = P.readRun(RUN_KEY);
  return saved && Array.isArray(saved.order) ? saved : null;
}

// Back to the saved order and answers; questions not in it go at the end.
function restoreSession(saved) {
  if (!saved) return false;
  const pos = new Map(saved.order.map((k, i) => [k, i]));
  const known = [], fresh = [];
  for (const q of questions) (pos.has(qKey(q)) ? known : fresh).push(q);
  if (!known.length) return false;
  known.sort((a, b) => pos.get(qKey(a)) - pos.get(qKey(b)));
  questions = known.concat(fresh);
  responses = questions.map((q) => {
    const r = saved.responses && saved.responses[qKey(q)];
    return r ? { selected: r.selected || null, answered: !!r.answered, struck: Array.isArray(r.struck) ? r.struck : [], flagged: false, skipped: !!r.skipped, highlights: {}, ...(r.u ? { u: r.u } : {}) } : null;
  });
  const at = new Map(questions.map((q, i) => [qKey(q), i]));
  redo = Array.isArray(saved.redo) ? saved.redo.map((k) => at.get(k)).filter((i) => i !== undefined) : null;
  if (redo && !redo.length) redo = null;
  showAll = !!(redo && saved.all);
  syncView();
  current = Math.min(Math.max(parseInt(saved.current, 10) || 0, 0), view.length);
  if (current >= view.length) {
    const open = view.findIndex((i) => !responses[i] || !responses[i].answered);
    if (open !== -1 && questions.length > saved.order.length) current = open;
  }
  return true;
}

function applyMarks() {
  questions.forEach((q, i) => {
    const m = P.mark(q._quiz, q._i);
    if (!m) return;
    const r = response(i);
    r.flagged = m.flagged;
    r.highlights = JSON.parse(JSON.stringify(m.highlights));
  });
}

// Whether a question belongs in an ?only= test.
function wanted(q) {
  if (only === "flagged") { const m = P.mark(q._quiz, q._i); return !!(m && m.flagged); }
  const tries = P.attempts(q._quiz, q._i);
  return only === "unseen" ? !tries.length : !!tries.length && !tries[tries.length - 1].ok;
}

function shuffle(arr) {
  for (let i = arr.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [arr[i], arr[j]] = [arr[j], arr[i]]; }
}

// ------------------------------------------------ loading
const fetchQuiz = (id, t) => api(`/v1/quiz/${enc(id)}${t ? `?t=${enc(t)}` : ""}`, { user });

// Questions by short id: the quizzes this browser knows them from first,
// then the rest of your quizzes until every id is found.
async function byIds() {
  const got = new Map();
  const found = () => new Set([...got.values()].flatMap((z) => z.questions.map((_, i) => P.qid(z.id, i))));
  const fetchAll = (ids) => Promise.all(ids.filter((id) => !got.has(id)).map((id) => fetchQuiz(id).then((z) => got.set(id, z), () => {})));
  await fetchAll([...new Set(qids.map(P.whereQid).filter(Boolean))]);
  if (qids.some((x) => !found().has(x))) {
    const { quizzes = [] } = await api("/v1/quizzes", { user });
    const rest = quizzes.map((z) => z.id).filter((id) => !got.has(id));
    for (let k = 0; k < rest.length && qids.some((x) => !found().has(x)); k += 6) await fetchAll(rest.slice(k, k + 6));
  }
  return [...got.values()];
}

async function load() {
  let quizzes;
  try {
    if (quizId) quizzes = [await fetchQuiz(quizId, token)];
    else {
      if (!user) { begun = false; show("q-out"); return; }
      quizzes = setIds.length ? (await Promise.all(setIds.map((id) => fetchQuiz(id).catch(() => null)))).filter(Boolean) : await byIds();
    }
  } catch (e) {
    // someone else's link without its token, or the owner signed out: sign in, then try again
    if (e.status === 404 && !user && !token) { begun = false; show("q-out"); return; }
    show("");
    err(e.status === 404 ? "This quiz does not exist, or its link has changed." : e.message);
    return;
  }
  for (const z of quizzes) {
    P.noteQuiz(z.id, { name: z.lecture || "Untitled PDF", n: z.questions.length, q: `id=${enc(z.id)}` + (z.id === quizId && token ? `&t=${enc(token)}` : "") });
    P.rememberQids(z.id, z.questions.length);
  }
  // this quiz as left on your other devices
  if (user) await S.pull(quizzes.map((z) => z.id));
  questions = quizzes.flatMap((z) => z.questions.map((q, i) => ({ ...q, _quiz: z.id, _i: i, _lecture: z.lecture })));
  if (qids.length) {
    const at = new Map(qids.map((id, i) => [id, i]));
    const qidOf = (q) => P.qid(q._quiz, q._i);
    questions = questions.filter((q) => at.has(qidOf(q))).sort((a, b) => at.get(qidOf(a)) - at.get(qidOf(b)));
  }
  owner = !!(quizId && quizzes[0] && quizzes[0].owner);

  const title = quizzes.length === 1 ? quizzes[0].lecture || "Quiz" : "Mixed";
  const sub = [];
  if (setIds.length && quizzes.length > 1) sub.push(`${quizzes.length} quizzes, shuffled`);
  if (qids.length) sub.push(`${questions.length} ${questions.length === 1 ? "question" : "questions"} by ID`);
  if (only) sub.push(`${only} questions`);
  document.title = title;
  $("q-title").textContent = title;
  $("q-sub").textContent = sub.join(", ").replace(/^./, (c) => c.toUpperCase());
  $("q-sub").classList.toggle("hidden", !sub.length);

  if (!questions.length) { message(qids.length ? "No questions with those IDs." : "This quiz has no questions."); return; }

  settleTest();
  let saved = readSession();
  if (!saved && quizId && !only && !P.test(RUN_KEY)) saved = importOld();

  // A narrowed test, or one reopened by id, keeps exactly the questions it
  // started with; a new narrowed test takes a fresh cut of your history.
  if (only || params.get("test")) {
    if (saved) { const kept = new Set(saved.order); questions = questions.filter((q) => kept.has(qKey(q))); }
    else if (only) questions = questions.filter(wanted);
    if (!questions.length) { message(only ? `No ${only} questions here.` : "That test was deleted."); return; }
  }

  const resumed = restoreSession(saved);
  if (!resumed) {
    if (setIds.length > 1) shuffle(questions);
    responses = [];
    syncView();
  }
  applyMarks();
  $("q-share").classList.toggle("hidden", !owner);
  show("q-play");
  if (resumed && current >= view.length) { showResults(); return; }
  render();
}

// ------------------------------------------------ slide images
// {page, box: [x, y, w, h] as fractions of the slide, caption, credit}: only
// the box shows, at its own shape. Each slide is fetched once, when first shown.
const slides = new Map();
const slide = (quiz, im) => {
  const k = `${quiz}:${im.src || im.page}`;
  if (!slides.has(k)) slides.set(k, quizImage(quiz, im, { token: quiz === quizId ? token : "", user }).catch((e) => { slides.delete(k); throw e; }));
  return slides.get(k);
};
addEventListener("pagehide", () => { for (const p of slides.values()) p.then(URL.revokeObjectURL, () => {}); slides.clear(); });
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, Number(v) || 0));
function figure(quiz, im, big = false) {
  const b = Array.isArray(im.box) && im.box.length === 4 ? im.box : [0, 0, 1, 1];
  const x = clamp(b[0], 0, 0.99), y = clamp(b[1], 0, 0.99);
  const w = Number(b[2]) > 0 ? clamp(b[2], 0.01, 1 - x) : 1 - x, h = Number(b[3]) > 0 ? clamp(b[3], 0.01, 1 - y) : 1 - y;
  const fig = document.createElement("figure");
  fig.className = "q-fig";
  const crop = document.createElement("div");
  crop.className = "q-crop";
  const img = document.createElement("img");
  img.alt = im.caption || "Slide";
  Object.assign(img.style, { width: `${100 / w}%`, height: `${100 / h}%`, left: `${(-x / w) * 100}%`, top: `${(-y / h) * 100}%` });
  // the box's shape on a 16:9 slide until the real one is known
  const size = (W, H) => {
    const ratio = (w * W) / (h * H);
    crop.style.aspectRatio = String(ratio);
    crop.style.width = big ? `min(100%, ${ratio * 78}vh)` : `min(100%, ${ratio * 46}vh)`;
  };
  size(16, 9);
  img.addEventListener("load", () => { size(img.naturalWidth, img.naturalHeight); crop.classList.add("ready"); });
  slide(quiz, im).then((src) => { img.src = src; }).catch(() => fig.remove());
  crop.append(img);
  fig.append(crop);
  if (!big) {
    crop.tabIndex = 0;
    crop.setAttribute("role", "button");
    crop.setAttribute("aria-label", "View larger");
    crop.addEventListener("click", () => zoom(quiz, im));
    crop.addEventListener("keydown", (e) => { if (!zoomed && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); e.stopPropagation(); zoom(quiz, im); } });
  }
  if (im.caption || im.credit) {
    const cap = document.createElement("figcaption");
    if (im.caption) { const c = document.createElement("span"); c.textContent = im.caption; cap.append(c); }
    if (im.credit) { const c = document.createElement("span"); c.className = "q-credit"; c.textContent = im.credit; cap.append(c); }
    fig.append(cap);
  }
  return fig;
}
let zoomed = null;
function zoom(quiz, im) {
  hidePop();
  zoomed = document.createElement("div");
  zoomed.className = "q-zoom";
  zoomed.append(figure(quiz, im, true));
  zoomed.addEventListener("click", unzoom);
  document.body.append(zoomed);
}
function unzoom() { zoomed?.remove(); zoomed = null; }

// ------------------------------------------------ tables
function table(rows) {
  const t = document.createElement("table");
  t.className = "q-tbl";
  rows.forEach((row, ri) => {
    const tr = document.createElement("tr");
    for (const c of row) { const cell = document.createElement(ri === 0 ? "th" : "td"); cell.textContent = c; tr.append(cell); }
    t.append(tr);
  });
  const wrap = document.createElement("div");
  wrap.className = "q-tbl-wrap";
  wrap.append(t);
  return wrap;
}

// A table written into the stem as Markdown (| a | b |) comes out as a table.
function splitTable(text) {
  const rows = [], rest = [];
  for (const line of String(text || "").split("\n")) {
    if (/^\|/.test(line.trim())) {
      if (!/^[|\s\-:]+$/.test(line)) rows.push(line.trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim()));
    } else rest.push(line);
  }
  return { rows, rest: rest.join("\n").trim() };
}

// ------------------------------------------------ highlighting
// A highlight is a pair of character offsets into a block's plain text (the
// stem, a choice, an explanation), so it survives re-rendering and reloads.
const hlPop = $("hl-pop"), hlAdd = $("hl-add"), hlDel = $("hl-del");
// placed in page coordinates, so it lives on <body>, not in the centered column
document.body.append(hlPop);
let hlSources = {}, hlPending = null, hlTimer = null;
const highlightsOf = (i) => response(i).highlights;
const esc = (t) => t.replace(/[&<>]/g, (c) => (c === "&" ? "&amp;" : c === "<" ? "&lt;" : "&gt;"));

function paint(el, text, key) {
  hlSources[key] = text;
  el.dataset.hlKey = key;
  const ranges = (highlightsOf(cur())[key] || []).map(([a, b]) => [Math.min(a, text.length), Math.min(b, text.length)]).filter(([a, b]) => b > a);
  if (!ranges.length) { el.textContent = text; return; }
  let html = "", pos = 0;
  for (const [a, b] of ranges) {
    if (a > pos) html += esc(text.slice(pos, a));
    html += `<mark class="hl" data-r="${a},${b}">${esc(text.slice(a, b))}</mark>`;
    pos = Math.max(pos, b);
  }
  el.innerHTML = html + esc(text.slice(pos));
}
function repaint(key) {
  const el = document.querySelector(`[data-hl-key="${CSS.escape(key)}"]`);
  if (el && hlSources[key] != null) paint(el, hlSources[key], key);
}
function mergeRanges(list) {
  const out = [];
  list.slice().sort((x, y) => x[0] - y[0]).forEach(([a, b]) => {
    const last = out[out.length - 1];
    if (last && a <= last[1]) last[1] = Math.max(last[1], b); else out.push([a, b]);
  });
  return out;
}
function subtractRange(list, start, end) {
  const out = [];
  for (const [a, b] of list) {
    if (b <= start || a >= end) { out.push([a, b]); continue; }
    if (a < start) out.push([a, start]);
    if (b > end) out.push([end, b]);
  }
  return out;
}
const overlaps = (key, s, e) => (highlightsOf(cur())[key] || []).some(([a, b]) => a < e && b > s);
function hlBlock(node) {
  const el = node && (node.nodeType === 3 ? node.parentElement : node);
  return el && el.closest ? el.closest("[data-hl-key]") : null;
}
function offsetIn(block, node, offset) {
  const walk = document.createTreeWalker(block, NodeFilter.SHOW_TEXT);
  let n, total = 0;
  while ((n = walk.nextNode())) { if (n === node) return total + offset; total += n.nodeValue.length; }
  return total;
}
// The selection as offsets into the first highlightable block it touches.
function selectionRange() {
  const sel = getSelection();
  if (!sel || sel.isCollapsed || !sel.rangeCount || resultsOpen || !questions.length) return null;
  const range = sel.getRangeAt(0);
  const block = hlBlock(range.startContainer) || hlBlock(range.endContainer);
  if (!block || !$("q-card").contains(block)) return null;
  const key = block.dataset.hlKey, text = hlSources[key];
  if (text == null) return null;
  let start = block.contains(range.startContainer) ? offsetIn(block, range.startContainer, range.startOffset) : 0;
  let end = block.contains(range.endContainer) ? offsetIn(block, range.endContainer, range.endOffset) : text.length;
  if (end < start) [start, end] = [end, start];
  while (start < end && /\s/.test(text[start])) start++;
  while (end > start && /\s/.test(text[end - 1])) end--;
  return end > start ? { key, start, end } : null;
}
function hidePop() { hlPop.classList.remove("visible"); hlPending = null; }
function showPop(rect, canAdd, canDel) {
  hlAdd.hidden = !canAdd;
  hlDel.hidden = !canDel;
  const below = rect.top < 52;
  hlPop.classList.toggle("below", below);
  hlPop.style.left = `${Math.round(rect.left + rect.width / 2 + scrollX)}px`;
  hlPop.style.top = `${Math.round((below ? rect.bottom : rect.top) + scrollY)}px`;
  hlPop.classList.add("visible");
}
function syncPop() {
  const sel = selectionRange();
  if (!sel) { if (!(hlPending && hlPending.fromClick)) hidePop(); return; }
  hlPending = sel;
  showPop(getSelection().getRangeAt(0).getBoundingClientRect(), true, overlaps(sel.key, sel.start, sel.end));
}
function applyHighlight(sel, remove) {
  const store = highlightsOf(cur());
  const had = store[sel.key] || [];
  const next = remove ? subtractRange(had, sel.start, sel.end) : mergeRanges(had.concat([[sel.start, sel.end]]));
  if (next.length) store[sel.key] = next; else delete store[sel.key];
  repaint(sel.key);
  getSelection()?.removeAllRanges();
  hidePop();
  saveMark(cur());
}
hlPop.addEventListener("mousedown", (e) => e.preventDefault());
hlAdd.addEventListener("click", () => { if (hlPending) applyHighlight(hlPending, false); });
hlDel.addEventListener("click", () => { if (hlPending) applyHighlight(hlPending, true); });
document.addEventListener("selectionchange", () => { clearTimeout(hlTimer); hlTimer = setTimeout(syncPop, 80); });
document.addEventListener("mousedown", (e) => { if (!hlPop.contains(e.target)) hidePop(); });
// a plain click on a highlight offers to remove just that one
document.addEventListener("click", (e) => {
  const m = e.target.closest && e.target.closest("mark.hl");
  if (!m) return;
  const sel = getSelection();
  if (sel && !sel.isCollapsed) return;
  const block = hlBlock(m);
  const [a, b] = (m.dataset.r || "").split(",").map(Number);
  if (!block || !isFinite(a) || !isFinite(b)) return;
  e.stopPropagation();
  hlPending = { key: block.dataset.hlKey, start: a, end: b, fromClick: true };
  showPop(m.getBoundingClientRect(), false, true);
}, true);
addEventListener("scroll", hidePop, { passive: true });
addEventListener("resize", hidePop);

// ------------------------------------------------ one question
function render() {
  const q = questions[cur()], resp = response(cur());
  resetTimer();
  if (!resp.answered) toggleTimer();
  $("q-meta").textContent = `Question ${cur() + 1} of ${questions.length}`;
  const idBtn = $("q-id");
  clearTimeout(idBtn._flash);
  idBtn.textContent = idBtn.dataset.label = P.qid(q._quiz, q._i);
  hidePop();
  hlSources = {};

  const { rows, rest } = splitTable(q.question);
  paint($("q-stem"), rows.length ? rest : q.question, "q");
  const t = Array.isArray(q.table) && q.table.length ? q.table : rows;
  $("q-table").replaceChildren(...(t.length ? [table(t)] : []));
  $("q-img").replaceChildren(...(q.image ? [figure(q._quiz, q.image)] : []));

  const box = $("q-choices");
  box.replaceChildren();
  for (const L of Object.keys(q.answers || {})) {
    const b = document.createElement("button");
    b.className = "q-choice";
    b.dataset.letter = L;
    const tag = document.createElement("span"); tag.className = "q-letter"; tag.textContent = L;
    const txt = document.createElement("span"); txt.className = "q-choice-text";
    paint(txt, q.answers[L], `ans:${L}`);
    b.append(tag, txt);
    // dragging across the words highlights rather than picks, as does a double click
    b.addEventListener("click", (e) => {
      if (pressed(b)) { e.preventDefault(); return; }
      if (e.detail >= 2) return;
      const sel = getSelection();
      if (sel && !sel.isCollapsed && b.contains(sel.anchorNode)) return;
      pick(L);
    });
    b.addEventListener("contextmenu", (e) => {
      e.preventDefault();
      // a touch long-press strikes once, whichever of it and the menu comes first
      if (pressed(b)) return;
      if (b._press && !b._press.done) { clearTimeout(b._press.timer); b._press.done = Date.now(); }
      strike(L);
    });
    longPress(b, () => strike(L));
    box.append(b);
  }
  paintChoices();
  renderHistory();
  actions();
  updateScore();
  bar();
  renderNav();
  saveSession();
}

// Touch: holding a choice for 450 ms strikes it out (right-click with a
// mouse) without picking it; moving more than 10 px first is a scroll.
const PRESS_MS = 450;
// after a long press, until just after the finger lifts: the click that follows is not a pick
const pressed = (b) => { const p = b._press; return !!(p && p.done && (!p.up || Date.now() - p.up < 500)); };
function longPress(b, fn) {
  const end = () => {
    const p = b._press;
    if (!p) return;
    if (p.done) p.up = p.up || Date.now();
    else { clearTimeout(p.timer); b._press = null; }
  };
  b.addEventListener("pointerdown", (e) => {
    if (e.pointerType !== "touch") return;
    const p = { x: e.clientX, y: e.clientY, done: 0 };
    p.timer = setTimeout(() => {
      p.done = Date.now();
      if (b.classList.contains("locked")) return;
      fn();
      navigator.vibrate?.(10);
    }, PRESS_MS);
    b._press = p;
  });
  b.addEventListener("pointermove", (e) => {
    const p = b._press;
    if (p && !p.done && Math.hypot(e.clientX - p.x, e.clientY - p.y) > 10) end();
  });
  b.addEventListener("pointerup", end);
  b.addEventListener("pointercancel", end);
}

function strike(L) {
  const x = response(cur());
  if (x.answered) return;
  x.struck = x.struck.includes(L) ? x.struck.filter((s) => s !== L) : [...x.struck, L];
  bump(x);
  paintChoices(); actions(); saveSession();
}

function paintChoices() {
  const q = questions[cur()], x = response(cur());
  for (const b of document.querySelectorAll(".q-choice")) {
    const L = b.dataset.letter;
    b.classList.toggle("selected", !x.answered && x.selected === L);
    b.classList.toggle("struck", !x.answered && x.struck.includes(L));
    b.classList.toggle("right", x.answered && L === q.correct);
    b.classList.toggle("wrong", x.answered && L === x.selected && L !== q.correct);
    b.classList.toggle("locked", x.answered);
    b.setAttribute("aria-disabled", x.answered ? "true" : "false");
  }
  const exp = $("q-exp-items");
  exp.replaceChildren();
  if (x.answered) {
    for (const L of Object.keys(q.answers || {})) {
      const p = document.createElement("p");
      p.className = L === q.correct ? "right" : "";
      const tag = document.createElement("b"); tag.textContent = `${L}. `;
      const body = document.createElement("span");
      paint(body, q.explanations?.[L] || "", `exp:${L}`);
      p.append(tag, body);
      exp.append(p);
    }
    if (q.explanationImage) exp.append(figure(q._quiz, q.explanationImage));
    if (q.page) { const p = document.createElement("p"); p.className = "muted small"; p.textContent = `Slide ${q.page}`; exp.append(p); }
  }
  $("q-exp").classList.toggle("hidden", !x.answered);
}

// Every earlier try at this question. Whether each was right shows at once;
// what was picked waits until this try is answered.
function when(t) {
  const d = new Date(t);
  const opts = { month: "short", day: "numeric" };
  if (d.getFullYear() !== new Date().getFullYear()) opts.year = "numeric";
  return d.toLocaleDateString(undefined, opts);
}
function renderHistory() {
  const q = questions[cur()], open = response(cur()).answered;
  const el = $("q-hist");
  el.replaceChildren();
  for (const a of P.attempts(q._quiz, q._i)) {
    const chip = document.createElement("span");
    chip.className = `q-try ${a.ok ? "ok" : "bad"}`;
    chip.append(`${a.t ? when(a.t) : "Earlier"} `);
    if (open) { const b = document.createElement("b"); b.textContent = `${a.p} `; chip.append(b); }
    chip.append(a.ok ? "✓" : "✗");
    chip.title = `${a.t ? new Date(a.t).toLocaleString() : "Earlier"}, ${a.ok ? "correct" : "incorrect"}`;
    el.append(chip);
  }
}

// ------------------------------------------------ timer
// 1:30 per question from when it shows; click to pause or carry on. Past
// 0:00 it turns red and counts the time over.
const TIMER_MS = 90 * 1000;
const timer = { left: TIMER_MS, end: 0, tick: 0 };
function paintTimer() {
  const el = $("q-timer");
  const over = timer.left < 0;
  const s = over ? Math.floor(-timer.left / 1000) : Math.ceil(timer.left / 1000);
  el.textContent = `${over ? "-" : ""}${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
  el.classList.toggle("running", !!timer.tick);
  el.classList.toggle("done", timer.left <= 0);
  el.title = timer.tick ? "Pause the timer" : "Start the timer";
  el.setAttribute("aria-pressed", timer.tick ? "true" : "false");
}
function stopTimer() {
  if (timer.tick) timer.left = timer.end - Date.now();
  clearInterval(timer.tick);
  timer.tick = 0;
}
function resetTimer() { clearInterval(timer.tick); timer.tick = 0; timer.left = TIMER_MS; paintTimer(); }
function toggleTimer() {
  if (timer.tick) { stopTimer(); paintTimer(); return; }
  timer.end = Date.now() + timer.left;
  timer.tick = setInterval(() => { timer.left = timer.end - Date.now(); paintTimer(); }, 200);
  paintTimer();
}
$("q-timer").addEventListener("click", toggleTimer);

$("q-id").addEventListener("click", () => {
  const btn = $("q-id"), q = questions[cur()];
  navigator.clipboard?.writeText(P.qid(q._quiz, q._i)).then(() => {
    btn.textContent = "Copied";
    clearTimeout(btn._flash);
    btn._flash = setTimeout(() => { btn.textContent = btn.dataset.label; }, 1400);
  }, () => {});
});

// ------------------------------------------------ buttons and bar
function actions() {
  disarmReset();
  const x = response(cur()), last = current + 1 >= view.length;
  const submit = $("q-submit"), next = $("q-next"), flag = $("q-flag");
  submit.classList.toggle("hidden", x.answered);
  submit.disabled = x.answered || !x.selected;
  next.classList.toggle("primary", x.answered);
  next.textContent = x.answered ? (last ? "See Score" : "Next") : (last ? "Skip to Score" : "Skip");
  next.title = x.answered ? (last ? "See your score" : "Next question (Right Arrow)") : "Skip this question (S)";
  flag.classList.toggle("on", !!x.flagged);
  flag.textContent = x.flagged ? "Flagged" : "Flag";
  flag.setAttribute("aria-pressed", x.flagged ? "true" : "false");
  flag.title = x.flagged ? "Remove the flag (F)" : "Flag for review (F)";
  $("q-back").disabled = current === 0 && !resultsOpen;
  resetButtons();
}

function resetButtons() {
  $("q-reset").disabled = resultsOpen || !touched(responses[cur()]);
  $("q-reset-test").disabled = resultsOpen || !view.some((i) => touched(responses[i]));
}

function bar() {
  const done = tally().total;
  $("q-progress-label").textContent = `${done} of ${view.length} answered`;
  $("q-fill").style.width = `${view.length ? (done / view.length) * 100 : 0}%`;
}

function updateScore() {
  const { correct, total } = tally();
  $("q-score").textContent = total ? `${correct} of ${total} correct (${Math.round((correct / total) * 100)}%)` : "";
}

function pick(L) {
  const x = response(cur());
  if (x.answered) return;
  x.selected = L;
  x.struck = x.struck.filter((s) => s !== L);
  bump(x);
  paintChoices(); actions(); saveSession();
}

function submit() {
  const x = response(cur());
  if (!x.selected || x.answered) return;
  x.answered = true;
  x.skipped = false;
  bump(x);
  stopTimer(); paintTimer();
  const q = questions[cur()];
  P.addAttempt(q._quiz, q._i, x.selected, x.selected === q.correct, RUN_KEY);
  paintChoices(); renderHistory(); actions(); updateScore(); bar(); renderNav(); saveSession();
}

function nextQuestion() {
  if (resultsOpen) return;
  const x = response(cur());
  if (!x.answered && !x.skipped) bump(x).skipped = true;
  current++;
  if (current >= view.length) { saveSession(); showResults(); }
  else { render(); scrollTo({ top: 0, behavior: "smooth" }); }
}

function prevQuestion() {
  if (resultsOpen) { reviewAnswers(); return; }
  if (current === 0) return;
  current--;
  render();
  scrollTo({ top: 0, behavior: "smooth" });
}

function goTo(n) {
  if (n < 0 || n >= view.length) return;
  if (n === current && !resultsOpen) return;
  if (!resultsOpen) { const x = response(cur()); if (!x.answered && !x.skipped && n > current) bump(x).skipped = true; }
  leaveResults();
  current = n;
  render();
  scrollTo({ top: 0, behavior: "smooth" });
}

function toggleFlag() {
  if (resultsOpen || !questions.length) return;
  const x = response(cur());
  x.flagged = !x.flagged;
  actions(); renderNav(); saveMark(cur());
}

// Put a question, or the whole test, back to untouched. Flags, highlights
// and the history of tries stay.
function clearAnswer(i) {
  const r = responses[i];
  if (!r) return;
  r.selected = null; r.answered = false; r.skipped = false; r.struck = [];
  bump(r);
}
function resetQuestion() {
  if (resultsOpen || !touched(responses[cur()])) return;
  clearAnswer(cur());
  render();
}
let resetArmed = null;
function resetTest() {
  if (resultsOpen || !view.length) return;
  const b = $("q-reset-test");
  if (!resetArmed) {
    b.classList.add("armed");
    b.textContent = "Confirm Reset";
    resetArmed = setTimeout(disarmReset, 3000);
    return;
  }
  disarmReset();
  view.forEach(clearAnswer);
  replay();
}
function disarmReset() {
  if (resetArmed) { clearTimeout(resetArmed); resetArmed = null; }
  const b = $("q-reset-test");
  b.classList.remove("armed");
  b.textContent = "Reset Test";
}

// ------------------------------------------------ question navigator
function renderNav() {
  const grid = $("q-grid");
  grid.replaceChildren();
  view.forEach((qi, n) => {
    const q = questions[qi], r = responses[qi];
    const chip = document.createElement("button");
    chip.className = "q-chip";
    chip.textContent = qi + 1;
    const bits = [];
    if (r && r.answered) {
      const ok = r.selected === q.correct;
      chip.classList.add(ok ? "right" : "wrong");
      bits.push(ok ? "correct" : "incorrect");
    } else if (r && r.skipped) { chip.classList.add("skipped"); bits.push("skipped"); }
    else bits.push("not answered");
    if (r && r.flagged) { chip.classList.add("flagged"); bits.push("flagged"); }
    if (n === current && !resultsOpen) { chip.classList.add("current"); chip.setAttribute("aria-current", "true"); }
    chip.title = `Question ${qi + 1}, ${bits.join(", ")}`;
    chip.setAttribute("aria-label", chip.title);
    chip.addEventListener("click", () => goTo(n));
    grid.append(chip);
  });
  $("q-scope").classList.toggle("hidden", !redo);
  if (redo) {
    $("q-scope-redo").textContent = `Redo ${redo.length}`;
    $("q-scope-all").textContent = `All ${questions.length}`;
    $("q-scope-redo").classList.toggle("on", !showAll);
    $("q-scope-all").classList.toggle("on", showAll);
  }
  const { flagged, skipped } = tally();
  const counts = $("q-counts");
  counts.replaceChildren();
  for (const [v, l] of [[skipped, "skipped"], [flagged, "flagged"]]) {
    if (!v) continue;
    const d = document.createElement("div");
    const b = document.createElement("b"); b.textContent = v;
    d.append(b, ` ${l}`);
    counts.append(d);
  }
  counts.classList.toggle("hidden", !counts.childNodes.length);
  const chip = grid.querySelector(".current");
  if (chip) {
    if (grid.scrollHeight > grid.clientHeight) {
      const top = chip.offsetTop - grid.offsetTop;
      if (top < grid.scrollTop || top + chip.offsetHeight > grid.scrollTop + grid.clientHeight) grid.scrollTop = top - grid.clientHeight / 2;
    }
    if (grid.scrollWidth > grid.clientWidth) {
      const left = chip.offsetLeft - grid.offsetLeft;
      if (left < grid.scrollLeft || left + chip.offsetWidth > grid.scrollLeft + grid.clientWidth) grid.scrollLeft = left - grid.clientWidth / 2;
    }
  }
}

// Between the redo and the whole quiz; nothing is cleared either way.
function setScope(all) {
  if (!redo || showAll === all) return;
  const here = resultsOpen ? -1 : cur();
  showAll = all;
  syncView();
  if (resultsOpen) { current = view.length; showResults(); return; }
  current = Math.max(view.indexOf(here), 0);
  render();
}
$("q-scope-redo").addEventListener("click", () => setScope(false));
$("q-scope-all").addEventListener("click", () => setScope(true));

// ------------------------------------------------ results
function leaveResults() {
  resultsOpen = false;
  $("q-result").classList.add("hidden");
  $("q-card").classList.remove("hidden");
}

function showResults() {
  hidePop();
  stopTimer();
  $("q-card").classList.add("hidden");
  const { correct, wrong, total, flagged, skipped } = tally();
  const pct = total ? Math.round((correct / total) * 100) : 0;
  $("r-correct").textContent = correct;
  $("r-wrong").textContent = wrong;
  $("r-skipped").textContent = skipped;
  $("r-flagged").textContent = flagged;
  $("r-total").textContent = total;
  $("r-pct").textContent = `${pct}%`;
  $("r-flagged-btn").classList.toggle("hidden", !flagged);
  $("r-skipped-btn").classList.toggle("hidden", !skipped);
  $("r-redo").classList.toggle("hidden", !wrong);
  const arc = $("r-arc"), circ = 2 * Math.PI * 60;
  arc.style.transition = "none";
  arc.style.strokeDashoffset = circ;
  $("q-result").classList.remove("hidden");
  void arc.getBoundingClientRect();
  arc.style.transition = "stroke-dashoffset 0.8s ease";
  arc.style.strokeDashoffset = circ * (1 - pct / 100);
  resultsOpen = true;
  disarmReset();
  bar();
  actions();
  renderNav();
  saveSession();
  // a finished test goes to your other devices now
  for (const id of new Set(questions.map((q) => q._quiz))) S.pushNow(id);
}

function reviewAnswers() {
  leaveResults();
  current = view.length - 1;
  render();
}
function reviewFlagged() { const n = view.findIndex((i) => responses[i] && responses[i].flagged); if (n !== -1) goTo(n); }
function reviewSkipped() { const n = view.findIndex((i) => { const r = responses[i]; return r && r.skipped && !r.answered; }); if (n !== -1) goTo(n); }

// Back to the first question in view, off the results screen.
function replay() {
  current = 0;
  leaveResults();
  render();
  scrollTo({ top: 0, behavior: "smooth" });
}

// Play these questions again with their answers cleared: as a redo, with the
// rest of the quiz answered behind it, or as the whole test.
function restartWith(list, asRedo) {
  const sorted = list.slice().sort((a, b) => a - b);
  sorted.forEach(clearAnswer);
  redo = asRedo ? sorted : null;
  showAll = false;
  syncView();
  replay();
}

// Start Over puts this test aside as it stands and begins a new one, in the
// same order.
function restartQuiz() {
  saveSession();
  P.endTest(RUN_KEY);
  RUN_KEY = newTestId();
  startedAt = Date.now();
  restartWith(questions.map((_, i) => i), false);
}

// Redo Missed: every answered question goes up as a tile, the correct ones
// are filed away, and the missed ones stay behind as the redo. A click
// anywhere cuts it short.
function redoMissed() {
  const missed = view.filter((i) => { const r = responses[i]; return r && r.answered && r.selected !== questions[i].correct; });
  if (!missed.length) return;
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) { restartWith(missed, true); return; }
  const veil = document.createElement("div");
  veil.className = "q-veil";
  veil.innerHTML = '<div class="q-veil-head">Redo Missed</div><div class="q-veil-grid"></div><div class="q-bin"><div class="q-bin-fill"></div><div class="q-bin-label">0</div></div><div class="q-veil-note"></div>';
  document.body.append(veil);
  const grid = veil.querySelector(".q-veil-grid"), bin = veil.querySelector(".q-bin");
  const fill = veil.querySelector(".q-bin-fill"), label = veil.querySelector(".q-bin-label"), note = veil.querySelector(".q-veil-note");
  grid.style.setProperty("--chip", view.length > 150 ? "20px" : view.length > 80 ? "25px" : "30px");
  const cells = view.map((qi) => {
    const r = responses[qi];
    const ok = !!(r && r.answered && r.selected === questions[qi].correct);
    const el = document.createElement("span");
    el.className = `q-tile ${ok ? "ok" : "bad"}`;
    const i = document.createElement("i");
    i.textContent = qi + 1;
    i.style.animationDelay = `${(-Math.random() * 1.15).toFixed(2)}s`;
    el.append(i);
    grid.append(el);
    return { el, ok };
  });
  void veil.offsetHeight;
  veil.classList.add("on");
  const keep = cells.filter((c) => c.ok);
  const step = keep.length ? Math.min(30, 1500 / keep.length) : 0;
  const timers = [];
  let filed = 0, ended = false;
  function file(c) {
    const from = c.el.getBoundingClientRect(), to = bin.getBoundingClientRect();
    c.el.firstChild.classList.add("still");
    c.el.style.transform = `translate(${to.left + to.width / 2 - (from.left + from.width / 2)}px, ${to.top + 10 - (from.top + from.height / 2)}px) scale(0.2)`;
    c.el.style.opacity = "0";
    filed++;
    fill.style.height = `${Math.round((filed / keep.length) * 100)}%`;
    label.textContent = filed;
  }
  const after = (ms, fn) => timers.push(setTimeout(fn, ms));
  function finish() {
    if (ended) return;
    ended = true;
    timers.forEach(clearTimeout);
    for (const c of cells) { if (c.ok && c.el.style.opacity !== "0") file(c); c.el.firstChild.classList.add("still"); }
    if (keep.length) { fill.style.height = "100%"; label.textContent = keep.length; }
    note.textContent = `${missed.length} ${missed.length === 1 ? "question" : "questions"} to redo`;
    setTimeout(() => {
      veil.classList.remove("on");
      setTimeout(() => { veil.remove(); restartWith(missed, true); }, 450);
    }, 1100);
  }
  veil.addEventListener("click", finish);
  after(850, () => {
    keep.forEach((c, n) => after(n * step, () => file(c)));
    after(keep.length * step + 850, finish);
  });
}

// ------------------------------------------------ wiring
$("q-submit").addEventListener("click", submit);
$("q-next").addEventListener("click", nextQuestion);
$("q-back").addEventListener("click", prevQuestion);
$("q-flag").addEventListener("click", toggleFlag);
$("q-reset").addEventListener("click", resetQuestion);
$("q-reset-test").addEventListener("click", resetTest);
$("r-review").addEventListener("click", reviewAnswers);
$("r-flagged-btn").addEventListener("click", reviewFlagged);
$("r-skipped-btn").addEventListener("click", reviewSkipped);
$("r-redo").addEventListener("click", redoMissed);
$("r-again").addEventListener("click", restartQuiz);

$("q-share").addEventListener("click", async () => {
  const b = $("q-share");
  try {
    const { share_token } = await api(`/v1/quiz/${enc(quizId)}/share`, { method: "POST", user });
    await navigator.clipboard.writeText(`${location.origin}/quiz/?id=${enc(quizId)}&t=${enc(share_token)}`);
    b.textContent = "Link Copied";
    setTimeout(() => { b.textContent = "Copy Share Link"; }, 2000);
  } catch (e) { err(e.message || "The link could not be copied."); }
});

// A to E (or 1 to 9) picks, Enter or Space submits then moves on, arrows
// move, S skips, F flags (on the score, opens the first flagged), H
// highlights the selected text. Right-click (or a long press on touch) strikes a choice out.
document.addEventListener("keydown", (e) => {
  if (zoomed) { if (e.key === "Escape" || e.key === "Enter" || e.key === " ") { e.preventDefault(); unzoom(); } return; }
  if (e.key === "Escape") { hidePop(); return; }
  if (!questions.length || $("q-play").classList.contains("hidden") || document.querySelector(".q-veil")) return;
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  const t = e.target;
  if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
  const key = e.key, k = key.length === 1 ? key.toLowerCase() : key;
  if (key === "ArrowLeft") { e.preventDefault(); prevQuestion(); return; }
  if (key === "ArrowRight") { e.preventDefault(); nextQuestion(); return; }
  if (resultsOpen) { if (k === "f") { e.preventDefault(); reviewFlagged(); } return; }
  // with nothing selected H falls through, so an H choice still works
  if (k === "h") { const sel = selectionRange(); if (sel) { e.preventDefault(); applyHighlight(sel, overlaps(sel.key, sel.start, sel.end)); return; } }
  if (k === "f") { e.preventDefault(); toggleFlag(); return; }
  if (k === "s") { e.preventDefault(); nextQuestion(); return; }
  if (key === "Enter" || key === " ") {
    const a = document.activeElement;
    if (a && a.tagName === "BUTTON" && !a.classList.contains("q-choice")) return;
    e.preventDefault();
    const x = response(cur());
    if (x.answered) nextQuestion(); else if (x.selected) submit();
    return;
  }
  const letters = Object.keys(questions[cur()].answers || {});
  const idx = /^[1-9]$/.test(key) ? Number(key) - 1 : letters.indexOf(key.toUpperCase());
  if (idx >= 0 && idx < letters.length && key.length === 1) { e.preventDefault(); pick(letters[idx]); }
});

// last, so everything above is defined before the first callback
watchUser((u) => {
  user = u;
  S.setUser(u);
  if (!begun) { begun = true; load(); }
});
