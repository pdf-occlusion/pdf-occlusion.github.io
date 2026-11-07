"""Write every page of the site from one template.

  python3 build.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ANKIWEB = "https://ankiweb.net/shared/info/783821131"
GITHUB = "https://github.com/pdf-occlusion/anki-pdf-occlusion"
HELP = GITHUB + "/issues"

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="pdf occlusion">
<meta property="og:description" content="An Anki add-on that turns lecture PDFs into image occlusion cards.">
<meta property="og:image" content="https://pdf-occlusion.github.io/assets/og.png">
<meta property="og:url" content="https://pdf-occlusion.github.io/">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Klee+One:wght@400;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<main>
"""

NAV = [("ankiweb", ANKIWEB, None), ("github", GITHUB, None),
       ("pricing", "/pricing/", "pricing"), ("account", "/account/", "account")]

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
    return f"""<div class="top{' small' if small else ''}">
  <a href="/" aria-label="pdf occlusion home"><img class="mark" src="/assets/logo.svg" alt=""></a>
  <h1>{name}</h1>
  <nav class="links" aria-label="Main">
    {links}
  </nav>
</div>
"""


def page(path, title, desc, body, script=""):
    body = body.replace("{G_ICON}", G_ICON)
    html = HEAD.format(title=title, desc=desc) + body + FOOT.format(script=script)
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
page("index.html", "pdf occlusion",
     "An Anki add-on that turns lecture PDFs into image occlusion cards.",
     body=top("pdf occlusion", small=False) + f"""
<div class="badges">
  <a class="badge" href="{ANKIWEB}"><span class="badge-k">add-on code</span><span class="badge-v">783821131</span></a>
  <a class="badge" href="https://apps.ankiweb.net"><span class="badge-k">anki</span><span class="badge-v">23.10+</span></a>
  <a class="badge" href="{GITHUB}/blob/main/LICENSE"><span class="badge-k">license</span><span class="badge-v">MIT</span></a>
</div>

<p class="lede">an anki add-on that turns lecture pdfs into image occlusion cards.</p>

<div class="panel demo">
  <img src="/assets/demo.gif" width="840" height="585" alt="The add-on open on a lecture: boxes drawn over key phrases, Detect boxing every label on a diagram, and the card that comes out">
</div>

<section>
  <h2>making cards</h2>
  <p>Open a lecture's slides in Anki and drag a box over anything you want to learn, or drag over a whole diagram and let Detect box every label in it. Group boxes that belong together, attach the notes PDF, and create every card at once. Each card shows its own slide, with the notes and slides a click away.</p>
</section>

<section>
  <h2>auto-occlude</h2>
  <p>For lecture-heavy weeks, Auto-occlude does the first pass for you. Claude reads each slide and boxes what is worth learning; you look it over, change what you want, and make the cards.</p>
  <p>You decide how it occludes: every diagram label or only the ones the lecture is about, key phrases or whole bullets, numbers and doses, bold or red text, tables by cell or row, flowcharts step by step, which slides to skip, and your own instructions in plain words. The add-on remembers your choices for every lecture.</p>
  <p>The add-on is free. Your first lecture with Auto-occlude is too, and after that it is <a href="/pricing/">$14.99 a month</a> for 60 lectures.</p>
</section>
""")

# ------------------------------------------------------------------ pricing
page("pricing/index.html", "pricing, pdf occlusion",
     "The add-on is free. Auto-occlude: one free lecture, then $14.99 a month for 60 lectures, or 10 lectures for $4.99.",
     body=top("pricing", "pricing") + f"""
<p class="lede">the add-on is free. these are for auto-occlude, where one lecture is one pdf of up to 150 slides.</p>

<div class="panel" style="margin-top:30px">
  <ul class="plain price-list">
    <li>
      <div><div class="name">first lecture</div><div class="what">to see how it does on your slides</div></div>
      <div class="amount">free</div>
    </li>
    <li>
      <div><div class="name">monthly</div><div class="what">60 lectures a month, about 15 a week</div></div>
      <div class="row" style="margin:0"><span class="amount">$14.99</span><button class="primary" data-buy="monthly">subscribe</button></div>
    </li>
    <li>
      <div><div class="name">yearly</div><div class="what">the same, two months cheaper</div></div>
      <div class="row" style="margin:0"><span class="amount">$149.90</span><button data-buy="yearly">subscribe</button></div>
    </li>
    <li>
      <div><div class="name">10 lectures</div><div class="what">no expiry, used after a plan's lectures run out</div></div>
      <div class="row" style="margin:0"><span class="amount">$4.99</span><button data-buy="pack10">buy</button></div>
    </li>
  </ul>
</div>
<p class="error hidden center" id="buy-error" role="alert"></p>

<section>
  <h2>good to know</h2>
  <ul class="dots">
    <li>Boxing by hand, Detect and cloze cards are always free.</li>
    <li>A plan's lectures reset each month. Cancel any time from your account; it runs to the end of what you paid for.</li>
    <li>Payments go through Stripe. Slides are not kept after they are occluded; the <a href="/privacy/">privacy page</a> has the details.</li>
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
page("account/index.html", "account, pdf occlusion", "Your lectures, plan and linked Anki installs.",
     body=top("account", "account") + f"""
<div id="signed-out" class="hidden">
  <p class="lede">sign in to see your lectures and link the add-on.</p>
  <div class="row center" style="margin-top:22px"><button id="sign-in">{{G_ICON}}sign in with google</button></div>
</div>

<div id="signed-in" class="hidden">
  <p class="lede" id="who"></p>
  <p class="note center hidden" id="paid"></p>

  <div class="panel" style="margin-top:26px">
    <div class="left" id="left">0</div>
    <div class="muted" id="left-note">lectures left</div>
    <dl class="kv">
      <dt>plan</dt><dd id="plan">none</dd>
      <dt>this month</dt><dd id="month"></dd>
      <dt>packs</dt><dd id="packs"></dd>
    </dl>
    <div class="row">
      <a class="btn primary" href="/pricing/" id="upgrade">see pricing</a>
      <button id="pack">buy 10 lectures</button>
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
    <h3>recent lectures</h3>
    <ul class="plain list" id="jobs"></ul>
    <p class="muted small hidden" id="no-jobs">nothing occluded yet</p>
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
  $("paid").textContent = paid === "pack10" ? "thanks, 10 lectures were added." : "thanks, your plan is active.";
  $("paid").classList.remove("hidden");
}
async function load() {
  const me = await api("/v1/me", { user });
  $("who").textContent = me.email || "";
  $("left").textContent = me.lectures_left;
  $("left-note").textContent = me.lectures_left === 1 ? "lecture left" : "lectures left";
  $("plan").textContent = me.plan === "yearly" ? "yearly" : me.plan === "monthly" ? "monthly" : me.free_left ? "free lecture unused" : "none";
  $("month").textContent = me.plan ? `${me.plan_used} of ${me.plan_allowance} used` : "no plan";
  $("packs").textContent = me.pack_credits ? `${me.pack_credits} left` : "none";
  $("upgrade").classList.toggle("hidden", !!me.plan);
  $("billing").classList.toggle("hidden", !me.plan && !me.pack_credits && !paid);
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
    li.children[0].textContent = j.lecture || "Untitled lecture";
    li.children[1].textContent = `${j.slides_total} slides, ${when(j.created_at)}`;
    jobs.append(li);
  }
  $("no-jobs").classList.toggle("hidden", me.jobs.length > 0);
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
$("pack").addEventListener("click", () => go("/v1/checkout", { product: "pack10" }));
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

# ------------------------------------------------------------------ link
page("link/index.html", "link anki, pdf occlusion", "Link the PDF Occlusion add-on to your account.",
     body=top("link anki") + f"""
<div id="step-code">
  <p class="lede">the code anki is showing</p>
  <p class="code" id="code"></p>
</div>
<div id="link-out" class="hidden">
  <div class="row center" style="margin-top:22px"><button id="sign-in">{{G_ICON}}sign in with google</button></div>
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
if (!code) err("Open this page from the add-on: Auto-occlude, then Sign in.");
let user = null;
watchUser((u) => {
  user = u;
  $("link-out").classList.toggle("hidden", !!u || !code);
  $("link-in").classList.toggle("hidden", !u || !code);
  if (u) $("as").textContent = u.email;
});
$("sign-in").addEventListener("click", () => signIn().catch((e) => err(e.message)));
$("switch").addEventListener("click", async () => { await signOut(); await signIn().catch((e) => err(e.message)); });
$("approve").addEventListener("click", async () => {
  $("approve").disabled = true;
  try {
    await api("/v1/link/approve", { method: "POST", body: { code }, user });
    $("link-in").classList.add("hidden"); $("step-code").classList.add("hidden"); $("done").classList.remove("hidden");
  } catch (e) { err(e.message); $("approve").disabled = false; }
});
</script>""")

# ------------------------------------------------------------------ privacy
page("privacy/index.html", "privacy, pdf occlusion", "What PDF Occlusion collects and why.",
     body=top("privacy") + """
<div class="prose">
  <p class="muted center" style="margin-top:14px">last updated november 7, 2026</p>
  <h2>the add-on</h2>
  <p>The add-on runs inside Anki on your computer. It reads your PDFs, draws boxes and makes cards locally. Without Auto-occlude it sends nothing anywhere.</p>
  <h2>auto-occlude</h2>
  <p>When you run Auto-occlude, the add-on sends the slides you chose to our server: an image of each slide, the text found on it with its position, the lecture's name, the settings you picked and, if you attached one, the text of the lecture notes. The server passes them to Anthropic's Claude model, which decides where the boxes go, and returns the result to the add-on.</p>
  <ul>
    <li>We do not store slide images, slide text or notes. They exist on our server only while the request is being handled.</li>
    <li>Anthropic processes them under its commercial terms, which do not allow using them to train its models.</li>
    <li>For each run we keep the lecture's name, the number of slides and the amount of model use, so you can see your history and we can count credits.</li>
  </ul>
  <h2>your account</h2>
  <p>You sign in with Google through Firebase Authentication. We keep your email address and a Google account identifier. Linking the add-on stores a random key on your computer; we keep only a fingerprint of it, and you can sign out every install from your account page.</p>
  <h2>payments</h2>
  <p>Payments are handled by Stripe. We never see your card number. We keep the Stripe customer and subscription identifiers needed to give you the lectures you paid for.</p>
  <h2>deleting your data</h2>
  <p>Delete your account from the <a href="/account/">account page</a>. That removes your account, your linked installs and your history right away, and cancels any plan. Stripe keeps its own payment records as the law requires.</p>
</div>
""")

# ------------------------------------------------------------------ terms
page("terms/index.html", "terms, pdf occlusion", "The terms for using PDF Occlusion's Auto-occlude service.",
     body=top("terms") + f"""
<div class="prose">
  <p class="muted center" style="margin-top:14px">last updated november 7, 2026</p>
  <h2>what you get</h2>
  <p>Auto-occlude places occlusion boxes on your lecture slides as a first draft. It can miss things or box things you would not have. Check every slide before you create cards.</p>
  <h2>your material</h2>
  <p>Only send slides you are allowed to use for your own study. You keep every right to your slides and cards.</p>
  <h2>credits and plans</h2>
  <ul>
    <li>One run of Auto-occlude on one lecture, up to 150 slides, uses one credit.</li>
    <li>Plan lectures reset each month and do not carry over. Lecture packs do not expire.</li>
    <li>A run that fails before any boxes come back can be retried. If a credit was used without a result, report it on the <a href="{HELP}">help page</a>.</li>
    <li>You can cancel a plan at any time. It stays active until the end of the period already paid.</li>
  </ul>
  <h2>fair use</h2>
  <p>Auto-occlude is for occluding lecture slides. Using it for anything else, or sharing an account, can end your access.</p>
  <h2>changes</h2>
  <p>If these terms or the prices change, we will say so on this site before the change applies to you.</p>
</div>
""")
