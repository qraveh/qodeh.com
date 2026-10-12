// Tests for assets/js/qsearch/core.js. Run: node --test tests/
import test from "node:test";
import assert from "node:assert/strict";
import { compile, scan, snippet, matchDoc, search, textFragment, fragmentFor, escapeRe } from "../assets/js/qsearch/core.js";

test("a query is a regular expression; one that does not parse is taken literally", () => {
  const c = compile("[bg]ui");
  assert.equal(c.literal, false);
  assert.equal(scan("a gui and a bui", c.re).count, 2);
  const lit = compile("a[b");                  // a lone "[" while typing
  assert.equal(lit.literal, true);
  assert.equal(scan("x a[b y", lit.re).count, 1);
  assert.equal(compile("   "), null);
});

test("case-insensitive by default, case-sensitive on request", () => {
  assert.equal(scan("Transmon transmon", compile("transmon").re).count, 2);
  assert.equal(scan("Transmon transmon", compile("transmon", { cs: true }).re).count, 1);
});

test("whole word uses Unicode word boundaries, in any script", () => {
  const w = compile("ion", { whole: true });
  assert.equal(scan("ion ions trapped-ion (ion)", w.re).count, 3);   // "ions" is not a whole-word hit; "-" and "(" delimit
  assert.equal(scan("кубит кубиты", compile("кубит", { whole: true }).re).count, 1);
  assert.equal(scan("קיוביט קיוביטים", compile("קיוביט", { whole: true }).re).count, 1);
});

test("an empty-matching pattern neither hangs nor counts", () => {
  const r = scan("aaa bbb", compile("x*").re);
  assert.equal(r.count, 0);
  assert.equal(scan("aaa", compile("a*").re).count, 1);
});

test("snippets cut at word boundaries and keep the hit", () => {
  const text = "one two three four five six seven eight nine ten eleven twelve thirteen";
  const s = snippet(text, [text.indexOf("seven"), text.indexOf("seven") + 5], 12);
  assert.equal(s.hit, "seven");
  assert.ok(s.pre.startsWith("…") && s.post.endsWith("…"));
  assert.ok(!/\S…$/.test(s.pre.slice(0, 2)));
});

test("ranking: title hits first, then description, then the text", () => {
  const docs = [
    { t: "Machine A", u: "/a", k: "machine", d: "", x: "uses transmon transmon transmon" },
    { t: "Transmon", u: "/t", k: "technology", d: "", x: "" },
    { t: "Machine B", u: "/b", k: "machine", d: "a transmon lattice", x: "" },
  ];
  const r = search(docs, compile("transmon"));
  assert.deepEqual(r.map(g => g.group.id), ["technology", "machine"]);
  assert.deepEqual(r[1].items.map(i => i.doc.u), ["/b", "/a"]);
});

test("site pages group together whatever their section", () => {
  const docs = [{ t: "About", u: "/about/", k: "page", d: "", x: "mission" }, { t: "Monitor", u: "/p/", k: "publication", d: "", x: "mission" }];
  const r = search(docs, compile("mission"));
  assert.equal(r.length, 1);
  assert.equal(r[0].group.id, "site");
  assert.equal(r[0].total, 2);
});

test("text fragments escape the directive's delimiters", () => {
  assert.equal(textFragment("trapped-ion, a & b"), "#:~:text=trapped%2Dion%2C%20a%20%26%20b");
  assert.equal(textFragment(""), "");
  const doc = { t: "X", d: "", x: "the dual-rail erasure qubit" };
  assert.equal(fragmentFor(doc, matchDoc(doc, compile("erasure").re)), "erasure");
});

test("escapeRe makes any string literal", () => {
  const s = "a.b*c+d?(e)[f]{g}|h^i$j\\k/l";
  assert.ok(new RegExp(escapeRe(s)).test(s));
});
