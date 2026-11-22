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
<meta property="og:title" content="PDF Occlusion">
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

NAV = [("Pricing", "/pricing/", "pricing"), ("Account", "/account/", "account")]

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
    <a href="/privacy/">Privacy</a>
    <a href="/terms/">Terms</a>
    <a href="{HELP}">Help</a>
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
    back = "" if not small else '<a class="back" href="/" onclick="if (document.referrer.startsWith(location.origin)) { history.back(); return false; }">&larr; Back</a>\n'
    return back + f"""<div class="top{' small' if small else ''}">
  <a href="/" aria-label="PDF Occlusion home"><img class="mark" src="/assets/logo.svg" alt=""></a>
  <h1>{name}</h1>
  <nav class="links" aria-label="Main">
    {links}
  </nav>
</div>
"""


def version(name):
    import hashlib
    return hashlib.sha1(open(os.path.join(HERE, "assets", name), "rb").read()).hexdigest()[:8]


def page(path, title, desc, body, script="", wide=False):
    body = body.replace("{G_ICON}", G_ICON)
    head = HEAD.format(title=title, desc=desc).replace("CSSVER", version("site.css"))
    if wide:
        head = head.replace("<main>", '<main class="wide">')
    script = script.replace("JSVER", version("quiz.js"))
    html = head + body + FOOT.format(script=(script + "\n" + BEACON).strip())
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
  <div><div class="amount">Free</div><div class="what">60 credits to start</div></div>
  <div><div class="amount">$14.99</div><div class="what">1,200 credits per month</div></div>
  <div><div class="amount">$9.99</div><div class="what">400 credits, no expiration</div></div>
</div>"""

page("index.html", "PDF Occlusion",
     "Generate turns a PDF into image occlusion boxes, text cards or a practice quiz, inside Anki. Your first 60 credits are free.",
     body=top("PDF Occlusion", small=False) + f"""
<div class="badges">
  <span class="badge"><span class="badge-k">Add-on code</span><span class="badge-v">783821131</span></span>
  <span class="badge"><span class="badge-k">Anki</span><span class="badge-v">23.10+</span></span>
  <span class="badge"><span class="badge-k">License</span><span class="badge-v">MIT</span></span>
</div>

<p class="lede">Press Generate and choose what your PDF becomes: boxes over its labels, cards from its text, or a quiz you can take on any device.</p>

<div style="margin-top:26px">{PRICES}</div>

<div class="panel demo">
  <img src="/assets/demo.gif" width="840" height="525" alt="PDF Occlusion open in Anki, placing boxes over the labels of an anatomy slide">
</div>

<section class="center">
  <h2>Three Outputs from One PDF</h2>
  <div class="panel outputs">
    <div><div class="name">Boxes</div><div class="what">Every label and key term covered on the page itself</div></div>
    <div><div class="name">Cards</div><div class="what">One fact per card, drawn from the text of each page</div></div>
    <div><div class="name">Quiz</div><div class="what">Basic Science, Clinical, Quick Recall or your own Custom style, with an explanation for every answer. For any course or exam, from Step 1 and COMLEX to NCLEX, PANCE and the MCAT.</div></div>
  </div>
</section>

<section class="center">
  <h2>Works with Any PDF</h2>
  <ul class="chips">
    <li>Lecture slides</li>
    <li>Anatomy atlases</li>
    <li>Histology</li>
    <li>Textbook figures</li>
    <li>Tables</li>
    <li>Vocabulary lists</li>
    <li>Character charts</li>
    <li>Maps</li>
    <li>Flowcharts</li>
    <li>Formula sheets</li>
    <li>Board prep</li>
  </ul>
</section>

<section class="center">
  <h2>Set It Once</h2>
  <ul class="chips">
    <li>All labels or key ones</li>
    <li>Key phrases or whole lines</li>
    <li>Numbers and doses</li>
    <li>Bold or colored text</li>
    <li>Tables by cell or row</li>
    <li>Pathways step by step</li>
    <li>Pages to skip</li>
    <li>Your own rules</li>
  </ul>
</section>
""")

# ------------------------------------------------------------------ pricing
page("pricing/index.html", "Pricing",
     "Start with 60 free credits. Monthly is $14.99 and Yearly is $149.90, each with 1,200 credits per month, or buy 400 credits for $9.99. Boxes and cards use 1 credit per slide; quizzes use 2 credits per question.",
     body=top("Pricing", "pricing") + f"""
<p class="lede">Generate uses credits. The add-on itself is free.</p>

<div class="panel outputs costs" style="margin-top:30px">
  <div><div class="name">Boxes</div><div class="what">1 credit per slide</div></div>
  <div><div class="name">Cards</div><div class="what">1 credit per slide</div></div>
  <div><div class="name">Quiz</div><div class="what">2 credits per question</div></div>
</div>

<div class="panel">
  <ul class="plain price-list">
    <li>
      <div><div class="name">Starter</div><div class="what">60 credits for new accounts</div></div>
      <div class="amount">Free</div>
    </li>
    <li>
      <div><div class="name">Monthly</div><div class="what">1,200 credits per month</div></div>
      <div class="row" style="margin:0"><span class="amount">$14.99</span><button class="primary" data-buy="monthly">Subscribe</button></div>
    </li>
    <li>
      <div><div class="name">Yearly</div><div class="what">1,200 credits per month, billed annually</div></div>
      <div class="row" style="margin:0"><span class="amount">$149.90</span><button data-buy="yearly">Subscribe</button></div>
    </li>
    <li>
      <div><div class="name">400 Credits</div><div class="what">Credits do not expire</div></div>
      <div class="row" style="margin:0"><span class="amount">$9.99</span><button data-buy="pack">Buy</button></div>
    </li>
  </ul>
</div>
<p class="error hidden center" id="buy-error" role="alert"></p>

<section>
  <ul class="dots">
    <li>Plan credits renew each month. Purchased credits are used after plan credits run out.</li>
    <li>Cancel anytime from your account. Your plan stays active until the end of the billing period.</li>
    <li>Slides are charged as they are completed, so stopping a run early only uses what was finished. A quiz has up to 40 questions and is charged once it is ready.</li>
    <li>Placing boxes by hand is always free.</li>
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
# The one signed-in place: credits, quizzes, installs. Quizzes play at
# /quiz/?id=..., which share links also use.
page("account/index.html", "Account", "Your quizzes, credits, plan and linked Anki installs.",
     body=top("Account", "account") + f"""
<div id="signed-out" class="hidden">
  <p class="lede">Sign in to see your practice quizzes and credits.</p>
  <div class="row center" style="margin-top:22px"><button id="sign-in">{{G_ICON}}Sign In with Google</button></div>
</div>

<div id="signed-in" class="hidden">
  <p class="lede" id="who"></p>
  <p class="note center hidden" id="paid"></p>

  <div class="panel" style="margin-top:26px">
    <div class="left" id="left">0</div>
    <div class="muted" id="left-note">Credits remaining</div>
    <dl class="kv">
      <dt>Plan</dt><dd id="plan">None</dd>
      <dt class="hidden" id="month-k">This month</dt><dd class="hidden" id="month"></dd>
      <dt class="hidden" id="free-k">Free credits</dt><dd class="hidden" id="free"></dd>
      <dt class="hidden" id="packs-k">Purchased credits</dt><dd class="hidden" id="packs"></dd>
    </dl>
    <div class="row">
      <a class="btn primary" href="/pricing/" id="upgrade">View Plans</a>
      <button id="pack">Buy 400 Credits</button>
      <button class="hidden" id="billing">Manage Billing</button>
    </div>
  </div>

  <div class="panel">
    <div class="panel-head">
      <h3>Practice Quizzes</h3>
      <label class="tick-all hidden" id="pick-all-wrap"><input type="checkbox" id="pick-all">Select All</label>
    </div>
    <ul class="plain list quiz-list" id="quizzes"></ul>
    <p class="muted small hidden" id="no-quizzes">No quizzes yet.</p>
    <div class="pickbar hidden" id="pickbar">
      <span class="pick-count" id="pick-count"></span>
      <div class="seg" id="pick-only">
        <button type="button" data-only="all"></button>
        <button type="button" data-only="missed"></button>
        <button type="button" data-only="unseen"></button>
        <button type="button" data-only="flagged"></button>
      </div>
      <span class="pick-go">
        <button type="button" class="primary" id="pick-go">Start</button>
        <button type="button" id="pick-clear">Clear</button>
      </span>
    </div>
    <form class="ids-row hidden" id="ids-row">
      <input id="ids-input" type="text" placeholder="Question IDs" aria-label="Question IDs" autocomplete="off" autocapitalize="none" spellcheck="false">
      <button type="submit" id="ids-go" disabled>Start</button>
    </form>
  </div>

  <div class="panel hidden" id="practice">
    <h3>Practice History</h3>
    <div class="hidden" id="open-sec"><h4>In Progress</h4><ul class="plain list test-list" id="open-list"></ul></div>
    <div class="hidden" id="weak-sec"><h4>Weakest Quizzes</h4><ul class="plain list test-list" id="weak-list"></ul></div>
    <div class="hidden" id="past-sec"><h4>Past Tests</h4><ul class="plain list test-list" id="past-list"></ul></div>
  </div>

  <div class="panel" id="devices-panel">
    <h3>Anki Installs</h3>
    <ul class="plain list" id="devices"></ul>
    <p class="muted small hidden" id="no-devices">No installs linked yet.</p>
    <div class="row"><button class="hidden" id="unlink">Sign Out of All Installs</button></div>
  </div>

  <div class="panel">
    <h3>History</h3>
    <ul class="plain list" id="jobs"></ul>
    <p class="muted small hidden" id="no-jobs">No activity yet.</p>
  </div>

  <div class="row center" style="margin-top:22px">
    <button id="sign-out">Sign Out</button>
    <button id="delete">Delete Account</button>
    <button class="hidden" id="delete-yes">Delete My Account and History</button>
    <button class="hidden" id="delete-no">Cancel</button>
  </div>
</div>
<p class="error hidden center" id="acct-error" role="alert"></p>
""", script="""<script type="module">
import { watchUser, signIn, signOut, deleteSignIn, api, when } from "/assets/app.js";
import * as P from "/assets/practice.js";
import * as S from "/assets/sync.js";
const $ = (id) => document.getElementById(id);
let user = null;
const err = (m) => { $("acct-error").textContent = m; $("acct-error").classList.remove("hidden"); };
const n = (x) => Number(x || 0).toLocaleString();
const STYLES = { step1: "Basic Science", shelf: "Clinical", recall: "Quick Recall", custom: "Custom" };
$("sign-in").addEventListener("click", () => signIn().catch((e) => err(e.message)));
$("sign-out").addEventListener("click", () => signOut());
const paid = new URLSearchParams(location.search).get("paid");
if (paid) {
  $("paid").textContent = paid === "pack" ? "Thank you. 400 credits were added to your account." : "Thank you. Your plan is active.";
  $("paid").classList.remove("hidden");
}
// credits from the server, or pages from a server that does not count credits yet
function credits(me) {
  const c = me.credits || {};
  return {
    left: me.credits_left ?? me.pages_left ?? 0,
    free: c.free ?? me.free_left ?? 0,
    used: c.plan_used ?? me.plan_used ?? 0,
    allowance: c.plan_allowance ?? me.plan_allowance ?? 0,
    pack: c.pack ?? me.pack_pages ?? 0,
  };
}
const row = (id, text) => { $(id).textContent = text || ""; $(id).classList.toggle("hidden", !text); $(id + "-k").classList.toggle("hidden", !text); };
async function load() {
  const [me, list] = await Promise.all([api("/v1/me", { user }), api("/v1/quizzes", { user }).catch(() => ({ quizzes: [] }))]);
  const c = credits(me);
  $("who").textContent = me.email || "";
  $("left").textContent = n(c.left);
  $("left-note").textContent = c.left === 1 ? "Credit remaining" : "Credits remaining";
  $("plan").textContent = me.plan === "yearly" ? "Yearly" : me.plan === "monthly" ? "Monthly" : "None";
  row("month", me.plan ? `${n(c.used)} of ${n(c.allowance)} used` : "");
  row("free", c.free ? `${n(c.free)} remaining` : "");
  row("packs", c.pack ? `${n(c.pack)} remaining` : "");
  $("upgrade").classList.toggle("hidden", !!me.plan);
  $("billing").classList.toggle("hidden", !me.plan && !c.pack && !paid);
  quizzes(list.quizzes || []);
  const dev = $("devices"); dev.replaceChildren();
  for (const d of me.devices) {
    const li = document.createElement("li");
    li.innerHTML = "<span></span><span></span>";
    li.children[0].textContent = d.label || "Anki";
    li.children[1].textContent = d.last_used ? `Last used ${when(d.last_used)}` : `Linked ${when(d.created_at)}`;
    dev.append(li);
  }
  $("no-devices").classList.toggle("hidden", me.devices.length > 0);
  $("unlink").classList.toggle("hidden", me.devices.length === 0);
  const jobs = $("jobs"); jobs.replaceChildren();
  for (const j of me.jobs) {
    const li = document.createElement("li");
    li.innerHTML = "<span></span><span></span>";
    li.children[0].textContent = j.lecture || "Untitled PDF";
    li.children[1].textContent = `${j.slides_total} ${j.slides_total === 1 ? "slide" : "slides"}, ${when(j.created_at)}`;
    jobs.append(li);
  }
  $("no-jobs").classList.toggle("hidden", me.jobs.length > 0);
}
let quizList = [];
function quizzes(list) {
  quizList = list;
  const ul = $("quizzes"); ul.replaceChildren();
  for (const q of list) {
    const li = document.createElement("li");
    li.dataset.id = q.id;
    const tick = document.createElement("input");
    tick.type = "checkbox";
    tick.className = "pick";
    tick.setAttribute("aria-label", `Add ${q.lecture || "this quiz"} to a practice set`);
    tick.addEventListener("change", paintPick);
    const text = document.createElement("div");
    const a = document.createElement("a");
    a.href = `/quiz/?id=${encodeURIComponent(q.id)}`;
    a.textContent = q.lecture || "Untitled PDF";
    const meta = document.createElement("div");
    meta.className = "muted small";
    const date = document.createElement("span");
    date.className = "nowrap";
    date.textContent = when(q.created_at);
    meta.append([STYLES[q.style], `${q.n_questions} ${q.n_questions === 1 ? "question" : "questions"}`].filter(Boolean).join(", ") + ", ", date);
    const st = P.stats(q.id, q.n_questions);
    if (st.seen) {
      const standing = document.createElement("span");
      standing.className = "standing";
      standing.textContent = `${st.seen} of ${q.n_questions} tried, ${Math.round((st.right / st.seen) * 100)}% correct`;
      meta.append(standing);
    }
    text.append(a, meta);
    const share = document.createElement("button");
    share.className = "small-btn";
    share.textContent = "Copy Link";
    share.addEventListener("click", () => copyLink(q.id, share));
    li.append(tick, text, share);
    ul.append(li);
  }
  $("no-quizzes").classList.toggle("hidden", list.length > 0);
  $("pick-all-wrap").classList.toggle("hidden", list.length < 2);
  $("ids-row").classList.toggle("hidden", !list.length);
  paintPick();
}

// ------------------------------------------------ practice sets
// Tick quizzes to play them shuffled together, all of their questions or
// only the ones missed, never tried or flagged here.
let pickOnly = "all";
const picked = () => [...document.querySelectorAll("#quizzes input.pick:checked")].map((t) => t.closest("li").dataset.id);
function counts(ids) {
  const c = { all: 0, missed: 0, unseen: 0, flagged: 0 };
  for (const id of ids) {
    const n = (quizList.find((q) => q.id === id) || {}).n_questions || 0;
    const st = P.stats(id, n);
    c.all += n; c.missed += st.seen - st.right; c.unseen += Math.max(0, n - st.seen); c.flagged += st.flagged;
  }
  return c;
}
const ONLY = { all: "All", missed: "Missed", unseen: "Unseen", flagged: "Flagged" };
function paintPick() {
  const ids = picked();
  $("pickbar").classList.toggle("hidden", !ids.length);
  const all = document.querySelectorAll("#quizzes input.pick");
  $("pick-all").checked = all.length > 0 && ids.length === all.length;
  if (!ids.length) { pickOnly = "all"; return; }
  const c = counts(ids);
  if (!c[pickOnly]) pickOnly = "all";
  $("pick-count").textContent = `${ids.length} ${ids.length === 1 ? "Quiz" : "Quizzes"}`;
  for (const b of document.querySelectorAll("#pick-only button")) {
    const k = b.dataset.only;
    b.textContent = `${ONLY[k]} ${c[k]}`;
    b.disabled = !c[k];
    b.classList.toggle("on", k === pickOnly && !!c[k]);
  }
  $("pick-go").disabled = !c[pickOnly];
}
$("pick-only").addEventListener("click", (e) => {
  const b = e.target.closest("button");
  if (!b || b.disabled) return;
  pickOnly = b.dataset.only;
  paintPick();
});
$("pick-all").addEventListener("change", () => {
  for (const t of document.querySelectorAll("#quizzes input.pick")) t.checked = $("pick-all").checked;
  paintPick();
});
$("pick-clear").addEventListener("click", () => {
  for (const t of document.querySelectorAll("#quizzes input.pick")) t.checked = false;
  paintPick();
});
$("pick-go").addEventListener("click", () => {
  const ids = picked();
  if (!ids.length) return;
  const what = ids.length === 1 ? `id=${encodeURIComponent(ids[0])}` : `set=${ids.map(encodeURIComponent).join(",")}`;
  location.href = `/quiz/?${what}` + (pickOnly !== "all" ? `&only=${pickOnly}` : "");
});

// Questions by the IDs shown on each question, typed or pasted.
const typedIds = () => [...new Set($("ids-input").value.toLowerCase().split(/[^a-z0-9]+/).filter(Boolean))];
$("ids-input").addEventListener("input", () => { $("ids-go").disabled = !typedIds().length; });
$("ids-row").addEventListener("submit", (e) => {
  e.preventDefault();
  const ids = typedIds();
  if (ids.length) location.href = `/quiz/?q=${ids.join(",")}`;
});

// ------------------------------------------------ practice history
// Tests in progress and finished, and the quizzes you do worst on, from
// this browser only.
const pct = (a, b) => (b ? `${Math.round((a / b) * 100)}%` : "");
function testRow(href, title, sub, how, del) {
  const li = document.createElement("li");
  const text = document.createElement("div");
  const a = document.createElement("a");
  a.href = href;
  a.textContent = title || "Quiz";
  text.append(a);
  const meta = document.createElement("div");
  meta.className = "muted small";
  meta.textContent = [sub, ...how].filter(Boolean).join(", ");
  text.append(meta);
  li.append(text);
  if (del) {
    const b = document.createElement("button");
    b.className = "small-btn";
    b.textContent = "Delete";
    b.addEventListener("click", () => {
      if (!b.classList.contains("armed")) {
        for (const x of document.querySelectorAll(".test-list .armed")) { x.classList.remove("armed"); x.textContent = "Delete"; }
        b.classList.add("armed");
        b.textContent = "Confirm Delete";
        return;
      }
      P.deleteTest(del);
      practice();
      quizzes(quizList);
    });
    li.append(b);
  }
  return li;
}
function fill(name, rows) {
  $(`${name}-list`).replaceChildren(...rows);
  $(`${name}-sec`).classList.toggle("hidden", !rows.length);
  return rows.length;
}
function practice() {
  const tests = P.listTests();
  const line = (t) => testRow(`/quiz/?${t.q}&test=${encodeURIComponent(t.id)}`, t.where, t.label,
    [`${t.right + t.wrong} of ${t.n} answered`, t.right + t.wrong ? `${pct(t.right, t.right + t.wrong)} correct` : "", when(t.updated)], t.id);
  const open = fill("open", tests.filter((t) => !t.done && !t.ended).map(line));
  const past = fill("past", tests.filter((t) => t.done || t.ended).map(line));
  const weak = P.quizzesPlayed().filter((z) => z.q && z.seen >= 5 && z.right < z.seen)
    .sort((a, b) => a.right / a.seen - b.right / b.seen).slice(0, 5)
    .map((z) => testRow(`/quiz/?${z.q}&only=missed`, z.name, "", [`${z.seen - z.right} missed`, `${pct(z.right, z.seen)} correct`]));
  const w = fill("weak", weak);
  $("practice").classList.toggle("hidden", !(open || past || w));
}
practice();
async function copyLink(id, b) {
  b.disabled = true;
  try {
    const { share_token } = await api(`/v1/quiz/${encodeURIComponent(id)}/share`, { method: "POST", user });
    await navigator.clipboard.writeText(`${location.origin}/quiz/?id=${encodeURIComponent(id)}&t=${encodeURIComponent(share_token)}`);
    b.textContent = "Copied";
    setTimeout(() => { b.textContent = "Copy Link"; }, 2000);
  } catch (e) { err(e.message || "The link could not be copied."); }
  b.disabled = false;
}
watchUser(async (u) => {
  user = u;
  S.setUser(u);
  // your practice from every device, then the lists again
  if (u) S.pullAll().then(() => { practice(); quizzes(quizList); });
  $("signed-out").classList.toggle("hidden", !!u);
  $("signed-in").classList.toggle("hidden", !u);
  // practice history is this browser's, so it shows signed out too
  if (u) $("signed-in").insertBefore($("practice"), $("devices-panel"));
  else $("signed-out").append($("practice"));
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
# /quiz/?id=...(&t=share token) plays one quiz, signed in or not. Without an
# id, /quiz/ goes to the account page, which lists the quizzes.
page("quiz/index.html", "Quiz", "A practice quiz made from lecture slides.", wide=True,
     body="""<script>(function () { var p = new URLSearchParams(location.search); if (!p.get("id") && !p.get("set") && !p.get("q")) location.replace("/account/"); })();</script>
""" + top("Quiz").replace("<h1>", '<h1 id="q-title">').replace("</h1>", '</h1>\n  <p class="q-sub muted hidden" id="q-sub"></p>') + f"""
<div id="q-loading" class="muted center" style="margin-top:22px">Loading</div>

<div id="q-out" class="hidden">
  <p class="lede">Sign in to see this quiz.</p>
  <div class="row center" style="margin-top:22px"><button id="sign-in">{{G_ICON}}Sign In with Google</button></div>
</div>

<div id="q-play" class="hidden">
  <div class="q-bar">
    <span id="q-progress-label"></span>
    <button class="q-tool" id="q-reset-test" title="Clear every answer in this test" disabled>Reset Test</button>
  </div>
  <div class="q-progress"><div id="q-fill"></div></div>

  <div class="q-layout">
    <aside class="q-rail" aria-label="Questions">
      <div class="q-rail-title">Questions</div>
      <div class="q-scope hidden" id="q-scope"><button type="button" id="q-scope-redo"></button><button type="button" id="q-scope-all"></button></div>
      <div class="q-counts hidden" id="q-counts"></div>
      <div class="q-grid" id="q-grid"></div>
      <div class="q-legend">
        <span><i class="q-sw right"></i>Correct</span>
        <span><i class="q-sw wrong"></i>Incorrect</span>
        <span><i class="q-sw skipped"></i>Skipped</span>
        <span><i class="q-flag-key">&#9873;</i>Flagged</span>
      </div>
    </aside>

    <div class="q-main">
      <div class="panel q-card" id="q-card">
        <div class="q-top">
          <span class="q-meta" id="q-meta"></span>
          <span class="q-tools">
            <button type="button" class="q-tool q-timer" id="q-timer" aria-pressed="false">1:30</button>
            <button type="button" class="q-tool q-id" id="q-id" title="Copy this question's ID"></button>
          </span>
        </div>
        <div class="q-hist" id="q-hist"></div>
        <p class="q-stem" id="q-stem"></p>
        <div id="q-table"></div>
        <div id="q-img"></div>
        <div class="q-choices" id="q-choices"></div>
        <div class="q-exp hidden" id="q-exp">
          <h3>Explanations</h3>
          <div id="q-exp-items"></div>
        </div>
        <div class="q-actions">
          <span class="q-score" id="q-score"></span>
          <span class="q-buttons">
            <button type="button" class="q-flag" id="q-flag" aria-pressed="false">Flag</button>
            <button type="button" id="q-reset" title="Clear your answer to this question">Reset</button>
            <button type="button" id="q-back" title="Previous question (Left Arrow)">Back</button>
            <button type="button" class="primary" id="q-submit" title="Submit (Enter)" disabled>Submit</button>
            <button type="button" id="q-next">Skip</button>
          </span>
        </div>
      </div>

      <div class="panel q-result hidden" id="q-result">
        <h2>Quiz Complete</h2>
        <div class="q-donut">
          <svg width="148" height="148" viewBox="0 0 148 148" aria-hidden="true">
            <circle cx="74" cy="74" r="60" fill="none" class="q-donut-track" stroke-width="14"/>
            <circle cx="74" cy="74" r="60" fill="none" class="q-donut-arc" stroke-width="14" stroke-dasharray="376.99" stroke-dashoffset="376.99" stroke-linecap="round" id="r-arc"/>
          </svg>
          <div class="q-donut-label"><div class="q-donut-pct" id="r-pct">0%</div><div class="muted small">Score</div></div>
        </div>
        <div class="q-stats">
          <div><div class="v right" id="r-correct">0</div><div class="l">Correct</div></div>
          <div><div class="v wrong" id="r-wrong">0</div><div class="l">Incorrect</div></div>
          <div><div class="v" id="r-skipped">0</div><div class="l">Skipped</div></div>
          <div><div class="v" id="r-flagged">0</div><div class="l">Flagged</div></div>
          <div><div class="v" id="r-total">0</div><div class="l">Answered</div></div>
        </div>
        <div class="row center">
          <button type="button" id="r-review">Review Answers</button>
          <button type="button" class="hidden" id="r-flagged-btn">Review Flagged</button>
          <button type="button" class="hidden" id="r-skipped-btn">Review Skipped</button>
          <button type="button" class="hidden" id="r-redo">Redo Missed</button>
          <button type="button" class="primary" id="r-again">Start Over</button>
        </div>
      </div>

      <div class="row center" style="margin-top:22px">
        <button class="hidden" id="q-share">Copy Share Link</button>
      </div>
    </div>
  </div>
</div>
<div class="hl-pop" id="hl-pop" role="toolbar" aria-label="Highlight">
  <button type="button" id="hl-add"><i class="dot"></i>Highlight</button>
  <button type="button" id="hl-del">Remove</button>
</div>
<p class="error hidden center" id="q-error" role="alert"></p>
""", script='<script type="module" src="/assets/quiz.js?v=JSVER"></script>')

# ------------------------------------------------------------------ link
page("link/index.html", "Link Anki", "Link the PDF Occlusion add-on to your account.",
     body=top("Link Anki") + f"""
<div id="step-code">
  <p class="lede">The code shown in Anki</p>
  <p class="code" id="code"></p>
</div>
<div id="link-out" class="hidden">
  <div class="row center" style="margin-top:22px"><button id="sign-in">{{G_ICON}}Sign In with Google</button></div>
  <p class="muted center" style="margin-top:14px">Your first 60 credits are free and need no card. Signing in keeps track of them.</p>
</div>
<div id="link-in" class="hidden">
  <p class="muted center" id="as" style="margin-top:18px"></p>
  <div class="row center">
    <button class="primary" id="approve">Link This Anki</button>
    <button id="switch">Use Another Account</button>
  </div>
</div>
<p class="note center hidden" id="done">Linked. You can close this tab and return to Anki.</p>
<p class="error hidden center" id="link-error" role="alert"></p>
""", script="""<script type="module">
import { watchUser, signIn, signOut, api } from "/assets/app.js";
const $ = (id) => document.getElementById(id);
const code = (new URLSearchParams(location.search).get("code") || "").toUpperCase();
$("code").textContent = code || "No code";
const err = (m) => { $("link-error").textContent = m; $("link-error").classList.remove("hidden"); };
const linked = new URLSearchParams(location.search).has("linked");
if (linked) { $("step-code").classList.add("hidden"); $("done").classList.remove("hidden"); }
else if (!code) err("Open this page from the add-on: Generate, then Sign in.");
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
page("privacy/index.html", "Privacy Policy", "Privacy policy for PDF Occlusion.",
     body=top("Privacy Policy") + f"""
<div class="prose">
  <p class="muted center" style="margin-top:14px">Effective November 21, 2026</p>

  <h2>1. Scope</h2>
  <p>This Privacy Policy describes how PDF Occlusion ("we", "us" or "our") collects, uses and discloses information in connection with this website, the PDF Occlusion add-on and the Generate service (together, the "Service"). By using the Service you acknowledge the practices described in this policy.</p>

  <h2>2. Information We Collect</h2>
  <ul>
    <li><b>Account information.</b> When you sign in, we receive your email address and an account identifier from the sign-in provider you choose.</li>
    <li><b>Submitted content.</b> When you use Generate to make boxes, cards or a quiz, the add-on transmits the text of every page of the PDF, a few page images to identify the document, images of the pages you select and the text found on them, the settings and instructions you choose, and any notes you attach ("Submitted Content"). To make them, the Service first works out what the document is and what each page teaches; those notes are part of Submitted Content.</li>
    <li><b>Usage records.</b> For each use of Generate we record the document name, the number of pages, the date and the credits consumed.</li>
    <li><b>Quizzes.</b> When you make a quiz, we keep its questions, answers and explanations, with the document name, in your account so you can take it later on any device. A quiz may also keep images of the lecture slides used in its questions. If you share a quiz, anyone with its link can view it until you change the link. Your answers to a quiz are kept in your browser and, when you are signed in, saved to your account so your progress follows you across devices.</li>
    <li><b>Installation identifiers.</b> Linking the add-on to your account creates a key stored on your device. We retain only a one-way fingerprint of that key. The add-on also sends a one-way fingerprint of your computer's hardware identifier, which we use to limit free credits to one allowance per computer; the identifier itself never leaves your computer.</li>
    <li><b>Usage statistics.</b> The add-on reports which of its buttons and features are used, page and card counts, errors, and its own, Anki's and your operating system's versions, tagged with the one-way computer fingerprint described above and, when you are signed in, your account. It does not report page images, file names, card text or anything you type. You can turn this off with the <code>usage_stats</code> setting in the add-on's config. This website records the pages you view, the links and buttons you click, whether signing in and linking worked, and the site that referred you, tagged with a random identifier stored in your browser.</li>
    <li><b>Payment information.</b> Payments are processed by a third-party payment processor. We do not receive or store full payment card numbers. We retain the customer and transaction identifiers needed to provide what you purchased.</li>
  </ul>

  <h2>3. How We Use Information</h2>
  <p>We use information to provide, operate and maintain the Service; to understand how the Service is used and improve it; to process transactions and account for credits; to authenticate users and linked installations; to detect and prevent fraud, abuse and security incidents; to communicate with you about your account; and to comply with legal obligations.</p>

  <h2>4. Submitted Content</h2>
  <p>Submitted Content is processed solely to provide the Service to you. It is not retained after your request has been completed (notes about the document are kept only while a run is in progress, at most 6 hours; quizzes made from it are kept as described in section 2), it is not sold, and it is not used to train machine learning models. You remain responsible for ensuring that you have the right to submit it.</p>

  <h2>5. Disclosure of Information</h2>
  <p>We do not sell or rent personal information. We disclose information only (a) to service providers that host, authenticate, process payments or otherwise perform services on our behalf, subject to obligations of confidentiality; (b) where required by law, regulation, legal process or governmental request; (c) to protect the rights, property or safety of the Service, its users or others; (d) in connection with a merger, acquisition or sale of assets; or (e) with your consent.</p>

  <h2>6. Retention</h2>
  <p>Account information, usage records, quizzes and quiz progress are retained for as long as your account is active. When you delete your account, they are deleted, except where retention is required by law or by our payment processor.</p>

  <h2>7. Security</h2>
  <p>We use reasonable administrative, technical and organizational measures to protect information. No method of transmission or storage is completely secure, and we cannot guarantee absolute security.</p>

  <h2>8. Your Choices and Rights</h2>
  <p>You may sign out linked installations or delete your account at any time from the <a href="/account/">account page</a>. Depending on where you live, you may have additional rights to access, correct, port, restrict or object to the processing of your personal information. To exercise them, contact us as described below.</p>

  <h2>9. Children</h2>
  <p>The Service is not directed to children under 13, and we do not knowingly collect personal information from them. If you believe a child has provided us information, contact us and we will delete it.</p>

  <h2>10. International Users</h2>
  <p>The Service is operated from the United States. By using it, you consent to the transfer and processing of your information in the United States, where data protection laws may differ from those of your country.</p>

  <h2>11. Changes</h2>
  <p>We may update this policy from time to time. Changes take effect when posted on this page with a new effective date. Your continued use of the Service after that date constitutes acceptance of the updated policy.</p>

  <h2>12. Contact</h2>
  <p>Questions about this policy may be submitted to <a href="{HELP}">pdf-occlusion-support@googlegroups.com</a>.</p>
</div>
""")

# ------------------------------------------------------------------ terms
page("terms/index.html", "Terms of Service", "Terms of service for PDF Occlusion.",
     body=top("Terms of Service") + f"""
<div class="prose">
  <p class="muted center" style="margin-top:14px">Effective November 21, 2026</p>

  <h2>1. Acceptance</h2>
  <p>These Terms of Service (the "Terms") govern your access to and use of this website, the PDF Occlusion add-on and the Generate service (together, the "Service"). By using the Service you agree to these Terms. If you do not agree, do not use the Service.</p>

  <h2>2. Eligibility</h2>
  <p>You must be at least 13 years old to use the Service, and old enough to form a binding contract where you live to make a purchase.</p>

  <h2>3. Accounts</h2>
  <p>You are responsible for your account, for keeping your sign-in and linked installations secure, and for all activity under your account. Accounts are for one person and may not be shared, sold or transferred.</p>

  <h2>4. The Add-on</h2>
  <p>The add-on's source code is licensed under the MIT License. These Terms govern the online features of the Service, including accounts, credits and Generate.</p>

  <h2>5. Credits</h2>
  <p>Generate is measured in credits. Each slide processed for boxes or cards consumes one credit; slides are counted as they are completed. Each quiz question consumes two credits once the quiz is ready. Credits have no cash value and are not transferable. Credits included with a subscription expire at the end of each monthly period. Purchased credits do not expire while your account remains active.</p>

  <h2>6. Subscriptions and Payment</h2>
  <p>Subscriptions are billed in advance and renew automatically at the end of each period until cancelled. You may cancel at any time; cancellation takes effect at the end of the current period. Except where required by law, all fees are non-refundable. We may change prices with notice, effective at your next renewal. You are responsible for applicable taxes.</p>

  <h2>7. Your Content</h2>
  <p>You retain all rights to the documents and other material you submit. You grant us a limited, non-exclusive license to process that material solely to provide the Service to you. You represent that you have all rights necessary to submit it and that doing so does not violate any law or the rights of any third party.</p>

  <h2>8. Acceptable Use</h2>
  <p>You agree not to: use the Service unlawfully or to infringe the rights of others; submit material you are not entitled to use; interfere with, overload or attempt to gain unauthorized access to the Service; circumvent usage limits or credit accounting; access the Service by automated means other than the add-on and this website; or resell or redistribute the Service.</p>

  <h2>9. Output</h2>
  <p>Boxes, cards and quizzes produced by the Service are generated automatically and may be incomplete or inaccurate. You are responsible for reviewing them before use. Nothing produced by the Service is professional, medical, legal or other advice.</p>

  <h2>10. Intellectual Property</h2>
  <p>Except for the add-on source code and your content, the Service and all related materials are owned by us and protected by law. No rights are granted other than those expressly stated in these Terms.</p>

  <h2>11. Suspension and Termination</h2>
  <p>We may suspend or terminate your access to the Service at any time if you breach these Terms or if required by law. You may stop using the Service and delete your account at any time.</p>

  <h2>12. Disclaimer of Warranties</h2>
  <p>THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE", WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, ACCURACY AND NON-INFRINGEMENT. WE DO NOT WARRANT THAT THE SERVICE WILL BE UNINTERRUPTED, ERROR-FREE OR SECURE.</p>

  <h2>13. Limitation of Liability</h2>
  <p>TO THE FULLEST EXTENT PERMITTED BY LAW, WE WILL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL OR PUNITIVE DAMAGES, OR FOR ANY LOSS OF DATA, PROFITS OR GOODWILL, ARISING FROM OR RELATED TO THE SERVICE. OUR TOTAL LIABILITY FOR ANY CLAIM WILL NOT EXCEED THE AMOUNT YOU PAID US IN THE TWELVE MONTHS BEFORE THE CLAIM AROSE.</p>

  <h2>14. Indemnification</h2>
  <p>You agree to indemnify and hold us harmless from any claims, losses and expenses, including reasonable legal fees, arising from your use of the Service, your content or your breach of these Terms.</p>

  <h2>15. General</h2>
  <p>These Terms are governed by the laws of the United States and the applicable state, without regard to conflict-of-law principles. If any provision is found unenforceable, the remainder stays in effect. Our failure to enforce a provision is not a waiver. These Terms, together with the Privacy Policy, are the entire agreement between you and us regarding the Service.</p>

  <h2>16. Changes</h2>
  <p>We may modify these Terms at any time. Changes take effect when posted on this page with a new effective date. Your continued use of the Service after that date constitutes acceptance of the modified Terms.</p>

  <h2>17. Contact</h2>
  <p>Questions about these Terms may be submitted to <a href="{HELP}">pdf-occlusion-support@googlegroups.com</a>.</p>
</div>
""")
