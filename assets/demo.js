// The live slide: an original schematic of the internal iliac artery, occluded
// the way the add-on does it. Masks are measured from the rendered text.

const NS = "http://www.w3.org/2000/svg";

// [id, text, x, y, anchor, relevant-to-the-lecture]
const LABELS = [
  ["common", "Common iliac a.", 586, 92, "start", false],
  ["external", "External iliac a.", 760, 470, "start", false],
  ["internal", "Internal iliac a.", 548, 214, "start", true],
  ["posterior", "Posterior division", 300, 238, "end", false],
  ["anterior", "Anterior division", 562, 262, "start", false],
  ["iliolumbar", "Iliolumbar a.", 318, 172, "end", true],
  ["latsacral", "Lateral sacral a.", 288, 310, "end", true],
  ["supgluteal", "Superior gluteal a.", 334, 380, "end", true],
  ["umbilical", "Umbilical a.", 664, 316, "start", true],
  ["obturator", "Obturator a.", 404, 432, "end", true],
  ["infvesical", "Inferior vesical a.", 664, 378, "start", true],
  ["midrectal", "Middle rectal a.", 650, 436, "start", true],
  ["infgluteal", "Inferior gluteal a.", 424, 486, "end", true],
  ["intpudendal", "Internal pudendal a.", 460, 548, "end", true],
];

const VESSELS = [
  // [d, width]
  ["M560 70 L560 150", 16],
  ["M560 150 C620 230 700 300 740 380 S770 520 784 580", 12],
  ["M560 150 C548 180 540 200 528 232", 11],
  ["M528 232 C480 236 440 236 404 232", 8],
  ["M404 232 C380 210 352 190 326 172", 5],
  ["M404 232 C380 260 330 290 296 304", 5],
  ["M404 232 C400 290 380 340 344 374", 6],
  ["M528 232 C534 320 540 420 544 540", 9],
  ["M532 300 C580 306 620 312 656 312", 5],
  ["M536 360 C500 380 460 410 414 428", 5],
  ["M538 372 C590 374 630 374 656 374", 5],
  ["M541 430 C580 432 620 432 642 432", 4],
  ["M542 470 C500 476 470 480 432 482", 6],
  ["M544 540 C520 544 500 546 470 546", 5],
];

const BULLETS = [
  // [lead, key phrase, rest, x, y]
  ["Supplies the ", "pelvic viscera, perineum", " and buttock", 40, 600],
  ["Its anterior division mostly ", "supplies viscera", "", 40, 630],
];

function el(name, attrs = {}, text) {
  const e = document.createElementNS(NS, name);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  if (text != null) e.textContent = text;
  return e;
}

export function mountSlide(host, { intro = true } = {}) {
  const svg = el("svg", { viewBox: "0 0 960 650", role: "img",
    "aria-label": "A lecture slide titled Branches of the Internal Iliac Artery, with its labels hidden under occlusion masks" });
  svg.append(el("rect", { x: 0, y: 0, width: 960, height: 650, fill: "#ffffff" }));
  svg.append(el("rect", { x: 0, y: 0, width: 960, height: 8, fill: "#2b3a67" }));
  svg.append(el("text", { x: 40, y: 64, class: "title" }, "Branches of the Internal Iliac Artery"));
  svg.append(el("rect", { x: 40, y: 570, width: 880, height: 1, fill: "#d8dbe2" }));
  for (const [d, w] of VESSELS) svg.append(el("path", { d, class: "vessel", "stroke-width": w }));

  const texts = {};
  for (const [id, t, x, y, anchor] of LABELS) {
    texts[id] = svg.appendChild(el("text", { x, y, class: "label", "text-anchor": anchor }, t));
  }
  const bulletParts = [];
  BULLETS.forEach(([lead, key, rest, x, y], i) => {
    const t = el("text", { x, y, class: "bullet" });
    const dot = el("tspan", {}, "•  " + lead);
    const k = el("tspan", {}, key);
    const r = el("tspan", {}, rest);
    t.append(dot, k, r);
    svg.append(t);
    bulletParts.push({ t, dot, k, r, i });
  });
  host.append(svg);

  // masks go on top of everything, sized to the text they cover
  const layer = svg.appendChild(el("g"));
  const masks = [];
  const pad = 4;
  const mk = (box, kind, id) => {
    const m = el("rect", {
      x: box.x - pad, y: box.y - pad + 1, width: box.width + pad * 2, height: box.height + pad * 2 - 2,
      class: "mask" + (intro ? " pre" : ""), rx: 3, tabindex: 0, role: "button",
      "aria-label": "Hidden answer",
    });
    m.dataset.kind = kind;
    m.dataset.id = id;
    const toggle = () => {
      m.classList.toggle("revealed");
      m.setAttribute("aria-label", m.classList.contains("revealed") ? "Answer shown" : "Hidden answer");
    };
    m.addEventListener("click", toggle);
    m.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggle(); } });
    layer.append(m);
    masks.push(m);
    return m;
  };

  const measure = () => {
    layer.replaceChildren();
    masks.length = 0;
    for (const [id, , , , , rel] of LABELS) {
      const m = mk(texts[id].getBBox(), "label", id);
      m.dataset.relevant = rel ? "1" : "0";
    }
    for (const b of bulletParts) {
      // key phrase only, and the whole predicate (key + rest)
      const kb = b.k.getBBox();
      mk(kb, "key", `b${b.i}`);
      const rb = b.r.getBBox();
      const whole = { x: kb.x, y: kb.y, width: (rb.width ? rb.x + rb.width : kb.x + kb.width) - kb.x, height: kb.height };
      mk(whole, "whole", `w${b.i}`);
    }
  };

  let settings = { labels: "all", text: "key_phrase" };
  let activeId = "obturator";

  const apply = (s = settings) => {
    settings = { ...settings, ...s };
    let shown = 0;
    for (const m of masks) {
      const k = m.dataset.kind;
      let on;
      if (k === "label") on = settings.labels === "all" || (settings.labels === "relevant" && m.dataset.relevant === "1");
      else if (k === "key") on = settings.text === "key_phrase";
      else on = settings.text === "whole_bullet";
      m.classList.toggle("off", !on);
      m.classList.toggle("active", on && m.dataset.id === activeId);
      if (on) shown++;
    }
    return shown;
  };

  // wait for the font metrics before measuring
  const ready = document.fonts ? document.fonts.ready : Promise.resolve();
  const started = ready.then(() => {
    measure();
    const n = apply();
    if (!intro) return n;
    const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    masks.forEach((m, i) => setTimeout(() => m.classList.remove("pre"), reduce ? 0 : 450 + i * 70));
    return n;
  });

  return {
    ready: started,
    apply,
    revealAll(on = true) { for (const m of masks) m.classList.toggle("revealed", on); },
    setActive(id) { activeId = id; apply(); },
  };
}
