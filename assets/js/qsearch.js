// Site search: the Atlas's Find carried over to the whole site (the editor's Q49 (b), 2026-10-11). One search over the
// site's pages and the Atlas's records — technologies, machines, organisations, architectures, the glossary — grouped
// by kind, each hit linking straight to its page (a text fragment scrolls to it and marks it). The query and options are
// read as in the Atlas (qsearch/core.js). Opens from any page with / or Ctrl+K (⌘K), or the menu's "Search"; the
// /search/ page shows the same panel in place and keeps the query in its address (?q=…&cs=1&w=1&l=ru).
//
// Loading: the site's pages and the Atlas's records without their text (search/site.json, search/atlas-<lang>.json,
// ~45 KB compressed) are fetched at idle on every page unless the reader saves data; the records' full text
// (search/atlas-<lang>-text.json, ~1 MB) when the search opens. Results come from what is there and deepen when the
// rest arrives. Built by scripts/build_search_index.py at deploy.
import { compile, search, snippet, fragmentFor, textFragment, escapeRe, KIND_LABEL } from "./qsearch/core.js";

const BASE = "/search/";
const LANGS = [["en", "English"], ["ru", "Русский"], ["he", "עברית"]];
const ATLAS = "/publications/quantum-technology-atlas/";
const PER_GROUP = 8;
const store = {};
const failed = new Set();       // files whose fetch failed: reported, and tried again when the search next opens

function saveData() {
  const c = navigator.connection;
  return !!(c && (c.saveData || /(^|-)2g$/.test(c.effectiveType || "")));
}
function load(name) {
  if (!store[name]) {
    failed.delete(name);
    store[name] = fetch(BASE + name, { credentials: "same-origin", priority: "low" })
      .then(r => { if (!r.ok) throw new Error(name + " " + r.status); return r.json(); });
    store[name].catch(() => { delete store[name]; failed.add(name); if (ui) status(); });
  }
  return store[name];
}
function ready(name) { return store[name] && store[name].done ? store[name].value : null; }
function track(name) { const p = load(name); if (!p.tracked) { p.tracked = true; p.then(v => { p.done = true; p.value = v; }, () => {}); } return p; }

// ---------- the documents in scope: the site's pages, and the Atlas's records (with their text once it has arrived)
function scopeLangs(l) { return l === "all" ? LANGS.map(x => x[0]) : [l]; }
function docsFor(lang) {
  const out = [];
  const site = ready("site.json");
  if (site) out.push(...site.docs);
  for (const L of scopeLangs(lang)) {
    const a = ready(`atlas-${L}.json`), x = ready(`atlas-${L}-text.json`);
    if (!a) continue;
    if (!a._docs || a._withText !== !!x) {
      a._docs = a.docs.map((d, i) => ({ ...d, x: x ? x.x[i] || "" : "", lang: L }));
      a._docs.push(...a.g.map(g => ({ t: g.t, u: g.u, k: "glossary", d: g.d, x: "", lang: L })));
      a._withText = !!x;
    }
    out.push(...a._docs);
  }
  return out;
}
function pending(lang) {
  const names = ["site.json", ...scopeLangs(lang).flatMap(L => [`atlas-${L}.json`, `atlas-${L}-text.json`])];
  return names.filter(n => !ready(n) && !failed.has(n));
}
function unavailable(lang) {
  const names = ["site.json", ...scopeLangs(lang).flatMap(L => [`atlas-${L}.json`, `atlas-${L}-text.json`])];
  return names.filter(n => failed.has(n));
}

// ---------- the panel (built on first use; a <dialog> over the page, or in place on /search/)
const opts = { cs: false, whole: false, lang: "en" };
let ui = null, active = -1, results = [], lastRun = "";

function el(tag, attrs, ...kids) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (k === "class") e.className = v; else if (k === "text") e.textContent = v; else e.setAttribute(k, v);
  }
  kids.forEach(k => k != null && e.append(k));
  return e;
}

function build(inPlace) {
  const q = el("input", { type: "search", class: "qs-q", autocomplete: "off", spellcheck: "false",
    placeholder: "Search the site and the Atlas — regex: [bg]ui  \\d+ q  a|b",
    "aria-label": "Search the site and the Atlas: a regular expression; Enter opens the first result",
    "aria-controls": "qs-res", "aria-autocomplete": "list", role: "combobox", "aria-expanded": "false" });
  const close = inPlace ? null : el("button", { type: "button", class: "qs-close", "aria-label": "Close (Escape)", title: "Close (Esc)", text: "✕" });
  const cs = el("button", { type: "button", class: "qs-o", "aria-pressed": "false", title: "click to toggle" });
  const whole = el("button", { type: "button", class: "qs-o", "aria-pressed": "false", title: "click to toggle" });
  const lang = el("select", { class: "qs-lang", "aria-label": "Language of the Atlas searched" });
  LANGS.forEach(([v, n]) => lang.append(el("option", { value: v, text: "Atlas: " + n })));
  lang.append(el("option", { value: "all", text: "Atlas: all languages" }));
  const mode = el("span", { class: "qs-mode", title: "the query is read as a regular expression; one that does not parse is taken literally" });
  const count = el("span", { class: "qs-count", "aria-live": "polite" });
  const res = el("div", { class: "qs-res", id: "qs-res", role: "listbox", "aria-label": "Results" });
  const atlasFind = el("button", { type: "button", class: "qs-atlas", hidden: "" });
  const foot = el("div", { class: "qs-foot" },
    el("span", { class: "qs-keys", text: "↑ ↓ choose · Enter open · " + (inPlace ? "/ or Ctrl+K from any page" : "Esc close") }), atlasFind);
  const panel = el("div", { class: "qs-panel" },
    el("div", { class: "qs-row" }, el("span", { class: "qs-icon", "aria-hidden": "true" }), q, close),
    el("div", { class: "qs-opts" }, cs, whole, lang, mode, count), res, foot);
  let box;
  if (inPlace) { box = inPlace; box.append(panel); }
  else {
    box = el("dialog", { class: "qs-dialog", "aria-label": "Search the site and the Atlas" }, panel);
    document.body.append(box);
    box.addEventListener("click", ev => { if (ev.target === box) box.close(); });     // a click on the backdrop closes
    close.addEventListener("click", () => box.close());
  }
  const paint = () => {
    cs.textContent = opts.cs ? "case-sensitive" : "case-insensitive"; cs.setAttribute("aria-pressed", String(opts.cs));
    whole.textContent = opts.whole ? "whole word" : "substring"; whole.setAttribute("aria-pressed", String(opts.whole));
    lang.value = opts.lang;
  };
  cs.addEventListener("click", () => { opts.cs = !opts.cs; paint(); run(); });
  whole.addEventListener("click", () => { opts.whole = !opts.whole; paint(); run(); });
  lang.addEventListener("change", () => { opts.lang = lang.value; fetchScope(); run(); });
  let typing = null;
  q.addEventListener("input", () => { clearTimeout(typing); typing = setTimeout(run, 70); });
  q.addEventListener("keydown", onKey);
  atlasFind.addEventListener("click", () => toAtlasFind(q.value.trim(), opts.lang === "all" ? "en" : opts.lang, false));
  ui = { box, q, res, count, mode, atlasFind, inPlace: !!inPlace, paint };
  paint();
  return ui;
}

function fetchScope() {
  const all = ["site.json", ...scopeLangs(opts.lang).flatMap(L => [`atlas-${L}.json`, `atlas-${L}-text.json`])];
  all.forEach(n => track(n).then(() => { if (ui && ui.q.value.trim()) run(true); }, () => { if (ui) status(); }));
}

function status(found) {
  if (found === undefined) found = ui.lastFound;
  ui.lastFound = found;
  const wait = pending(opts.lang), lost = unavailable(opts.lang);
  const parts = [];
  if (found != null) parts.push(found === 0 ? "no results" : found + (found === 1 ? " result" : " results"));
  if (wait.some(n => n.endsWith("-text.json"))) parts.push("Atlas full text loading…");
  else if (wait.length) parts.push("loading…");
  if (lost.some(n => n.endsWith("-text.json"))) parts.push("Atlas full text unavailable: titles and descriptions only");
  if (lost.some(n => !n.endsWith("-text.json"))) parts.push("part of the index is unavailable; it is tried again when the search reopens");
  ui.count.textContent = parts.join(" · ");
}

function run(again) {
  if (!ui) return;
  const v = ui.q.value.trim();
  const key = [v, opts.cs, opts.whole, opts.lang, pending(opts.lang).length].join("|");
  if (key === lastRun && !again) return;
  lastRun = key;
  if (ui.inPlace) syncAddress(v);
  const c = compile(v, opts);
  ui.mode.textContent = c ? (c.literal ? "literal" : "regex") : "";
  ui.atlasFind.hidden = !v;
  ui.atlasFind.textContent = v ? `Find “${v.length > 30 ? v.slice(0, 30) + "…" : v}” inside the Atlas page →` : "";
  results = c ? search(docsFor(opts.lang), c) : [];
  render(results, c);
  status(c ? results.reduce((n, g) => n + g.total, 0) : null);
}

function mark(text, at) {
  if (!at) return document.createTextNode(text);
  const f = document.createDocumentFragment();
  f.append(text.slice(0, at[0]), el("mark", { text: text.slice(at[0], at[1]) }), text.slice(at[1]));
  return f;
}

function href(doc, m) {
  return doc.k === "glossary" ? doc.u : doc.u + textFragment(fragmentFor(doc, m));
}

function render(groups, c) {
  const res = ui.res;
  res.textContent = "";
  active = -1;
  ui.q.setAttribute("aria-expanded", String(groups.length > 0));
  ui.q.removeAttribute("aria-activedescendant");
  if (!c) { res.append(el("p", { class: "qs-hint", text: "Type to search every page of the site and every record of the Atlas. The query is a regular expression: [bg]ui · \\d+ q · erasure|leakage · heron.*flux" })); return; }
  let n = 0;
  for (const { group, items, total } of groups) {
    const list = el("ol", { class: "qs-list" });
    const show = items.slice(0, PER_GROUP);
    const addItems = arr => arr.forEach(({ doc, m }) => {
      const id = "qs-i" + (n++);
      const a = el("a", { class: "qs-hit", href: href(doc, m), id, role: "option" });
      if (doc.k === "glossary") a.addEventListener("click", ev => { ev.preventDefault(); toAtlasFind(escapeRe(doc.t), doc.lang, true); });
      const at = m.text || m.desc;
      const src = m.text ? doc.x : m.desc ? doc.d : doc.d;
      const meta = el("span", { class: "qs-k", text: KIND_LABEL[doc.k] + (doc.lang && doc.lang !== "en" ? " · " + doc.lang.toUpperCase() : "") + (m.textCount > 1 ? ` · ${m.textCount}${m.textCount >= 500 ? "+" : ""} hits` : "") });
      a.append(el("span", { class: "qs-t" }, mark(doc.t, m.title)), meta);
      if (at && src) { const s = snippet(src, at); a.append(el("span", { class: "qs-s" }, s.pre, el("mark", { text: s.hit }), s.post)); }
      else if (doc.d) a.append(el("span", { class: "qs-s", text: doc.d.length > 160 ? doc.d.slice(0, 160) + "…" : doc.d }));
      const li = el("li", {}, a);
      if (doc.lang && doc.lang !== "en") { li.setAttribute("lang", doc.lang); if (doc.lang === "he") li.setAttribute("dir", "rtl"); }
      list.append(li);
    });
    addItems(show);
    const sec = el("section", { class: "qs-g" }, el("h3", { class: "qs-gh" }, group.label + " ", el("span", { text: String(total) })), list);
    if (total > show.length) {
      const more = el("button", { type: "button", class: "qs-more", text: `Show all ${total}` });
      more.addEventListener("click", () => { addItems(items.slice(PER_GROUP)); more.remove(); });
      sec.append(more);
    }
    res.append(sec);
  }
}

function options() { return Array.from(ui.res.querySelectorAll(".qs-hit")); }
function setActive(i) {
  const all = options();
  if (!all.length) return;
  active = (i + all.length) % all.length;
  all.forEach((a, k) => a.setAttribute("aria-selected", String(k === active)));
  ui.q.setAttribute("aria-activedescendant", all[active].id);
  all[active].scrollIntoView({ block: "nearest" });
}
function onKey(ev) {
  if (ev.key === "ArrowDown") { ev.preventDefault(); setActive(active + 1); }
  else if (ev.key === "ArrowUp") { ev.preventDefault(); setActive(active - 1); }
  else if (ev.key === "Enter") {
    const all = options();
    const a = all[active >= 0 ? active : 0];
    if (a) { ev.preventDefault(); a.click(); }
  }
}

// The Atlas's own Find opens with this query: it keeps its state under "qtech-find" (build/find_js.py in qt-map) and a
// page loaded with that state open reopens Find and runs the query. If the Atlas ever changes the key, it simply opens.
function toAtlasFind(query, lang, literal) {
  try {
    localStorage.setItem("qtech-find", JSON.stringify({ open: true, x: null, y: null, collapsed: false, q: query,
      cs: literal ? false : opts.cs, whole: literal ? false : opts.whole, scope: "this" }));
  } catch (e) {}
  location.href = ATLAS + (lang && lang !== "en" ? lang + "/" : "");
}

function syncAddress(v) {
  const p = new URLSearchParams();
  if (v) p.set("q", v);
  if (opts.cs) p.set("cs", "1");
  if (opts.whole) p.set("w", "1");
  if (opts.lang !== "en") p.set("l", opts.lang);
  const s = p.toString();
  history.replaceState(null, "", location.pathname + (s ? "?" + s : ""));
}

function open() {
  if (!ui) build(null);
  fetchScope();
  if (ui.inPlace) { ui.q.focus(); return; }
  if (!ui.box.open) ui.box.showModal();
  ui.q.focus();
  try { ui.q.select(); } catch (e) {}
  run(true);
}

// ---------- wiring
function init() {
  const page = document.getElementById("qs-page");
  if (page) {                                   // the /search/ page: the panel in place, the query from the address
    const p = new URLSearchParams(location.search);
    opts.cs = p.get("cs") === "1"; opts.whole = p.get("w") === "1";
    if (["ru", "he", "all"].includes(p.get("l"))) opts.lang = p.get("l");
    build(page);
    ui.q.value = p.get("q") || "";
    fetchScope();
    ui.q.focus();
    run(true);
  }
  document.addEventListener("keydown", ev => {
    const t = ev.target;
    const typing = t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.tagName === "SELECT" || t.isContentEditable);
    // the Atlas's hotkeys, matched by the physical key so that a Russian or Hebrew layout opens it too (the editor, 2 Oct 2026)
    if (!typing && !ev.ctrlKey && !ev.metaKey && !ev.altKey && (ev.key === "/" || (ev.code === "Slash" && !ev.shiftKey))) { ev.preventDefault(); open(); }
    else if ((ev.ctrlKey || ev.metaKey) && !ev.shiftKey && !ev.altKey && (ev.code === "KeyK" || ev.key === "k" || ev.key === "K")) { ev.preventDefault(); open(); }
  });
  document.querySelectorAll('#menu a[href$="/search/"]').forEach(a => a.addEventListener("click", ev => {
    if (ev.ctrlKey || ev.metaKey || ev.shiftKey || ev.button !== 0 || page) return;   // a new tab, or already on the page
    ev.preventDefault(); open();
  }));
  // at idle, the light tier, so the first keystroke already has something to search
  const idle = window.requestIdleCallback || (f => setTimeout(f, 2500));
  const preload = () => idle(() => { if (!saveData()) { track("site.json"); track("atlas-en.json"); } }, { timeout: 5000 });
  if (document.readyState === "complete") preload(); else addEventListener("load", preload, { once: true });
}

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
