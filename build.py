"""Write every page of the site from one template.

  python3 build.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ANKIWEB = "https://ankiweb.net/shared/info/783821131"
GITHUB = "https://github.com/pdf-occlusion/anki-pdf-occlusion"
HELP = "mailto:pdf-occlusion-support@googlegroups.com"

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="pdf occlusion">
<meta property="og:description" content="An Anki add-on that turns lecture PDFs into flashcards and practice quizzes.">
<meta property="og:image" content="https://pdf-occlusion.github.io/assets/og.png">
<meta property="og:url" content="https://pdf-occlusion.github.io/">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Klee+One:wght@400;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css?v=CSSVER">
</head>
<body>
<main>
"""

NAV = [("pricing", "/pricing/", "pricing"), ("quizzes", "/quiz/", "quiz"), ("account", "/account/", "account")]

# Page views and clicks, for the owner's statistics: a random id kept in this
# browser, the page's path and where the visitor came from. No query string,
# so codes in links (/link/?code=) are never sent.
BEACON = """<script>
(function () {
  try {
    var k = "po-anon", id = localStorage.getItem(k);
    if (!id) { id = crypto.randomUUID ? crypto.randomUUID() : String(Math.random()).slice(2) + Date.now(); localStorage.setItem(k, id); }
    var api = "https://pdf-occlusion-api.pdf-occlusion.workers.dev/v1/events";
    var send = function (name, props) {
      try { navigator.sendBeacon(api, new Blob([JSON.stringify({ anon: id, events: [{ name: name, at: Date.now(), props: props }] })], { type: "text/plain" })); } catch (e) {}
    };
    window.poTrack = send;
    var ref = document.referrer ? new URL(document.referrer).hostname : "";
    var utm = new URLSearchParams(location.search).get("utm_source") || "";
    send("page_view", { path: location.pathname, ref: ref === location.hostname ? "" : ref, utm: utm.slice(0, 40) });
    document.addEventListener("click", function (e) {
      var a = e.target.closest && e.target.closest("a, button");
      if (a) send("click", { window: "web", page: location.pathname, button: (a.textContent || a.getAttribute("aria-label") || "").trim().slice(0, 60), href: (a.getAttribute("href") || "").split("?")[0] });
    }, true);
  } catch (e) {}
})();
</script>"""

FOOT = f"""</main>
<footer>
  <nav aria-label="Footer">
    <a href="/privacy/">privacy</a>
    <a href="/terms/">terms</a>
    <a href="{HELP}">help</a>
  </nav>
</footer>
{{script}}
</body>
</html>
"""


def top(name, current=None, small=True):
    links = "\n    ".join(
        f'<a href="{href}"{" aria-current=\"page\"" if key and key == current else ""}>{label}</a>'
        for label, href, key in NAV)
    back = "" if not small else '<a class="back" href="/" onclick="if (document.referrer.startsWith(location.origin)) { history.back(); return false; }">&larr; back</a>\n'
    return back + f"""<div class="top{' small' if small else ''}">
  <a href="/" aria-label="pdf occlusion home"><img class="mark" src="/assets/logo.svg" alt=""></a>
  <h1>{name}</h1>
  <nav class="links" aria-label="Main">
    {links}
  </nav>
</div>
"""


def page(path, title, desc, body, script=""):
    body = body.replace("{G_ICON}", G_ICON)
    import hashlib
    css_v = hashlib.sha1(open(os.path.join(HERE, "assets/site.css"), "rb").read()).hexdigest()[:8]
    html = HEAD.format(title=title, desc=desc).replace("CSSVER", css_v) + body + FOOT.format(script=(script + "\n" + BEACON).strip())
    out = os.path.join(HERE, path)
    os.makedirs(os.path.dirname(out) or HERE, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", path)


G_ICON = ('<svg class="g-icon" viewBox="0 0 18 18" aria-hidden="true"><path fill="#4285F4" d="M17.64 9.2c0-.64-.06-1.25-.16-1.84H9v3.48h4.84a4.14 4.14 0 0 1-1.8 2.72v2.26h2.92c1.7-1.57 2.68-3.88 2.68-6.62z"/>'
          '<path fill="#34A853" d="M9 18c2.43 0 4.47-.8 5.96-2.18l-2.92-2.26c-.8.54-1.84.86-3.04.86-2.34 0-4.32-1.58-5.03-3.7H.96v2.33A9 9 0 0 0 9 18z"/>'
          '<path fill="#FBBC05" d="M3.97 10.72A5.4 5.4 0 0 1 3.68 9c0-.6.1-1.18.29-1.72V4.95H.96A9 9 0 0 0 0 9c0 1.45.35 2.83.96 4.05l3.01-2.33z"/>'
          '<path fill="#EA4335" d="M9 3.58c1.32 0 2.5.45 3.44 1.35l2.58-2.58A9 9 0 0 0 .96 4.95l3.01 2.33C4.68 5.16 6.66 3.58 9 3.58z"/></svg>')

# ------------------------------------------------------------------ home
PRICES = f"""<div class="panel prices">
  <div><div class="amount">free</div><div class="what">your first 50 pages and 2 quizzes</div></div>
  <div><div class="amount">$14.99</div><div class="what">a month for 1,000 pages and 20 quizzes</div></div>
  <div><div class="amount">$9.99</div><div class="what">400 pages, no expiry</div></div>
</div>"""

page("index.html", "pdf occlusion",
     "Auto turns a PDF into image occlusion boxes, text cards or a practice quiz, inside Anki. Your first 50 pages and 2 quizzes are free.",
     body=top("pdf occlusion", small=False) + f"""
<div class="badges">
  <span class="badge"><span class="badge-k">add-on code</span><span class="badge-v">783821131</span></span>
  <span class="badge"><span class="badge-k">anki</span><span class="badge-v">23.10+</span></span>
  <span class="badge"><span class="badge-k">license</span><span class="badge-v">MIT</span></span>
</div>

<p class="lede">press auto and choose what your pdf becomes: boxes over its labels, cards from its text, or a quiz to take on any device.</p>

<div style="margin-top:26px">{PRICES}</div>

<div class="panel demo">
  <img src="/assets/demo.gif" width="840" height="585" alt="PDF Occlusion open in Anki with boxes placed over the labels of an anatomy diagram">
</div>

<section class="center">
  <h2>three things from one pdf</h2>
  <div class="panel outputs">
    <div><div class="name">boxes</div><div class="what">every label and key term covered on the page itself</div></div>
    <div><div class="name">cards</div><div class="what">one fact per card, from what each page says</div></div>
    <div><div class="name">quiz</div><div class="what">board-style questions with a reason for every answer</div></div>
  </div>
</section>

<section class="center">
  <h2>anything in a pdf</h2>
  <ul class="chips">
    <li>lecture slides</li>
    <li>anatomy atlases</li>
    <li>histology</li>
    <li>textbook figures</li>
    <li>tables</li>
    <li>vocabulary lists</li>
    <li>character charts</li>
    <li>maps</li>
    <li>flowcharts</li>
    <li>formula sheets</li>
    <li>board prep</li>
  </ul>
</section>

<section class="center">
  <h2>set it once</h2>
  <ul class="chips">
    <li>all labels or key ones</li>
    <li>key phrases or whole lines</li>
    <li>numbers and doses</li>
    <li>bold or colored text</li>
    <li>tables by cell or row</li>
    <li>pathways step by step</li>
    <li>pages to skip</li>
    <li>your own rules</li>
  </ul>
</section>
""")

# ------------------------------------------------------------------ pricing
page("pricing/index.html", "pricing",
     "Your first 50 pages and 2 quizzes are free. Then $14.99 a month for 1,000 pages and 20 quizzes, $149.90 a year, or 400 pages for $9.99.",
     body=top("pricing", "pricing") + f"""
<p class="lede">auto is counted in pages and quizzes. the add-on itself is free.</p>

<div class="panel" style="margin-top:30px">
  <ul class="plain price-list">
    <li>
      <div><div class="name">to start</div><div class="what">50 pages and 2 quizzes</div></div>
      <div class="amount">free</div>
    </li>
    <li>
      <div><div class="name">monthly</div><div class="what">1,000 pages and 20 quizzes a month</div></div>
      <div class="row" style="margin:0"><span class="amount">$14.99</span><button class="primary" data-buy="monthly">subscribe</button></div>
    </li>
    <li>
      <div><div class="name">yearly</div><div class="what">1,000 pages and 20 quizzes a month, two months cheaper</div></div>
      <div class="row" style="margin:0"><span class="amount">$149.90</span><button data-buy="yearly">subscribe</button></div>
    </li>
    <li>
      <div><div class="name">400 pages</div><div class="what">no expiry</div></div>
      <div class="row" style="margin:0"><span class="amount">$9.99</span><button data-buy="pack">buy</button></div>
    </li>
  </ul>
</div>
<p class="error hidden center" id="buy-error" role="alert"></p>

<section>
  <ul class="dots">
    <li>Boxes and cards use 1 page per slide. A quiz uses 1 quiz, however long the lecture.</li>
    <li>A plan's pages and quizzes reset each month. Extra pages are used once its pages run out.</li>
    <li>Cancel any time from your account. The plan runs to the end of what you paid for.</li>
    <li>Pages are counted as they are done, so a run you stop early only uses what was finished. A quiz is counted once its questions are ready.</li>
    <li>Boxing by hand is always free.</li>
  </ul>
</section>
""", script="""<script type="module">
import { watchUser, signIn, api } from "/assets/app.js";
let user = null;
watchUser((u) => { user = u; });
const err = document.getElementById("buy-error");
for (const b of document.querySelectorAll("[data-buy]")) {
  b.addEventListener("click", async () => {
    err.classList.add("hidden");
    b.disabled = true;
    try {
      if (!user) await signIn();
      if (!user) { b.disabled = false; return; }
      const { url } = await api("/v1/checkout", { method: "POST", body: { product: b.dataset.buy }, user });
      location.href = url;
    } catch (e) {
      err.textContent = e.message || "Checkout could not start.";
      err.classList.remove("hidden");
      b.disabled = false;
    }
  });
}
</script>""")

# ------------------------------------------------------------------ account
page("account/index.html", "account", "Your pages, quizzes, plan and linked Anki installs.",
     body=top("account", "account") + f"""
<div id="signed-out" class="hidden">
  <p class="lede">sign in to see your plan and link the add-on.</p>
  <div class="row center" style="margin-top:22px"><button id="sign-in">{{G_ICON}}sign in with google</button></div>
</div>

<div id="signed-in" class="hidden">
  <p class="lede" id="who"></p>
  <p class="note center hidden" id="paid"></p>

  <div class="panel" style="margin-top:26px">
    <div class="balances">
      <div><div class="left" id="left">0</div><div class="muted" id="left-note">pages left</div></div>
      <div><div class="left" id="qleft">0</div><div class="muted" id="qleft-note">quizzes left</div></div>
    </div>
    <dl class="kv">
      <dt>plan</dt><dd id="plan">none</dd>
      <dt>pages this month</dt><dd id="month"></dd>
      <dt>quizzes this month</dt><dd id="qmonth"></dd>
      <dt>extra pages</dt><dd id="packs"></dd>
    </dl>
    <div class="row">
      <a class="btn primary" href="/pricing/" id="upgrade">see pricing</a>
      <button id="pack">buy 400 pages</button>
      <button class="hidden" id="billing">manage billing</button>
    </div>
  </div>

  <div class="panel">
    <h3>anki installs</h3>
    <ul class="plain list" id="devices"></ul>
    <p class="muted small hidden" id="no-devices">none linked yet</p>
    <div class="row"><button class="hidden" id="unlink">sign out of all installs</button></div>
  </div>

  <div class="panel">
    <h3>quizzes</h3>
    <ul class="plain list" id="quizzes"></ul>
    <p class="muted small hidden" id="no-quizzes">nothing yet</p>
    <div class="row hidden" id="all-quizzes"><a class="btn" href="/quiz/">all quizzes</a></div>
  </div>

  <div class="panel">
    <h3>history</h3>
    <ul class="plain list" id="jobs"></ul>
    <p class="muted small hidden" id="no-jobs">nothing yet</p>
  </div>

  <div class="row center" style="margin-top:22px">
    <button id="sign-out">sign out</button>
    <button id="delete">delete account</button>
    <button class="hidden" id="delete-yes">delete my account and history</button>
    <button class="hidden" id="delete-no">keep it</button>
  </div>
</div>
<p class="error hidden center" id="acct-error" role="alert"></p>
""", script="""<script type="module">
import { watchUser, signIn, signOut, deleteSignIn, api, when } from "/assets/app.js";
const $ = (id) => document.getElementById(id);
let user = null;
const err = (m) => { $("acct-error").textContent = m; $("acct-error").classList.remove("hidden"); };
$("sign-in").addEventListener("click", () => signIn().catch((e) => err(e.message)));
$("sign-out").addEventListener("click", () => signOut());
const paid = new URLSearchParams(location.search).get("paid");
if (paid) {
  $("paid").textContent = paid === "pack" ? "thanks, 400 pages were added." : "thanks, your plan is active.";
  $("paid").classList.remove("hidden");
}
async function load() {
  const me = await api("/v1/me", { user });
  $("who").textContent = me.email || "";
  $("left").textContent = me.pages_left.toLocaleString();
  $("left-note").textContent = me.pages_left === 1 ? "page left" : "pages left";
  $("qleft").textContent = me.quiz_left.toLocaleString();
  $("qleft-note").textContent = me.quiz_left === 1 ? "quiz left" : "quizzes left";
  $("plan").textContent = me.plan === "yearly" ? "yearly" : me.plan === "monthly" ? "monthly" : me.free_left || me.quiz_free_left ? "free to start" : "none";
  $("month").textContent = me.plan ? `${me.plan_used} of ${me.plan_allowance} used` : "no plan";
  $("qmonth").textContent = me.plan ? `${me.quiz_plan_used} of ${me.quiz_plan_allowance} used` : "no plan";
  $("packs").textContent = me.pack_pages ? `${me.pack_pages} left` : "none";
  $("upgrade").classList.toggle("hidden", !!me.plan);
  $("billing").classList.toggle("hidden", !me.plan && !me.pack_pages && !paid);
  const dev = $("devices"); dev.replaceChildren();
  for (const d of me.devices) {
    const li = document.createElement("li");
    li.innerHTML = "<span></span><span></span>";
    li.children[0].textContent = d.label || "Anki";
    li.children[1].textContent = d.last_used ? `used ${when(d.last_used)}` : `linked ${when(d.created_at)}`;
    dev.append(li);
  }
  $("no-devices").classList.toggle("hidden", me.devices.length > 0);
  $("unlink").classList.toggle("hidden", me.devices.length === 0);
  const jobs = $("jobs"); jobs.replaceChildren();
  for (const j of me.jobs) {
    const li = document.createElement("li");
    li.innerHTML = "<span></span><span></span>";
    li.children[0].textContent = j.lecture || "Untitled pdf";
    li.children[1].textContent = `${j.slides_total} pages, ${when(j.created_at)}`;
    jobs.append(li);
  }
  $("no-jobs").classList.toggle("hidden", me.jobs.length > 0);
  const { quizzes } = await api("/v1/quizzes", { user });
  const ql = $("quizzes"); ql.replaceChildren();
  for (const q of quizzes.slice(0, 5)) {
    const li = document.createElement("li");
    li.innerHTML = "<a></a><span></span>";
    li.children[0].href = `/quiz/?id=${encodeURIComponent(q.id)}`;
    li.children[0].textContent = q.lecture || "Untitled pdf";
    li.children[1].textContent = `${q.n_questions} questions, ${when(q.created_at)}`;
    ql.append(li);
  }
  $("no-quizzes").classList.toggle("hidden", quizzes.length > 0);
  $("all-quizzes").classList.toggle("hidden", quizzes.length <= 5);
}
watchUser(async (u) => {
  user = u;
  $("signed-out").classList.toggle("hidden", !!u);
  $("signed-in").classList.toggle("hidden", !u);
  if (u) load().catch((e) => err(e.message));
});
async function go(path, body) {
  try { const { url } = await api(path, { method: "POST", body, user }); location.href = url; }
  catch (e) { err(e.message); }
}
$("pack").addEventListener("click", () => go("/v1/checkout", { product: "pack" }));
$("billing").addEventListener("click", () => go("/v1/portal"));
const asking = (on) => {
  $("delete").classList.toggle("hidden", on);
  $("delete-yes").classList.toggle("hidden", !on);
  $("delete-no").classList.toggle("hidden", !on);
};
$("delete").addEventListener("click", () => asking(true));
$("delete-no").addEventListener("click", () => asking(false));
$("delete-yes").addEventListener("click", async () => {
  try { await api("/v1/me/delete", { method: "POST", user }); asking(false); await deleteSignIn(); }
  catch (e) { err(e.message); }
});
$("unlink").addEventListener("click", async () => {
  try { await api("/v1/devices/sign-out", { method: "POST", user }); await load(); } catch (e) { err(e.message); }
});
</script>""")

# ------------------------------------------------------------------ quiz
# /quiz/ lists the signed-in account's quizzes; /quiz/?id=...(&t=share token)
# plays one, signed in or not.
page("quiz/index.html", "quizzes", "Practice questions made from your lecture PDFs.",
     body=top("quizzes", "quiz") + f"""
<div id="q-loading" class="muted center" style="margin-top:22px">loading</div>

<div id="q-out" class="hidden">
  <p class="lede">sign in to see your quizzes.</p>
  <div class="row center" style="margin-top:22px"><button id="sign-in">{{G_ICON}}sign in with google</button></div>
</div>

<div id="q-list" class="hidden">
  <p class="lede" id="q-left"></p>
  <div class="panel" style="margin-top:26px">
    <ul class="plain list" id="quizzes"></ul>
    <p class="muted small hidden" id="no-quizzes">nothing yet</p>
  </div>
</div>

<div id="q-play" class="hidden">
  <div class="q-bar">
    <span id="q-pos"></span>
    <span id="q-score"></span>
  </div>
  <div class="q-progress"><div id="q-fill"></div></div>

  <div class="panel q-card" id="q-card">
    <p class="q-stem" id="q-stem"></p>
    <div id="q-table"></div>
    <div class="q-choices" id="q-choices"></div>
    <div class="q-exp hidden" id="q-exp"></div>
    <div class="row q-actions">
      <button id="q-back">back</button>
      <button class="primary" id="q-submit" disabled>submit</button>
      <button class="primary hidden" id="q-next">next</button>
    </div>
  </div>

  <div class="panel q-result hidden" id="q-result">
    <div class="left" id="r-pct"></div>
    <div class="muted" id="r-line"></div>
    <div class="row center">
      <button id="r-review">review</button>
      <button id="r-missed">retry missed</button>
      <button id="r-again">start over</button>
    </div>
  </div>

  <ol class="q-nav" id="q-nav" aria-label="Questions"></ol>

  <div class="row center" style="margin-top:22px">
    <button class="hidden" id="q-share">copy share link</button>
  </div>
</div>
<p class="error hidden center" id="q-error" role="alert"></p>
""", script="""<script type="module">
import { watchUser, signIn, api, when } from "/assets/app.js";
const $ = (id) => document.getElementById(id);
const params = new URLSearchParams(location.search);
const quizId = params.get("id");
const token = params.get("t");
const show = (id) => { for (const k of ["q-loading", "q-out", "q-list", "q-play"]) $(k).classList.toggle("hidden", k !== id); };
const err = (m) => { $("q-error").textContent = m; $("q-error").classList.remove("hidden"); };
const plural = (n, one, many) => `${n} ${n === 1 ? one : many}`;
let user = null;
let started = false;

$("sign-in").addEventListener("click", () => signIn().catch((e) => err(e.message)));

watchUser((u) => {
  user = u;
  if (quizId) { if (!started) { started = true; openQuiz(); } return; }
  if (!u) { show("q-out"); return; }
  loadList().catch((e) => { show("q-list"); err(e.message); });
});

// ------------------------------------------------ the list
async function loadList() {
  const [list, me] = await Promise.all([api("/v1/quizzes", { user }), api("/v1/me", { user }).catch(() => null)]);
  $("q-left").textContent = me ? `${plural(me.quiz_left, "quiz", "quizzes")} left` : "";
  const ul = $("quizzes"); ul.replaceChildren();
  for (const q of list.quizzes) {
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.href = `/quiz/?id=${encodeURIComponent(q.id)}`;
    a.textContent = q.lecture || "untitled pdf";
    const s = document.createElement("span");
    s.textContent = `${plural(q.n_questions, "question", "questions")}, ${when(q.created_at)}`;
    li.append(a, s);
    ul.append(li);
  }
  $("no-quizzes").classList.toggle("hidden", list.quizzes.length > 0);
  show("q-list");
}

// ------------------------------------------------ playing
let quiz = null, order = [], cur = 0, resp = {}, resultsOpen = false;
const key = () => `po-quiz-${quizId}`;
const save = () => { try { localStorage.setItem(key(), JSON.stringify({ resp, order, cur })); } catch {} };
const restore = () => { try { return JSON.parse(localStorage.getItem(key()) || "null"); } catch { return null; } };
const r = (i) => (resp[i] = resp[i] || { selected: null, answered: false, struck: [] });

async function openQuiz() {
  try {
    quiz = await api(`/v1/quiz/${encodeURIComponent(quizId)}${token ? `?t=${encodeURIComponent(token)}` : ""}`, { user });
  } catch (e) {
    // someone else's link without its token, or the owner signed out: sign in, then try again
    if (e.status === 404 && !user && !token) { started = false; show("q-out"); return; }
    show("");
    err(e.status === 404 ? "this quiz does not exist, or its link has changed." : e.message);
    return;
  }
  document.title = quiz.lecture || "quiz";
  document.querySelector(".top h1").textContent = quiz.lecture || "quiz";
  const n = quiz.questions.length;
  const saved = restore();
  if (saved && Array.isArray(saved.order) && saved.order.length && saved.order.every((i) => i < n)) {
    resp = saved.resp || {}; order = saved.order; cur = Math.min(saved.cur || 0, order.length - 1);
  } else {
    order = quiz.questions.map((_, i) => i);
  }
  $("q-share").classList.toggle("hidden", !quiz.owner);
  show("q-play");
  render();
}

function tally() {
  let right = 0, done = 0;
  for (const i of order) { const x = resp[i]; if (x && x.answered) { done++; if (x.selected === quiz.questions[i].correct) right++; } }
  return { right, done };
}

function bar() {
  const { right, done } = tally();
  $("q-pos").textContent = resultsOpen ? "done" : `${cur + 1} of ${order.length}`;
  $("q-score").textContent = done ? `${right} of ${done} right` : "";
  $("q-fill").style.width = `${(done / order.length) * 100}%`;
}

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

function render() {
  resultsOpen = false;
  $("q-result").classList.add("hidden");
  $("q-card").classList.remove("hidden");
  const i = order[cur], q = quiz.questions[i], x = r(i);
  $("q-stem").textContent = q.question;
  $("q-table").replaceChildren(...(q.table ? [table(q.table)] : []));
  const box = $("q-choices"); box.replaceChildren();
  for (const L of Object.keys(q.answers)) {
    const b = document.createElement("button");
    b.className = "q-choice";
    b.dataset.letter = L;
    const tag = document.createElement("span"); tag.className = "q-letter"; tag.textContent = L;
    const txt = document.createElement("span"); txt.textContent = q.answers[L];
    b.append(tag, txt);
    b.addEventListener("click", () => pick(L));
    b.addEventListener("contextmenu", (e) => {
      e.preventDefault();
      if (x.answered) return;
      x.struck = x.struck.includes(L) ? x.struck.filter((s) => s !== L) : [...x.struck, L];
      paint(); save();
    });
    box.append(b);
  }
  paint();
  bar(); nav(); save();
}

function paint() {
  const i = order[cur], q = quiz.questions[i], x = r(i);
  for (const b of document.querySelectorAll(".q-choice")) {
    const L = b.dataset.letter;
    b.classList.toggle("selected", !x.answered && x.selected === L);
    b.classList.toggle("struck", !x.answered && x.struck.includes(L));
    b.classList.toggle("right", x.answered && L === q.correct);
    b.classList.toggle("wrong", x.answered && L === x.selected && L !== q.correct);
    b.disabled = x.answered;
  }
  const exp = $("q-exp");
  exp.replaceChildren();
  if (x.answered) {
    for (const L of Object.keys(q.answers)) {
      const p = document.createElement("p");
      p.className = L === q.correct ? "right" : "";
      const tag = document.createElement("b"); tag.textContent = `${L}. `;
      p.append(tag, document.createTextNode(q.explanations?.[L] || ""));
      exp.append(p);
    }
    if (q.page) { const p = document.createElement("p"); p.className = "muted small"; p.textContent = `page ${q.page}`; exp.append(p); }
  }
  exp.classList.toggle("hidden", !x.answered);
  $("q-submit").classList.toggle("hidden", x.answered);
  $("q-submit").disabled = !x.selected;
  $("q-next").classList.toggle("hidden", !x.answered);
  $("q-next").textContent = cur === order.length - 1 ? "see score" : "next";
  $("q-back").disabled = cur === 0;
}

function pick(L) {
  const x = r(order[cur]);
  if (x.answered) return;
  x.selected = L; x.struck = x.struck.filter((s) => s !== L);
  paint(); save();
}

function submit() {
  const x = r(order[cur]);
  if (!x.selected || x.answered) return;
  x.answered = true;
  paint(); bar(); nav(); save();
}

function go(n) {
  if (n < 0) return;
  if (n >= order.length) { results(); return; }
  cur = n; render();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function nav() {
  const ol = $("q-nav"); ol.replaceChildren();
  order.forEach((i, n) => {
    const li = document.createElement("li");
    const b = document.createElement("button");
    b.textContent = n + 1;
    b.setAttribute("aria-label", `question ${n + 1}`);
    const x = resp[i];
    if (x && x.answered) b.className = x.selected === quiz.questions[i].correct ? "right" : "wrong";
    if (n === cur && !resultsOpen) b.setAttribute("aria-current", "true");
    b.addEventListener("click", () => go(n));
    li.append(b); ol.append(li);
  });
}

function results() {
  resultsOpen = true;
  const { right, done } = tally();
  $("q-card").classList.add("hidden");
  $("q-result").classList.remove("hidden");
  $("r-pct").textContent = done ? `${Math.round((right / done) * 100)}%` : "0%";
  const skipped = order.length - done;
  $("r-line").textContent = `${right} of ${order.length} right` + (skipped ? `, ${skipped} not answered` : "");
  const missed = order.filter((i) => resp[i]?.answered && resp[i].selected !== quiz.questions[i].correct);
  $("r-missed").classList.toggle("hidden", !missed.length);
  bar(); nav(); save();
}

function restart(list) {
  for (const i of list) delete resp[i];
  order = list; cur = 0; render();
}

$("q-submit").addEventListener("click", submit);
$("q-next").addEventListener("click", () => go(cur + 1));
$("q-back").addEventListener("click", () => go(cur - 1));
$("r-review").addEventListener("click", () => go(0));
$("r-missed").addEventListener("click", () => restart(order.filter((i) => resp[i]?.answered && resp[i].selected !== quiz.questions[i].correct)));
$("r-again").addEventListener("click", () => restart(quiz.questions.map((_, i) => i)));

$("q-share").addEventListener("click", async () => {
  const b = $("q-share");
  try {
    const { share_token } = await api(`/v1/quiz/${encodeURIComponent(quizId)}/share`, { method: "POST", user });
    const link = `${location.origin}/quiz/?id=${encodeURIComponent(quizId)}&t=${encodeURIComponent(share_token)}`;
    await navigator.clipboard.writeText(link);
    b.textContent = "link copied";
    setTimeout(() => { b.textContent = "copy share link"; }, 2000);
  } catch (e) { err(e.message || "the link could not be copied."); }
});

// A to E (or 1 to 5) picks, enter submits then moves on, arrows move
document.addEventListener("keydown", (e) => {
  if (!quiz || e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.key === "ArrowLeft") { e.preventDefault(); if (resultsOpen) go(order.length - 1); else go(cur - 1); return; }
  if (e.key === "ArrowRight") { e.preventDefault(); if (!resultsOpen) go(cur + 1); return; }
  if (resultsOpen) return;
  if (e.key === "Enter") {
    if (document.activeElement && document.activeElement.tagName === "BUTTON" && !document.activeElement.classList.contains("q-choice")) return;
    e.preventDefault();
    if (r(order[cur]).answered) go(cur + 1); else submit();
    return;
  }
  const letters = Object.keys(quiz.questions[order[cur]].answers);
  const k = /^[1-5]$/.test(e.key) ? letters[Number(e.key) - 1] : e.key.toUpperCase();
  if (letters.includes(k) && e.key.length === 1) { e.preventDefault(); pick(k); }
});
</script>""")

# ------------------------------------------------------------------ link
page("link/index.html", "link anki", "Link the PDF Occlusion add-on to your account.",
     body=top("link anki") + f"""
<div id="step-code">
  <p class="lede">the code anki is showing</p>
  <p class="code" id="code"></p>
</div>
<div id="link-out" class="hidden">
  <div class="row center" style="margin-top:22px"><button id="sign-in">{{G_ICON}}sign in with google</button></div>
  <p class="muted center" style="margin-top:14px">the first 50 pages and 2 quizzes are free and need no card. signing in keeps count of them.</p>
</div>
<div id="link-in" class="hidden">
  <p class="muted center" id="as" style="margin-top:18px"></p>
  <div class="row center">
    <button class="primary" id="approve">link this anki</button>
    <button id="switch">use another account</button>
  </div>
</div>
<p class="note center hidden" id="done">linked. you can close this tab and go back to anki.</p>
<p class="error hidden center" id="link-error" role="alert"></p>
""", script="""<script type="module">
import { watchUser, signIn, signOut, api } from "/assets/app.js";
const $ = (id) => document.getElementById(id);
const code = (new URLSearchParams(location.search).get("code") || "").toUpperCase();
$("code").textContent = code || "no code";
const err = (m) => { $("link-error").textContent = m; $("link-error").classList.remove("hidden"); };
const linked = new URLSearchParams(location.search).has("linked");
if (linked) { $("step-code").classList.add("hidden"); $("done").classList.remove("hidden"); }
else if (!code) err("Open this page from the add-on: Auto, then Sign in.");
let user = null;
watchUser((u) => {
  user = u;
  $("link-out").classList.toggle("hidden", !!u || !code);
  $("link-in").classList.toggle("hidden", !u || !code);
  if (u) $("as").textContent = u.email;
});
// one Google window at a time: a second click would cancel the open one
const google = async () => {
  $("sign-in").disabled = true;
  try { await signIn(); } catch (e) { err(e.message); } finally { $("sign-in").disabled = false; }
};
$("sign-in").addEventListener("click", google);
$("switch").addEventListener("click", async () => { await signOut(); await google(); });
$("approve").addEventListener("click", async () => {
  $("approve").disabled = true;
  try {
    await api("/v1/link/approve", { method: "POST", body: { code }, user });
    window.poTrack?.("link_result", { result: "ok" });
    $("link-in").classList.add("hidden"); $("step-code").classList.add("hidden"); $("done").classList.remove("hidden");
    // each code works once: coming back to this page should not offer it again
    history.replaceState(null, "", "/link/?linked=1");
  } catch (e) {
    window.poTrack?.("link_result", { result: "error", message: String(e.message || "").slice(0, 120) });
    err(e.status === 404 || e.status === 409
      ? "This code has already been used or has expired. If Anki shows you as signed in, you're all set. If not, start again from Anki."
      : e.message);
    $("approve").disabled = false;
  }
});
// how long the page was open and how far it got, each time it is hidden or closed
const opened = Date.now();
let left = false;
const leave = () => {
  if (left) return;
  left = true;
  const stage = linked ? "linked" : !code ? "no_code" : !$("done").classList.contains("hidden") ? "linked" : user ? "signed_in" : "signed_out";
  window.poTrack?.("link_left", { seconds: Math.round((Date.now() - opened) / 1000), stage });
};
document.addEventListener("visibilitychange", () => { if (document.hidden) leave(); else left = false; });
addEventListener("pagehide", leave);
</script>""")

# ------------------------------------------------------------------ privacy
page("privacy/index.html", "privacy", "Privacy policy for PDF Occlusion.",
     body=top("privacy") + f"""
<div class="prose">
  <p class="muted center" style="margin-top:14px">effective november 21, 2026</p>

  <h2>1. scope</h2>
  <p>This Privacy Policy describes how PDF Occlusion ("we", "us" or "our") collects, uses and discloses information in connection with this website, the PDF Occlusion add-on and the Auto service (together, the "Service"). By using the Service you acknowledge the practices described in this policy.</p>

  <h2>2. information we collect</h2>
  <ul>
    <li><b>Account information.</b> When you sign in, we receive your email address and an account identifier from the sign-in provider you choose.</li>
    <li><b>Submitted content.</b> When you use Auto to make boxes, cards or a quiz, the add-on transmits the text of every page of the PDF, a few page images to identify the document, images of the pages you select and the text found on them, the settings and instructions you choose, and any notes you attach ("Submitted Content"). To make them, the Service first works out what the document is and what each page teaches; those notes are part of Submitted Content.</li>
    <li><b>Usage records.</b> For each use of Auto we record the document name, the number of pages, the date and the credits consumed.</li>
    <li><b>Quizzes.</b> When you make a quiz, we keep its questions, answers and explanations, with the document name, in your account so you can take it later on any device. If you share a quiz, anyone with its link can view it until you change the link. Your answers to a quiz are kept only in your browser.</li>
    <li><b>Installation identifiers.</b> Linking the add-on to your account creates a key stored on your device. We retain only a one-way fingerprint of that key. The add-on also sends a one-way fingerprint of your computer's hardware identifier, which we use to limit free pages to one allowance per computer; the identifier itself never leaves your computer.</li>
    <li><b>Usage statistics.</b> The add-on reports which of its buttons and features are used, page and card counts, errors, and its own, Anki's and your operating system's versions, tagged with the one-way computer fingerprint described above and, when you are signed in, your account. It does not report page images, file names, card text or anything you type. You can turn this off with the <code>usage_stats</code> setting in the add-on's config. This website records the pages you view, the links and buttons you click, whether signing in and linking worked, and the site that referred you, tagged with a random identifier stored in your browser.</li>
    <li><b>Payment information.</b> Payments are processed by a third-party payment processor. We do not receive or store full payment card numbers. We retain the customer and transaction identifiers needed to provide what you purchased.</li>
  </ul>

  <h2>3. how we use information</h2>
  <p>We use information to provide, operate and maintain the Service; to understand how the Service is used and improve it; to process transactions and account for credits; to authenticate users and linked installations; to detect and prevent fraud, abuse and security incidents; to communicate with you about your account; and to comply with legal obligations.</p>

  <h2>4. submitted content</h2>
  <p>Submitted Content is processed solely to provide the Service to you. It is not retained after your request has been completed (notes about the document are kept only while a run is in progress, at most 6 hours; quizzes made from it are kept as described in section 2), it is not sold, and it is not used to train machine learning models. You remain responsible for ensuring that you have the right to submit it.</p>

  <h2>5. disclosure of information</h2>
  <p>We do not sell or rent personal information. We disclose information only (a) to service providers that host, authenticate, process payments or otherwise perform services on our behalf, subject to obligations of confidentiality; (b) where required by law, regulation, legal process or governmental request; (c) to protect the rights, property or safety of the Service, its users or others; (d) in connection with a merger, acquisition or sale of assets; or (e) with your consent.</p>

  <h2>6. retention</h2>
  <p>Account information, usage records and quizzes are retained for as long as your account is active. When you delete your account, they are deleted, except where retention is required by law or by our payment processor.</p>

  <h2>7. security</h2>
  <p>We use reasonable administrative, technical and organizational measures to protect information. No method of transmission or storage is completely secure, and we cannot guarantee absolute security.</p>

  <h2>8. your choices and rights</h2>
  <p>You may sign out linked installations or delete your account at any time from the <a href="/account/">account page</a>. Depending on where you live, you may have additional rights to access, correct, port, restrict or object to the processing of your personal information. To exercise them, contact us as described below.</p>

  <h2>9. children</h2>
  <p>The Service is not directed to children under 13, and we do not knowingly collect personal information from them. If you believe a child has provided us information, contact us and we will delete it.</p>

  <h2>10. international users</h2>
  <p>The Service is operated from the United States. By using it, you consent to the transfer and processing of your information in the United States, where data protection laws may differ from those of your country.</p>

  <h2>11. changes</h2>
  <p>We may update this policy from time to time. Changes take effect when posted on this page with a new effective date. Your continued use of the Service after that date constitutes acceptance of the updated policy.</p>

  <h2>12. contact</h2>
  <p>Questions about this policy may be submitted to <a href="{HELP}">pdf-occlusion-support@googlegroups.com</a>.</p>
</div>
""")

# ------------------------------------------------------------------ terms
page("terms/index.html", "terms", "Terms of service for PDF Occlusion.",
     body=top("terms") + f"""
<div class="prose">
  <p class="muted center" style="margin-top:14px">effective november 21, 2026</p>

  <h2>1. acceptance</h2>
  <p>These Terms of Service (the "Terms") govern your access to and use of this website, the PDF Occlusion add-on and the Auto service (together, the "Service"). By using the Service you agree to these Terms. If you do not agree, do not use the Service.</p>

  <h2>2. eligibility</h2>
  <p>You must be at least 13 years old to use the Service, and old enough to form a binding contract where you live to make a purchase.</p>

  <h2>3. accounts</h2>
  <p>You are responsible for your account, for keeping your sign-in and linked installations secure, and for all activity under your account. Accounts are for one person and may not be shared, sold or transferred.</p>

  <h2>4. the add-on</h2>
  <p>The add-on's source code is licensed under the MIT License. These Terms govern the online features of the Service, including accounts, credits and Auto.</p>

  <h2>5. credits</h2>
  <p>Auto is measured in pages and quizzes. Each page processed for boxes or cards consumes one page credit; pages are counted as they are completed. Each quiz consumes one quiz credit once its questions are ready. Credits have no cash value and are not transferable. Credits included with a subscription expire at the end of each monthly period. Purchased page credits do not expire while your account remains active.</p>

  <h2>6. subscriptions and payment</h2>
  <p>Subscriptions are billed in advance and renew automatically at the end of each period until cancelled. You may cancel at any time; cancellation takes effect at the end of the current period. Except where required by law, all fees are non-refundable. We may change prices with notice, effective at your next renewal. You are responsible for applicable taxes.</p>

  <h2>7. your content</h2>
  <p>You retain all rights to the documents and other material you submit. You grant us a limited, non-exclusive license to process that material solely to provide the Service to you. You represent that you have all rights necessary to submit it and that doing so does not violate any law or the rights of any third party.</p>

  <h2>8. acceptable use</h2>
  <p>You agree not to: use the Service unlawfully or to infringe the rights of others; submit material you are not entitled to use; interfere with, overload or attempt to gain unauthorized access to the Service; circumvent usage limits or credit accounting; access the Service by automated means other than the add-on and this website; or resell or redistribute the Service.</p>

  <h2>9. output</h2>
  <p>Boxes, cards and quizzes produced by the Service are generated automatically and may be incomplete or inaccurate. You are responsible for reviewing them before use. Nothing produced by the Service is professional, medical, legal or other advice.</p>

  <h2>10. intellectual property</h2>
  <p>Except for the add-on source code and your content, the Service and all related materials are owned by us and protected by law. No rights are granted other than those expressly stated in these Terms.</p>

  <h2>11. suspension and termination</h2>
  <p>We may suspend or terminate your access to the Service at any time if you breach these Terms or if required by law. You may stop using the Service and delete your account at any time.</p>

  <h2>12. disclaimer of warranties</h2>
  <p>THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE", WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, ACCURACY AND NON-INFRINGEMENT. WE DO NOT WARRANT THAT THE SERVICE WILL BE UNINTERRUPTED, ERROR-FREE OR SECURE.</p>

  <h2>13. limitation of liability</h2>
  <p>TO THE FULLEST EXTENT PERMITTED BY LAW, WE WILL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL OR PUNITIVE DAMAGES, OR FOR ANY LOSS OF DATA, PROFITS OR GOODWILL, ARISING FROM OR RELATED TO THE SERVICE. OUR TOTAL LIABILITY FOR ANY CLAIM WILL NOT EXCEED THE AMOUNT YOU PAID US IN THE TWELVE MONTHS BEFORE THE CLAIM AROSE.</p>

  <h2>14. indemnification</h2>
  <p>You agree to indemnify and hold us harmless from any claims, losses and expenses, including reasonable legal fees, arising from your use of the Service, your content or your breach of these Terms.</p>

  <h2>15. general</h2>
  <p>These Terms are governed by the laws of the United States and the applicable state, without regard to conflict-of-law principles. If any provision is found unenforceable, the remainder stays in effect. Our failure to enforce a provision is not a waiver. These Terms, together with the Privacy Policy, are the entire agreement between you and us regarding the Service.</p>

  <h2>16. changes</h2>
  <p>We may modify these Terms at any time. Changes take effect when posted on this page with a new effective date. Your continued use of the Service after that date constitutes acceptance of the modified Terms.</p>

  <h2>17. contact</h2>
  <p>Questions about these Terms may be submitted to <a href="{HELP}">pdf-occlusion-support@googlegroups.com</a>.</p>
</div>
""")
