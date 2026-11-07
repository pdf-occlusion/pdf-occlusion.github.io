"""Write the site's inner pages from one header and footer.

  python3 build.py

index.html is written by hand; everything else comes from here.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="PDF Occlusion">
<meta property="og:description" content="Lecture PDFs into Anki image occlusion cards. A whole lecture, occluded in a minute.">
<meta property="og:image" content="https://pdf-occlusion.github.io/assets/og.png">
<meta property="og:url" content="https://pdf-occlusion.github.io/">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
{extra_head}</head>
<body>
<header class="site-head">
  <div class="wrap">
    <a class="brand" href="/"><img src="/assets/logo.svg" alt="" width="26" height="26">PDF Occlusion</a>
    <nav class="nav" aria-label="Main">
      <a class="hide-s" href="/#how">How it works</a>
      <a href="/pricing/"{cur_pricing}>Pricing</a>
      <a href="/account/"{cur_account}>Account</a>
      <a class="btn btn-primary btn-small" href="https://ankiweb.net/shared/info/783821131">Get the add-on</a>
    </nav>
  </div>
</header>
"""

FOOT = """
<footer class="site-foot">
  <div class="wrap">
    <span>&copy; <span data-year></span> PDF Occlusion</span>
    <nav aria-label="Footer">
      <a href="/pricing/">Pricing</a>
      <a href="/account/">Account</a>
      <a href="/privacy/">Privacy</a>
      <a href="/terms/">Terms</a>
      <a href="https://github.com/pdf-occlusion/anki-pdf-occlusion">Source</a>
      <a href="mailto:ravi14.bandaru@gmail.com">Contact</a>
    </nav>
  </div>
</footer>
{script}
</body>
</html>
"""


def page(path, title, desc, body, script="", current=None, extra_head=""):
    html = HEAD.format(
        title=title, desc=desc, extra_head=extra_head,
        cur_pricing=' aria-current="page"' if current == "pricing" else "",
        cur_account=' aria-current="page"' if current == "account" else "",
    ) + body + FOOT.format(script=script)
    out = os.path.join(HERE, path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", path)


G_ICON = ('<svg class="g-icon" viewBox="0 0 18 18" aria-hidden="true"><path fill="#4285F4" d="M17.64 9.2c0-.64-.06-1.25-.16-1.84H9v3.48h4.84a4.14 4.14 0 0 1-1.8 2.72v2.26h2.92c1.7-1.57 2.68-3.88 2.68-6.62z"/>'
          '<path fill="#34A853" d="M9 18c2.43 0 4.47-.8 5.96-2.18l-2.92-2.26c-.8.54-1.84.86-3.04.86-2.34 0-4.32-1.58-5.03-3.7H.96v2.33A9 9 0 0 0 9 18z"/>'
          '<path fill="#FBBC05" d="M3.97 10.72A5.4 5.4 0 0 1 3.68 9c0-.6.1-1.18.29-1.72V4.95H.96A9 9 0 0 0 0 9c0 1.45.35 2.83.96 4.05l3.01-2.33z"/>'
          '<path fill="#EA4335" d="M9 3.58c1.32 0 2.5.45 3.44 1.35l2.58-2.58A9 9 0 0 0 .96 4.95l3.01 2.33C4.68 5.16 6.66 3.58 9 3.58z"/></svg>')

# ------------------------------------------------------------------ pricing
page("pricing/index.html", "Pricing, PDF Occlusion",
     "One free lecture, then a monthly plan for about 15 lectures a week, or lecture packs that never expire.",
     current="pricing", body=f"""
<main class="app">
  <div class="wrap">
    <h1>Pricing</h1>
    <p class="lede" style="margin-top:1rem">Your first lecture is free. After that, one auto-occluded lecture uses one credit, however many slides it has.</p>

    <div class="plans" style="margin-top:2.6rem">
      <article class="plan featured">
        <h3>Semester plan</h3>
        <div class="billing-switch" role="group" aria-label="Billing period">
          <button type="button" data-period="monthly" aria-pressed="true">Monthly</button>
          <button type="button" data-period="yearly" aria-pressed="false">Yearly</button>
        </div>
        <div class="price"><strong id="plan-price">$14.99</strong><span class="per" id="plan-per">a month</span></div>
        <p class="what">60 lectures every month, about 15 a week. Enough for a full block of daily lectures.</p>
        <ul>
          <li>Every setting, including your own instructions</li>
          <li>Uses the lecture notes when you attach them</li>
          <li>Unused lectures reset each month</li>
          <li id="plan-note">Cancel any time</li>
        </ul>
        <button class="btn btn-primary" data-buy="monthly" id="buy-plan">Choose monthly</button>
      </article>

      <article class="plan">
        <h3>Lecture pack</h3>
        <div class="price"><strong>$4.99</strong><span class="per">once</span></div>
        <p class="what">10 lectures to use whenever you like. Good for a lighter block, or on top of the plan in a heavy week.</p>
        <ul>
          <li>Never expire</li>
          <li>Stack as many as you need</li>
          <li>Same settings as the plan</li>
        </ul>
        <button class="btn btn-quiet" data-buy="pack10">Buy 10 lectures</button>
      </article>

      <article class="plan">
        <h3>Free</h3>
        <div class="price"><strong>$0</strong></div>
        <p class="what">The add-on itself, and one auto-occluded lecture to see how it does on your slides.</p>
        <ul>
          <li>Manual occlusion, always free</li>
          <li>Cloze cards from text slides</li>
          <li>1 auto-occluded lecture</li>
        </ul>
        <a class="btn btn-quiet" href="https://ankiweb.net/shared/info/783821131">Get the add-on</a>
      </article>
    </div>

    <div class="notice error hidden" id="buy-error" role="alert"></div>

    <section class="faq" style="padding:4rem 0 0">
      <h2 style="font-size:1.8rem;margin-bottom:1.4rem">Questions</h2>
      <details><summary>What counts as one lecture?</summary><p>One run of Auto-occlude on one PDF, up to 150 slides. Running it again on the same lecture later uses another credit.</p></details>
      <details><summary>What if I go over 60 in a month?</summary><p>Lecture packs top up the plan. They are used only after the month's 60 are gone, and whatever is left carries over.</p></details>
      <details><summary>Do I need the plan to occlude by hand?</summary><p>No. Drawing boxes, grouping, cloze cards and everything else in the add-on stay free. Credits are only for Auto-occlude.</p></details>
      <details><summary>What happens to my slides?</summary><p>They are sent to the model that places the boxes and are not stored afterwards. Your cards are made in your own Anki collection. The <a href="/privacy/">privacy page</a> has the details.</p></details>
      <details><summary>Can I cancel?</summary><p>Yes, from your account page, at any time. The plan runs to the end of the period you paid for.</p></details>
    </section>
  </div>
</main>
""", script="""<script type="module">
import { watchUser, signIn, api } from "/assets/app.js";
let user = null;
watchUser((u) => { user = u; });
const price = document.getElementById("plan-price"), per = document.getElementById("plan-per");
const note = document.getElementById("plan-note"), buyPlan = document.getElementById("buy-plan");
for (const b of document.querySelectorAll(".billing-switch button")) {
  b.addEventListener("click", () => {
    for (const x of document.querySelectorAll(".billing-switch button")) x.setAttribute("aria-pressed", String(x === b));
    const yearly = b.dataset.period === "yearly";
    price.textContent = yearly ? "$149.90" : "$14.99";
    per.textContent = yearly ? "a year" : "a month";
    note.textContent = yearly ? "Two months free compared with monthly" : "Cancel any time";
    buyPlan.dataset.buy = yearly ? "yearly" : "monthly";
    buyPlan.textContent = yearly ? "Choose yearly" : "Choose monthly";
  });
}
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
page("account/index.html", "Account, PDF Occlusion", "Your lectures, plan and linked Anki installs.",
     current="account", body=f"""
<main class="app">
  <div class="wrap">
    <h1>Account</h1>

    <div id="signed-out" class="hidden">
      <p class="lede" style="margin-top:1rem">Sign in to see your lectures and plan, and to link the add-on.</p>
      <div class="signin"><button class="btn btn-quiet" id="sign-in">{G_ICON}Sign in with Google</button></div>
    </div>

    <div id="signed-in" class="hidden">
      <p class="lede" style="margin-top:.8rem" id="who"></p>
      <div class="notice hidden" id="paid"></div>
      <div class="account-grid">
        <div class="card">
          <h3>Lectures left</h3>
          <div class="balance" style="margin-top:.8rem"><strong id="left">0</strong><span class="muted" id="left-note"></span></div>
          <div class="meter hidden" id="meter"><span id="meter-fill" style="width:0"></span></div>
          <dl class="kv">
            <dt>Plan</dt><dd id="plan">Free</dd>
            <dt>This month</dt><dd id="month"></dd>
            <dt>Packs</dt><dd id="packs"></dd>
          </dl>
          <div class="actions-row">
            <a class="btn btn-primary" href="/pricing/" id="upgrade">See plans</a>
            <button class="btn btn-quiet" id="pack">Buy 10 lectures</button>
            <button class="btn btn-quiet hidden" id="billing">Manage billing</button>
          </div>
        </div>
        <div class="card">
          <h3>Anki installs</h3>
          <ul class="list" id="devices"></ul>
          <p class="muted small hidden" id="no-devices" style="margin-top:.8rem">None linked yet.</p>
          <div class="actions-row"><button class="btn btn-quiet btn-small hidden" id="unlink">Sign out of all installs</button></div>
        </div>
      </div>
      <div class="card" style="margin-top:1.2rem">
        <h3>Recent lectures</h3>
        <ul class="list" id="jobs"></ul>
        <p class="muted small hidden" id="no-jobs" style="margin-top:.8rem">Nothing occluded yet.</p>
      </div>
      <div class="actions-row"><button class="btn btn-quiet btn-small" id="sign-out">Sign out</button></div>
      <div class="notice error hidden" id="acct-error" role="alert"></div>
    </div>
  </div>
</main>
""", script="""<script type="module">
import { watchUser, signIn, signOut, api, when } from "/assets/app.js";
const $ = (id) => document.getElementById(id);
let user = null;
const err = (m) => { $("acct-error").textContent = m; $("acct-error").classList.remove("hidden"); };
$("sign-in").addEventListener("click", () => signIn().catch((e) => err(e.message)));
$("sign-out").addEventListener("click", () => signOut());
const paid = new URLSearchParams(location.search).get("paid");
if (paid) {
  $("paid").textContent = paid === "pack10" ? "Thanks. 10 lectures were added." : "Thanks. Your plan is active.";
  $("paid").classList.remove("hidden");
}
async function load() {
  const me = await api("/v1/me", { user });
  $("who").textContent = me.email ? `Signed in as ${me.email}` : "";
  $("left").textContent = me.lectures_left;
  $("left-note").textContent = me.lectures_left === 1 ? "lecture" : "lectures";
  $("plan").textContent = me.plan === "yearly" ? "Yearly" : me.plan === "monthly" ? "Monthly" : me.free_left ? "Free, first lecture unused" : "Free";
  $("month").textContent = me.plan ? `${me.plan_used} of ${me.plan_allowance} used` : "No plan";
  $("packs").textContent = me.pack_credits ? `${me.pack_credits} left` : "None";
  if (me.plan) {
    $("meter").classList.remove("hidden");
    $("meter-fill").style.width = `${Math.min(100, (100 * me.plan_used) / me.plan_allowance)}%`;
    $("upgrade").classList.add("hidden");
  }
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
$("unlink").addEventListener("click", async () => {
  try { await api("/v1/devices/sign-out", { method: "POST", user }); await load(); } catch (e) { err(e.message); }
});
</script>""")

# ------------------------------------------------------------------ link
page("link/index.html", "Link Anki, PDF Occlusion", "Link the PDF Occlusion add-on to your account.",
     body=f"""
<main class="app">
  <div class="wrap" style="max-width:40rem">
    <h1>Link Anki</h1>
    <div id="step-code">
      <p class="lede" style="margin-top:1rem">Check that this matches the code showing in Anki.</p>
      <p class="code-big" id="code"></p>
    </div>
    <div id="link-out" class="hidden" style="margin-top:1.6rem">
      <div class="signin" style="margin-top:0"><button class="btn btn-quiet" id="sign-in">{G_ICON}Sign in with Google</button></div>
    </div>
    <div id="link-in" class="hidden" style="margin-top:1.6rem">
      <p class="muted" id="as"></p>
      <div class="actions-row"><button class="btn btn-primary" id="approve">Link this Anki</button>
      <button class="btn btn-quiet" id="switch">Use another account</button></div>
    </div>
    <div id="done" class="hidden" style="margin-top:1.6rem">
      <div class="notice">Linked. You can close this tab and go back to Anki.</div>
    </div>
    <div class="notice error hidden" id="link-error" role="alert"></div>
  </div>
</main>
""", script="""<script type="module">
import { watchUser, signIn, signOut, api } from "/assets/app.js";
const $ = (id) => document.getElementById(id);
const code = (new URLSearchParams(location.search).get("code") || "").toUpperCase();
$("code").textContent = code || "No code";
const err = (m) => { $("link-error").textContent = m; $("link-error").classList.remove("hidden"); };
if (!code) err("Open this page from the add-on: Auto-occlude, then Sign in.");
let user = null;
watchUser((u) => {
  user = u;
  $("link-out").classList.toggle("hidden", !!u || !code);
  $("link-in").classList.toggle("hidden", !u || !code);
  if (u) $("as").textContent = `Signed in as ${u.email}`;
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
page("privacy/index.html", "Privacy, PDF Occlusion", "What PDF Occlusion collects and why.", body="""
<main class="app">
  <div class="wrap prose">
    <h1>Privacy</h1>
    <p class="muted">Last updated November 7, 2026</p>
    <h2>The add-on</h2>
    <p>The add-on runs inside Anki on your computer. It reads your PDFs, draws boxes and makes cards locally. Without Auto-occlude it sends nothing anywhere.</p>
    <h2>Auto-occlude</h2>
    <p>When you run Auto-occlude, the add-on sends the slides you chose to our server: an image of each slide, the text found on it with its position, the lecture's name, the settings you picked and, if you attached one, the text of the lecture notes. The server passes them to Anthropic's Claude model, which decides where the boxes go, and returns the result to the add-on.</p>
    <ul>
      <li>We do not store slide images, slide text or notes. They exist on our server only while the request is being handled.</li>
      <li>Anthropic processes them under its commercial terms, which do not allow using them to train its models.</li>
      <li>For each run we keep the lecture's name, the number of slides and the amount of model use, so you can see your history and we can count credits.</li>
    </ul>
    <h2>Your account</h2>
    <p>You sign in with Google through Firebase Authentication. We keep your email address and a Google account identifier. Linking the add-on stores a random key on your computer; we keep only a fingerprint of it, and you can sign out every install from your account page.</p>
    <h2>Payments</h2>
    <p>Payments are handled by Stripe. We never see your card number. We keep the Stripe customer and subscription identifiers needed to give you the lectures you paid for.</p>
    <h2>Deleting your data</h2>
    <p>Ask through the Contact link below and we will delete your account and its history.</p>
  </div>
</main>
""")

page("terms/index.html", "Terms, PDF Occlusion", "The terms for using PDF Occlusion's Auto-occlude service.", body="""
<main class="app">
  <div class="wrap prose">
    <h1>Terms</h1>
    <p class="muted">Last updated November 7, 2026</p>
    <h2>What you get</h2>
    <p>Auto-occlude places occlusion boxes on your lecture slides as a first draft. It can miss things or box things you would not have. Check every slide before you create cards.</p>
    <h2>Your material</h2>
    <p>Only send slides you are allowed to use for your own study. You keep every right to your slides and cards.</p>
    <h2>Credits and plans</h2>
    <ul>
      <li>One run of Auto-occlude on one lecture, up to 150 slides, uses one credit.</li>
      <li>Plan lectures reset each month and do not carry over. Lecture packs do not expire.</li>
      <li>A run that fails before any boxes come back can be retried; email us if a credit was used without a result.</li>
      <li>You can cancel a plan at any time. It stays active until the end of the period already paid.</li>
    </ul>
    <h2>Fair use</h2>
    <p>Auto-occlude is for occluding lecture slides. Using it for anything else, or sharing an account, can end your access.</p>
    <h2>Changes</h2>
    <p>If these terms or the prices change, we will say so on this site before the change applies to you.</p>
    <p>Questions: <a href="mailto:ravi14.bandaru@gmail.com">ravi14.bandaru@gmail.com</a></p>
  </div>
</main>
""")
