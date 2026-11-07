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
<meta property="og:description" content="An Anki add-on that turns lecture PDFs into image occlusion cards.">
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

NAV = [("pricing", "/pricing/", "pricing"), ("account", "/account/", "account")]

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
    html = HEAD.format(title=title, desc=desc).replace("CSSVER", css_v) + body + FOOT.format(script=script)
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
  <div><div class="amount">free</div><div class="what">your first pdf</div></div>
  <div><div class="amount">$14.99</div><div class="what">a month for 60 pdfs</div></div>
  <div><div class="amount">$4.99</div><div class="what">10 pdfs, no expiry</div></div>
</div>"""

page("index.html", "pdf occlusion",
     "Auto-occlude boxes every label, term and key phrase in a PDF for you, inside Anki. Your first PDF is free.",
     body=top("pdf occlusion", small=False) + f"""
<div class="badges">
  <span class="badge"><span class="badge-k">add-on code</span><span class="badge-v">783821131</span></span>
  <span class="badge"><span class="badge-k">anki</span><span class="badge-v">23.10+</span></span>
  <span class="badge"><span class="badge-k">license</span><span class="badge-v">MIT</span></span>
</div>

<p class="lede">press auto-occlude and every label, term and key phrase in your pdf is boxed for you. check it over, then make the cards.</p>

<div style="margin-top:26px">{PRICES}</div>

<div class="panel demo">
  <img src="/assets/demo.gif" width="840" height="585" alt="PDF Occlusion open in Anki with boxes placed over the labels of an anatomy diagram">
</div>

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
     "Your first PDF is free. Then $14.99 a month for 60 PDFs, $149.90 a year, or 10 PDFs for $4.99.",
     body=top("pricing", "pricing") + f"""
<p class="lede">one pdf of up to 150 pages is one use of auto-occlude. the add-on itself is free.</p>

<div class="panel" style="margin-top:30px">
  <ul class="plain price-list">
    <li>
      <div><div class="name">first pdf</div><div class="what">on us</div></div>
      <div class="amount">free</div>
    </li>
    <li>
      <div><div class="name">monthly</div><div class="what">60 pdfs a month</div></div>
      <div class="row" style="margin:0"><span class="amount">$14.99</span><button class="primary" data-buy="monthly">subscribe</button></div>
    </li>
    <li>
      <div><div class="name">yearly</div><div class="what">60 pdfs a month, two months cheaper</div></div>
      <div class="row" style="margin:0"><span class="amount">$149.90</span><button data-buy="yearly">subscribe</button></div>
    </li>
    <li>
      <div><div class="name">10 pdfs</div><div class="what">no expiry</div></div>
      <div class="row" style="margin:0"><span class="amount">$4.99</span><button data-buy="pack10">buy</button></div>
    </li>
  </ul>
</div>
<p class="error hidden center" id="buy-error" role="alert"></p>

<section>
  <ul class="dots">
    <li>A plan's pdfs reset each month. Packs are used once they run out.</li>
    <li>Cancel any time from your account. The plan runs to the end of what you paid for.</li>
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
page("account/index.html", "account", "Your PDFs, plan and linked Anki installs.",
     body=top("account", "account") + f"""
<div id="signed-out" class="hidden">
  <p class="lede">sign in to see your plan and link the add-on.</p>
  <div class="row center" style="margin-top:22px"><button id="sign-in">{{G_ICON}}sign in with google</button></div>
</div>

<div id="signed-in" class="hidden">
  <p class="lede" id="who"></p>
  <p class="note center hidden" id="paid"></p>

  <div class="panel" style="margin-top:26px">
    <div class="left" id="left">0</div>
    <div class="muted" id="left-note">pdfs left</div>
    <dl class="kv">
      <dt>plan</dt><dd id="plan">none</dd>
      <dt>this month</dt><dd id="month"></dd>
      <dt>extra pdfs</dt><dd id="packs"></dd>
    </dl>
    <div class="row">
      <a class="btn primary" href="/pricing/" id="upgrade">see pricing</a>
      <button id="pack">buy 10 pdfs</button>
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
  $("paid").textContent = paid === "pack10" ? "thanks, 10 pdfs were added." : "thanks, your plan is active.";
  $("paid").classList.remove("hidden");
}
async function load() {
  const me = await api("/v1/me", { user });
  $("who").textContent = me.email || "";
  $("left").textContent = me.lectures_left;
  $("left-note").textContent = me.lectures_left === 1 ? "pdf left" : "pdfs left";
  $("plan").textContent = me.plan === "yearly" ? "yearly" : me.plan === "monthly" ? "monthly" : me.free_left ? "free pdf unused" : "none";
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
    li.children[0].textContent = j.lecture || "Untitled pdf";
    li.children[1].textContent = `${j.slides_total} pages, ${when(j.created_at)}`;
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
page("link/index.html", "link anki", "Link the PDF Occlusion add-on to your account.",
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
page("privacy/index.html", "privacy", "Privacy policy for PDF Occlusion.",
     body=top("privacy") + f"""
<div class="prose">
  <p class="muted center" style="margin-top:14px">effective november 7, 2026</p>

  <h2>1. scope</h2>
  <p>This Privacy Policy describes how PDF Occlusion ("we", "us" or "our") collects, uses and discloses information in connection with this website, the PDF Occlusion add-on and the Auto-occlude service (together, the "Service"). By using the Service you acknowledge the practices described in this policy.</p>

  <h2>2. information we collect</h2>
  <ul>
    <li><b>Account information.</b> When you sign in, we receive your email address and an account identifier from the sign-in provider you choose.</li>
    <li><b>Submitted content.</b> When you use Auto-occlude, the add-on transmits images of the pages you select, the text found on them, the settings you choose and any notes you attach ("Submitted Content").</li>
    <li><b>Usage records.</b> For each use of Auto-occlude we record the document name, the number of pages, the date and the credits consumed.</li>
    <li><b>Installation identifiers.</b> Linking the add-on to your account creates a key stored on your device. We retain only a one-way fingerprint of that key.</li>
    <li><b>Payment information.</b> Payments are processed by a third-party payment processor. We do not receive or store full payment card numbers. We retain the customer and transaction identifiers needed to provide what you purchased.</li>
  </ul>

  <h2>3. how we use information</h2>
  <p>We use information to provide, operate and maintain the Service; to process transactions and account for credits; to authenticate users and linked installations; to detect and prevent fraud, abuse and security incidents; to communicate with you about your account; and to comply with legal obligations.</p>

  <h2>4. submitted content</h2>
  <p>Submitted Content is processed solely to provide the Service to you. It is not retained after your request has been completed, it is not sold, and it is not used to train machine learning models. You remain responsible for ensuring that you have the right to submit it.</p>

  <h2>5. disclosure of information</h2>
  <p>We do not sell or rent personal information. We disclose information only (a) to service providers that host, authenticate, process payments or otherwise perform services on our behalf, subject to obligations of confidentiality; (b) where required by law, regulation, legal process or governmental request; (c) to protect the rights, property or safety of the Service, its users or others; (d) in connection with a merger, acquisition or sale of assets; or (e) with your consent.</p>

  <h2>6. retention</h2>
  <p>Account information and usage records are retained for as long as your account is active. When you delete your account, they are deleted, except where retention is required by law or by our payment processor.</p>

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
  <p class="muted center" style="margin-top:14px">effective november 7, 2026</p>

  <h2>1. acceptance</h2>
  <p>These Terms of Service (the "Terms") govern your access to and use of this website, the PDF Occlusion add-on and the Auto-occlude service (together, the "Service"). By using the Service you agree to these Terms. If you do not agree, do not use the Service.</p>

  <h2>2. eligibility</h2>
  <p>You must be at least 13 years old to use the Service, and old enough to form a binding contract where you live to make a purchase.</p>

  <h2>3. accounts</h2>
  <p>You are responsible for your account, for keeping your sign-in and linked installations secure, and for all activity under your account. Accounts are for one person and may not be shared, sold or transferred.</p>

  <h2>4. the add-on</h2>
  <p>The add-on's source code is licensed under the MIT License. These Terms govern the online features of the Service, including accounts, credits and Auto-occlude.</p>

  <h2>5. credits</h2>
  <p>Each use of Auto-occlude on one document of up to 150 pages consumes one credit. Credits have no cash value and are not transferable. Credits included with a subscription expire at the end of each monthly period. Purchased credit packs do not expire while your account remains active.</p>

  <h2>6. subscriptions and payment</h2>
  <p>Subscriptions are billed in advance and renew automatically at the end of each period until cancelled. You may cancel at any time; cancellation takes effect at the end of the current period. Except where required by law, all fees are non-refundable. We may change prices with notice, effective at your next renewal. You are responsible for applicable taxes.</p>

  <h2>7. your content</h2>
  <p>You retain all rights to the documents and other material you submit. You grant us a limited, non-exclusive license to process that material solely to provide the Service to you. You represent that you have all rights necessary to submit it and that doing so does not violate any law or the rights of any third party.</p>

  <h2>8. acceptable use</h2>
  <p>You agree not to: use the Service unlawfully or to infringe the rights of others; submit material you are not entitled to use; interfere with, overload or attempt to gain unauthorized access to the Service; circumvent usage limits or credit accounting; access the Service by automated means other than the add-on; or resell or redistribute the Service.</p>

  <h2>9. output</h2>
  <p>Occlusions produced by the Service are generated automatically and may be incomplete or inaccurate. You are responsible for reviewing them before use. Nothing produced by the Service is professional, medical, legal or other advice.</p>

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
