// The quiz home, /quiz/ with no quiz: your quizzes by month with where you
// stand on each, practice sets (tick quizzes, then all, missed, unseen or
// flagged questions), questions by ID, quizzes shared with you and your
// practice history. Signed out it shows the practice kept in this browser.
import { watchUser, signIn, api } from "/assets/app.js";
import * as P from "/assets/practice.js";
import * as S from "/assets/sync.js";

const $ = (id) => document.getElementById(id);
const enc = encodeURIComponent;
let user = null, mine = [];
const err = (m) => { $("h-error").textContent = m; $("h-error").classList.remove("hidden"); };
const show = (id, on) => $(id).classList.toggle("hidden", !on);
const pct = (a, b) => (b ? `${Math.round((a / b) * 100)}%` : "");
const plural = (n, one, many) => `${n.toLocaleString()} ${n === 1 ? one : many}`;
function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text != null) e.textContent = text;
  return e;
}
function stat(parts) {
  const s = el("span", "h-stat");
  for (const p of parts.filter(Boolean)) s.append(el("span", "", p));
  return s;
}
// tried out of all, and how many were right on the last try
function standing(list) {
  let total = 0, seen = 0, right = 0, flagged = 0;
  for (const q of list) {
    const st = P.stats(q.id, q.n);
    total += q.n; seen += Math.min(st.seen, q.n); right += Math.min(st.right, st.seen, q.n); flagged += st.flagged;
  }
  return { total, seen, right, flagged };
}

$("h-sign-in").addEventListener("click", () => signIn().catch((e) => err(e.message)));

// ------------------------------------------------ your quizzes
function quizRow(q, tickable) {
  const a = el("a", "h-item");
  a.href = `/quiz/?${q.query}`;
  a.dataset.id = q.id;
  if (tickable) {
    const t = el("button", "h-tick");
    t.type = "button";
    t.setAttribute("role", "checkbox");
    t.setAttribute("aria-checked", "false");
    t.setAttribute("aria-label", `Add ${q.name} to a practice set`);
    a.append(t);
  }
  a.append(el("span", "h-item-name", `${q.name} (${q.n} Qs)`));
  const s = standing([q]);
  a.append(s.seen ? stat([`${s.seen}/${s.total}`, pct(s.right, s.seen)]) : stat([]));
  if (q.owner) {
    const b = el("button", "h-small", "Copy Link");
    b.type = "button";
    b.addEventListener("click", (e) => { e.preventDefault(); e.stopPropagation(); copyLink(q.id, b); });
    const d = el("button", "h-small", "Delete");
    d.type = "button";
    d.addEventListener("click", (e) => { e.preventDefault(); e.stopPropagation(); deleteQuiz(q, d); });
    a.append(b, d);
  }
  return a;
}

// first click arms the button, the second deletes
function armed(b, label) {
  if (b.classList.contains("armed")) return true;
  for (const x of document.querySelectorAll(".h-small.armed")) { x.classList.remove("armed"); x.textContent = x.dataset.label || "Delete"; }
  b.dataset.label = label;
  b.classList.add("armed");
  b.textContent = "Confirm Delete";
  return false;
}
async function deleteQuiz(q, b) {
  if (!armed(b, "Delete")) return;
  b.disabled = true;
  try {
    await api(`/v1/quiz/${enc(q.id)}`, { method: "DELETE", user });
    mine = mine.filter((x) => x.id !== q.id);
    P.forgetQuiz(q.id);
    paintAll();
  } catch (e) { err(e.message || "The quiz could not be deleted."); b.disabled = false; }
}

const monthOf = (t) => new Date(t).toLocaleDateString(undefined, { month: "long", year: "numeric" });
const groupOf = (q) => q.folder || monthOf(q.created_at);
const playSet = (ids) => (ids.length === 1 ? `/quiz/?id=${enc(ids[0])}` : `/quiz/?set=${ids.map(enc).join(",")}`);

// Groups made here that have no quizzes yet; once a quiz is moved in, the
// server keeps the name with the quiz.
const EMPTY = "po-empty-groups";
const emptyGroups = () => { try { return JSON.parse(localStorage.getItem(EMPTY)) || []; } catch { return []; } };
const setEmptyGroups = (a) => { try { localStorage.setItem(EMPTY, JSON.stringify([...new Set(a)])); } catch {} };

function groups() {
  const map = new Map();
  for (const name of emptyGroups()) map.set(name, []);
  for (const q of mine) {
    const k = groupOf(q);
    if (!map.has(k)) map.set(k, []);
    map.get(k).push(q);
  }
  // named groups that now hold quizzes no longer need remembering here
  const still = emptyGroups().filter((n) => !map.get(n).length);
  if (still.length !== emptyGroups().length) setEmptyGroups(still);
  return map;
}

async function moveTo(ids, folder) {
  await api("/v1/quizzes/move", { method: "POST", body: { ids, folder }, user });
  const set = new Set(ids);
  for (const q of mine) if (set.has(q.id)) q.folder = folder || null;
  paintAll();
}

function nameForm(start, onSave, onCancel) {
  const f = el("form", "h-name-form");
  const i = el("input");
  i.type = "text"; i.maxLength = 60; i.value = start; i.setAttribute("aria-label", "Group name");
  const ok = el("button", "h-small", "Save"); ok.type = "submit";
  const no = el("button", "h-small", "Cancel"); no.type = "button";
  f.append(i, ok, no);
  f.addEventListener("submit", (e) => { e.preventDefault(); const v = i.value.trim(); if (v) onSave(v); });
  no.addEventListener("click", onCancel);
  setTimeout(() => { i.focus(); i.select(); });
  return f;
}

function paintMine() {
  const list = $("h-mine-list");
  list.replaceChildren();
  for (const [name, items] of groups()) {
    const g = el("div", "h-group");
    const head = el("div", "h-group-head");
    const t = el("button", "h-tick");
    t.type = "button";
    t.setAttribute("role", "checkbox");
    t.setAttribute("aria-checked", "false");
    t.setAttribute("aria-label", `Add all of ${name} to a practice set`);
    t.disabled = !items.length;
    const title = el("div", "h-group-title");
    const s = standing(items);
    const count = el("span", "h-group-count");
    for (const c of [items.length ? plural(items.length, "quiz", "quizzes") : "", items.length ? `${s.total} Qs` : "", s.seen ? pct(s.right, s.seen) : ""].filter(Boolean)) count.append(el("span", "", c));
    title.append(el("span", "h-group-name", name), count);
    const rename = el("button", "h-small", "Rename");
    rename.type = "button";
    rename.addEventListener("click", () => {
      const back = () => head.replaceChildren(t, title, ...tools);
      head.replaceChildren(t, nameForm(name, async (v) => {
        if (v === name) return back();
        try {
          if (items.length) await moveTo(items.map((q) => q.id), v);
          else { setEmptyGroups(emptyGroups().map((n) => (n === name ? v : n))); paintAll(); }
        } catch (e) { err(e.message || "The group could not be renamed."); back(); }
      }, back));
    });
    let tools;
    if (items.length) {
      const shuffle = el("button", "h-small", "Shuffle");
      shuffle.type = "button";
      shuffle.title = `Shuffle every question in ${name}`;
      shuffle.addEventListener("click", () => { location.href = playSet(items.map((q) => q.id)); });
      tools = [rename, shuffle];
    } else {
      const del = el("button", "h-small", "Delete");
      del.type = "button";
      del.addEventListener("click", () => { if (armed(del, "Delete")) { setEmptyGroups(emptyGroups().filter((n) => n !== name)); paintAll(); } });
      tools = [rename, del];
    }
    head.append(t, title, ...tools);
    const rows = el("div", "h-group-items");
    for (const q of items) rows.append(quizRow(q, true));
    if (!items.length) rows.append(el("div", "h-empty", "No quizzes in this group."));
    g.append(head, rows);
    list.append(g);
  }
  if (!list.children.length) list.append(el("div", "h-empty", "No quizzes yet."));
  $("h-shuffle-all").disabled = mine.length < 1;
  show("h-ids", mine.length > 0);
  paintPick();
}

// a new, empty group from the button at the top of Your Quizzes
const newOpen = (on) => {
  show("h-new-form", on);
  $("h-new-group").disabled = on;
  $("h-new-name").value = "";
  $("h-new-go").disabled = true;
  if (on) $("h-new-name").focus();
};
$("h-new-group").addEventListener("click", () => newOpen(true));
$("h-new-cancel").addEventListener("click", () => newOpen(false));
$("h-new-name").addEventListener("input", () => { $("h-new-go").disabled = !$("h-new-name").value.trim(); });
$("h-new-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const v = $("h-new-name").value.trim();
  if (!v) return;
  if (!groups().has(v)) setEmptyGroups([v, ...emptyGroups()]);
  newOpen(false);
  paintAll();
});
$("h-shuffle-all").addEventListener("click", () => { if (mine.length) location.href = playSet(mine.map((q) => q.id)); });

// ------------------------------------------------ shared with you
// Quizzes opened from someone's link, from the practice kept here (and, signed
// in, on your account).
function paintShared() {
  const own = new Set(mine.map((q) => q.id));
  const shared = P.quizzesPlayed()
    .filter((z) => z.q && !own.has(z.id) && /(^|&)t=/.test(z.q) && z.n)
    .map((z) => ({ id: z.id, name: z.name || "Quiz", n: z.n, query: z.q }));
  const list = $("h-shared-list");
  list.replaceChildren(...shared.map((q) => quizRow(q, false)));
  $("h-shared-count").textContent = shared.length ? plural(shared.length, "quiz", "quizzes") : "";
  show("h-shared", shared.length > 0);
}

// ------------------------------------------------ practice history
function testRow(href, title, sub, how, del) {
  const a = el("a", "h-item");
  a.href = href;
  const name = el("span", "h-item-name", title || "Quiz");
  if (sub) { name.append(" "); name.append(el("span", "h-item-sub", sub)); }
  a.append(name, stat(how));
  if (del) {
    const b = el("button", "h-small", "Delete");
    b.type = "button";
    b.addEventListener("click", (e) => {
      e.preventDefault(); e.stopPropagation();
      if (!b.classList.contains("armed")) {
        for (const x of document.querySelectorAll("#h-history-list .armed")) { x.classList.remove("armed"); x.textContent = "Delete"; }
        b.classList.add("armed");
        b.textContent = "Confirm Delete";
        return;
      }
      P.deleteTest(del);
      paintAll();
    });
    a.append(b);
  }
  return a;
}
const day = (t) => new Date(t).toLocaleDateString(undefined, { month: "short", day: "numeric" });
function paintHistory() {
  const tests = P.listTests();
  const line = (t) => testRow(`/quiz/?${t.q}&test=${enc(t.id)}`, t.where, t.label,
    [`${t.right + t.wrong}/${t.n}`, t.right + t.wrong ? pct(t.right, t.right + t.wrong) : "", t.updated ? day(t.updated) : ""], t.id);
  const open = tests.filter((t) => !t.done && !t.ended).map(line);
  const past = tests.filter((t) => t.done || t.ended).map(line);
  const weak = P.quizzesPlayed().filter((z) => z.q && z.seen >= 5 && z.right < z.seen)
    .sort((a, b) => a.right / a.seen - b.right / b.seen).slice(0, 5)
    .map((z) => testRow(`/quiz/?${z.q}&only=missed`, z.name, "", [`${z.seen - z.right} missed`, pct(z.right, z.seen)]));
  const list = $("h-history-list");
  list.replaceChildren();
  for (const [name, rows] of [["In Progress", open], ["Weakest Quizzes", weak], ["Past Tests", past]]) {
    if (!rows.length) continue;
    list.append(el("div", "h-sub-head", name), ...rows);
  }
  $("h-history-count").textContent = tests.length ? plural(tests.length, "test", "tests") : "";
  const any = open.length + past.length + weak.length > 0;
  $("h-history-btn").disabled = !any;
  show("h-history", historyOpen);
}
// History opens from its button at the top; closed until asked for
let historyOpen = false;
function setHistory(open) {
  historyOpen = open;
  $("h-history-btn").setAttribute("aria-expanded", open ? "true" : "false");
  $("h-history-btn").classList.toggle("on", open);
  show("h-history", open);
  if (open) $("h-history").scrollIntoView({ behavior: "smooth", block: "nearest" });
}
$("h-history-btn").addEventListener("click", () => setHistory(!historyOpen));
$("h-history-close").addEventListener("click", () => setHistory(false));

// ------------------------------------------------ practice sets
let pickOnly = "all";
const ONLY = { all: "All", missed: "Missed", unseen: "Unseen", flagged: "Flagged" };
const pickedRows = () => [...document.querySelectorAll("#h-mine-list .h-item.picked")];
function setPicked(row, on) {
  row.classList.toggle("picked", on);
  row.querySelector(".h-tick").setAttribute("aria-checked", on ? "true" : "false");
}
$("h-mine-list").addEventListener("click", (e) => {
  const tick = e.target.closest(".h-tick");
  if (!tick) return;
  e.preventDefault();
  const row = tick.closest(".h-item");
  if (row) setPicked(row, !row.classList.contains("picked"));
  else {
    const rows = [...tick.closest(".h-group").querySelectorAll(".h-item")];
    const all = rows.every((r) => r.classList.contains("picked"));
    rows.forEach((r) => setPicked(r, !all));
  }
  paintPick();
});
function paintPick() {
  const rows = pickedRows();
  $("h-pickbar").classList.toggle("open", rows.length > 0);
  document.body.classList.toggle("picking", rows.length > 0);
  for (const g of document.querySelectorAll("#h-mine-list .h-group")) {
    const all = [...g.querySelectorAll(".h-item")];
    const on = all.length > 0 && all.every((r) => r.classList.contains("picked"));
    const t = g.querySelector(".h-group-head .h-tick");
    t.classList.toggle("on", on);
    t.setAttribute("aria-checked", on ? "true" : "false");
  }
  if (!rows.length) { pickOnly = "all"; show("h-move-form", false); show("h-pick-move", true); return; }
  const ids = new Set(rows.map((r) => r.dataset.id));
  const s = standing(mine.filter((q) => ids.has(q.id)));
  const counts = { all: s.total, missed: s.seen - s.right, unseen: s.total - s.seen, flagged: s.flagged };
  if (!counts[pickOnly]) pickOnly = "all";
  $("h-pick-count").textContent = plural(rows.length, "Quiz", "Quizzes");
  for (const b of document.querySelectorAll("#h-pick-only button")) {
    const k = b.dataset.only;
    b.textContent = `${ONLY[k]} ${counts[k]}`;
    b.disabled = !counts[k];
    b.classList.toggle("on", k === pickOnly && !!counts[k]);
  }
  $("h-pick-go").disabled = !counts[pickOnly];
  const sel = $("h-pick-move");
  sel.replaceChildren(new Option("Move To", ""), ...[...groups().keys()].map((n) => new Option(n, n)), new Option("New Group", "\u0000new"));
  sel.value = "";
}
$("h-pick-move").addEventListener("change", async () => {
  const v = $("h-pick-move").value;
  if (!v) return;
  if (v === "\u0000new") {
    show("h-move-form", true);
    show("h-pick-move", false);
    $("h-move-name").value = "";
    $("h-move-go").disabled = true;
    $("h-move-name").focus();
    return;
  }
  try { await moveTo(pickedRows().map((r) => r.dataset.id), v); } catch (e) { err(e.message || "The quizzes could not be moved."); }
});
$("h-move-name").addEventListener("input", () => { $("h-move-go").disabled = !$("h-move-name").value.trim(); });
$("h-move-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const v = $("h-move-name").value.trim();
  if (!v) return;
  show("h-move-form", false);
  show("h-pick-move", true);
  try { await moveTo(pickedRows().map((r) => r.dataset.id), v); } catch (e) { err(e.message || "The quizzes could not be moved."); }
});
$("h-pick-only").addEventListener("click", (e) => {
  const b = e.target.closest("button");
  if (!b || b.disabled) return;
  pickOnly = b.dataset.only;
  paintPick();
});
$("h-pick-clear").addEventListener("click", () => { pickedRows().forEach((r) => setPicked(r, false)); paintPick(); });
$("h-pick-go").addEventListener("click", () => {
  const ids = pickedRows().map((r) => r.dataset.id);
  if (ids.length) location.href = playSet(ids) + (pickOnly !== "all" ? `&only=${pickOnly}` : "");
});

// ------------------------------------------------ questions by ID
const typedIds = () => [...new Set($("h-ids-input").value.toLowerCase().split(/[^a-z0-9]+/).filter(Boolean))];
$("h-ids-input").addEventListener("input", () => { $("h-ids-go").disabled = !typedIds().length; });
$("h-ids").addEventListener("submit", (e) => {
  e.preventDefault();
  const ids = typedIds();
  if (ids.length) location.href = `/quiz/?q=${ids.join(",")}`;
});

async function copyLink(id, b) {
  b.disabled = true;
  try {
    const { share_token } = await api(`/v1/quiz/${enc(id)}/share`, { method: "POST", user });
    await navigator.clipboard.writeText(`${location.origin}/quiz/?id=${enc(id)}&t=${enc(share_token)}`);
    b.textContent = "Copied";
    setTimeout(() => { b.textContent = "Copy Link"; }, 2000);
  } catch (e) { err(e.message || "The link could not be copied."); }
  b.disabled = false;
}

// ------------------------------------------------ wiring
function paintAll() {
  // ticks survive a repaint
  const picked = new Set(pickedRows().map((r) => r.dataset.id));
  if (user) paintMine();
  for (const r of document.querySelectorAll("#h-mine-list .h-item")) if (picked.has(r.dataset.id)) setPicked(r, true);
  paintPick();
  paintShared();
  paintHistory();
}

watchUser(async (u) => {
  user = u;
  S.setUser(u);
  show("h-out", !u);
  show("h-mine", !!u);
  $("h-who").textContent = u ? u.email || "" : "";
  if (!u) { mine = []; $("h-pickbar").classList.remove("open"); paintAll(); return; }
  paintAll();
  // your quizzes, and your practice from every device; whichever comes first shows first
  const listed = api("/v1/quizzes", { user }).then(({ quizzes = [] }) => {
    mine = quizzes.map((q) => ({ id: q.id, name: q.lecture || "Untitled PDF", n: q.n_questions || 0, created_at: q.created_at, folder: q.folder || null, query: `id=${enc(q.id)}`, owner: true }));
    paintAll();
  }, (e) => err(e.message));
  await Promise.all([listed, S.pullAll().then(paintAll)]);
});
