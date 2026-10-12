// The site search's core: the query as the Atlas's Find reads it, matching, ranking, snippets. Pure functions, no DOM,
// so that tests/qsearch_core.test.mjs runs them in Node.
//
// The query is a regular expression in the ECMAScript dialect (`[bg]ui`, `\d+ q`, `erasure|stirania`, `heron.*flux`);
// an expression that does not parse yet (a lone "[" while typing) is taken literally until it does — as in the Atlas.
// Options: case-insensitive / case-sensitive, substring / whole word (Unicode word boundaries: any non-letter, non-digit
// delimits a word, not only a space).

export function escapeRe(s) {
  return s.replace(/[.*+?^${}()|[\]\\\/]/g, "\\$&");
}

// {re, literal} for a query, or null for an empty one. `re` carries the g flag (scan walks it with lastIndex).
export function compile(query, opts = {}) {
  const src = (query || "").trim();
  if (!src) return null;
  let body = src, literal = false;
  try { new RegExp(src, "u"); } catch (e) { body = escapeRe(src); literal = true; }
  if (opts.whole) body = "(?<![\\p{L}\\p{N}_])(?:" + body + ")(?![\\p{L}\\p{N}_])";
  const flags = "gu" + (opts.cs ? "" : "i");
  try { return { re: new RegExp(body, flags), literal }; }
  catch (e) { return { re: new RegExp(escapeRe(src), flags), literal: true }; }
}

// Hits of `re` in `text`, at most `cap` counted: {count, first: [start, end] | null}. Empty matches are not hits
// (a query such as "a*" matches the empty string everywhere) and never stall the walk.
export function scan(text, re, cap = 200) {
  if (!text) return { count: 0, first: null };
  re.lastIndex = 0;
  let m, count = 0, first = null, guard = 0;
  while ((m = re.exec(text)) !== null) {
    if (m[0].length === 0) { re.lastIndex = m.index + 1; if (++guard > 100000) break; continue; }
    if (!first) first = [m.index, m.index + m[0].length];
    if (++count >= cap) break;
  }
  return { count, first };
}

// A snippet around a hit: {pre, hit, post}, cut at word boundaries, with "…" where the text goes on.
export function snippet(text, at, radius = 70) {
  const [s, e] = at;
  let a = Math.max(0, s - radius), b = Math.min(text.length, e + radius);
  if (a > 0) { const sp = text.indexOf(" ", a); if (sp > -1 && sp < s) a = sp + 1; }
  if (b < text.length) { const sp = text.lastIndexOf(" ", b); if (sp > e) b = sp; }
  return { pre: (a > 0 ? "…" : "") + text.slice(a, s), hit: text.slice(s, e), post: text.slice(e, b) + (b < text.length ? "…" : "") };
}

// Match one document {t, d, x}: null when nothing matches, otherwise the score and where the first hits are.
// Title hits weigh most, then the description, then the number of hits in the text.
export function matchDoc(doc, re) {
  const t = scan(doc.t, re, 20), d = scan(doc.d, re, 20), x = scan(doc.x, re, 500);
  const total = t.count + d.count + x.count;
  if (!total) return null;
  const score = (t.count ? 1000 : 0) + (d.count ? 100 : 0) + Math.min(x.count, 99);
  return { score, total, title: t.first, desc: d.first, text: x.first, textCount: x.count };
}

// The literal text of the first hit to point a text fragment at (#:~:text=…): the hit in the text, else in the description.
export function fragmentFor(doc, m) {
  if (m.text) return doc.x.slice(m.text[0], m.text[1]);
  if (m.desc) return doc.d.slice(m.desc[0], m.desc[1]);
  return "";
}

// URL of a text fragment for `text` (the directive's own delimiters - , & are escaped); "" when there is nothing to point at.
export function textFragment(text) {
  const t = (text || "").trim().slice(0, 80);
  if (!t) return "";
  return "#:~:text=" + encodeURIComponent(t).replace(/-/g, "%2D");
}

// The groups, in the order they are shown; a document's kind decides its group.
export const GROUPS = [
  { id: "site", label: "On this site", kinds: ["page", "publication", "project", "lecture"] },
  { id: "technology", label: "Atlas · technologies", kinds: ["technology"] },
  { id: "machine", label: "Atlas · machines", kinds: ["machine"] },
  { id: "organisation", label: "Atlas · organisations", kinds: ["organisation"] },
  { id: "architecture", label: "Atlas · architectures", kinds: ["architecture"] },
  { id: "glossary", label: "Atlas · glossary", kinds: ["glossary"] },
];
export const KIND_LABEL = { page: "Page", publication: "Publication", project: "Project", lecture: "Lecture",
  technology: "Technology", machine: "Machine", organisation: "Organisation", architecture: "Architecture", glossary: "Glossary" };

// Search a list of documents: [{group, items: [{doc, m}], total}] with the items of each group ranked.
export function search(docs, compiled) {
  if (!compiled) return [];
  const byGroup = new Map(GROUPS.map(g => [g.id, []]));
  const kindGroup = {};
  GROUPS.forEach(g => g.kinds.forEach(k => { kindGroup[k] = g.id; }));
  for (const doc of docs) {
    const m = matchDoc(doc, compiled.re);
    if (m) byGroup.get(kindGroup[doc.k] || "site").push({ doc, m });
  }
  const out = [];
  for (const g of GROUPS) {
    const items = byGroup.get(g.id);
    if (!items.length) continue;
    items.sort((a, b) => b.m.score - a.m.score || a.doc.t.localeCompare(b.doc.t));
    out.push({ group: g, items, total: items.length });
  }
  return out;
}
