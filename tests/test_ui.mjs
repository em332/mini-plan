/* Tests der Bedienung: Suchlogik und Namensfilter im DOM (jsdom).
   Aufruf: node --test tests/test_ui.mjs   (benoetigt: npm install jsdom) */
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { JSDOM } from "jsdom";
import { createRequire } from "node:module";

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const require = createRequire(import.meta.url);
const S = require(path.join(ROOT, "public", "search.js"));
const PLAN = JSON.parse(fs.readFileSync(path.join(ROOT, "public", "plan.json"), "utf8"));

function page() {
  const dom = new JSDOM(fs.readFileSync(path.join(ROOT, "public", "index.html"), "utf8"),
    { runScripts: "outside-only", pretendToBeVisual: true });
  const { window } = dom;
  window.eval(fs.readFileSync(path.join(ROOT, "public", "search.js"), "utf8"));
  window.eval(fs.readFileSync(path.join(ROOT, "public", "app.js"), "utf8"));
  return window;
}

const visibleMasses = (w) =>
  [...w.document.querySelectorAll(".mass")].filter((el) => !el.hidden);
const marked = (w) =>
  [...w.document.querySelectorAll(".servers li.is-match")].map((li) => li.dataset.name);

/* ---------------- Suchlogik ---------------- */
test("Suche ignoriert Gross- und Kleinschreibung", () => {
  assert.ok(S.matches("Lena B.", "lena"));
  assert.ok(S.matches("Lena B.", "LENA"));
  assert.ok(S.matches("Lena B.", "LeNa b."));
});

test("Teiltreffer funktionieren", () => {
  assert.ok(S.matches("Anna-Catharina M.", "cath"));
  assert.ok(S.matches("Simon Johannes E.", "johannes"));
});

test("Umlaut- und ss-Eingaben werden beruecksichtigt", () => {
  assert.equal(S.normalise("Wöß"), "woess");
  assert.ok(S.matches("Wöß", "woess"));
  assert.ok(S.matches("Wöß", "woss"));
  assert.ok(S.matches("Wöß", "WÖSS"));
});

test("Normalisierung fuehrt verschiedene Personen nicht zusammen", () => {
  assert.notEqual(S.normalise("Emma K."), S.normalise("Emma O."));
  assert.ok(!S.matches("Emma K.", "Emma O."));
  assert.ok(!S.matches("Lukas B.", "Lukas K."));
  assert.ok(!S.matches("Felix B.", "Magnus B."));
});

test("Exakter Name trifft nur diese Person, nicht aehnliche Namen", () => {
  const all = [...new Set(PLAN.services.flatMap((s) => s.servers))];
  assert.ok(all.includes("Lena B.") && all.includes("Annalena B."));
  assert.ok(S.matches("Lena B.", "Lena B.", all));
  assert.ok(!S.matches("Annalena B.", "Lena B.", all), "Annalena darf kein Treffer sein");
  // Teileingabe bleibt weiterhin ein Teiltreffer fuer beide
  assert.ok(S.matches("Lena B.", "lena", all));
  assert.ok(S.matches("Annalena B.", "lena", all));
});

test("Leere Eingabe liefert den Gesamtplan", () => {
  const r = S.filterPlan(PLAN.services, "  ");
  assert.equal(r.active, false);
  assert.equal(r.services.length, 8);
});

/* ---------------- Filter im DOM ---------------- */
test("Ohne Filter sind alle acht Gottesdienste sichtbar", () => {
  const w = page();
  assert.equal(visibleMasses(w).length, 8);
  assert.match(w.document.getElementById("filter-status").textContent, /alle 8 Gottesdienste/);
});

test("Bedienelemente erscheinen erst mit JavaScript", () => {
  const raw = fs.readFileSync(path.join(ROOT, "public", "index.html"), "utf8");
  assert.match(raw, /<form class="filter print-hide" id="filter" hidden>/);
  const w = page();
  assert.equal(w.document.getElementById("filter").hidden, false);
});

test("Auswahlliste enthaelt genau die eindeutigen Anzeigenamen", () => {
  const w = page();
  const opts = [...w.document.querySelectorAll("#name-select option")]
    .map((o) => o.value).filter(Boolean);
  const names = new Set(PLAN.services.flatMap((s) => s.servers));
  assert.equal(opts.length, names.size);
  assert.equal(new Set(opts).size, opts.length, "Anzeigenamen muessen eindeutig sein");
});

test("Filter zeigt die passenden Termine mit vollstaendiger Besetzung", () => {
  const w = page();
  const input = w.document.getElementById("name-search");
  input.value = "Zita B.";
  input.dispatchEvent(new w.Event("input"));

  const expected = PLAN.services.filter((s) => s.servers.includes("Zita B."));
  const shown = visibleMasses(w);
  assert.equal(shown.length, expected.length);
  assert.equal(shown.length, 2);
  shown.forEach((el) => {
    const svc = PLAN.services.find((s) => s.id === el.id);
    assert.equal(el.querySelectorAll(".servers li").length, svc.servers.length);
  });
  assert.match(w.document.getElementById("filter-status").textContent, /2 Termine/);
});

test("Gesuchte Person wird sichtbar hervorgehoben, nicht nur farblich", () => {
  const w = page();
  const input = w.document.getElementById("name-search");
  input.value = "zita";
  input.dispatchEvent(new w.Event("input"));
  assert.deepEqual([...new Set(marked(w))], ["Zita B."]);
  const li = w.document.querySelector(".servers li.is-match .match-flag");
  assert.match(li.textContent, /gesucht/);
});

test("Angezeigte Terminanzahl stimmt mit dem geprueften Plan ueberein", () => {
  const w = page();
  const input = w.document.getElementById("name-search");
  for (const name of new Set(PLAN.services.flatMap((s) => s.servers))) {
    input.value = name;
    input.dispatchEvent(new w.Event("input"));
    const expected = PLAN.services.filter((s) => s.servers.includes(name)).length;
    assert.equal(visibleMasses(w).length, expected, name);
    assert.match(w.document.getElementById("filter-status").textContent,
      new RegExp("^" + expected + " Termin"));
  }
});

test("Kein Treffer liefert eine verstaendliche Meldung", () => {
  const w = page();
  const input = w.document.getElementById("name-search");
  input.value = "Xaver Q.";
  input.dispatchEvent(new w.Event("input"));
  assert.equal(visibleMasses(w).length, 0);
  const st = w.document.getElementById("filter-status");
  assert.match(st.textContent, /Keine Treffer/);
  assert.ok(st.classList.contains("is-empty"));
});

test("Filter zuruecksetzen stellt den Gesamtplan wieder her", () => {
  const w = page();
  const input = w.document.getElementById("name-search");
  input.value = "Zita B.";
  input.dispatchEvent(new w.Event("input"));
  assert.equal(visibleMasses(w).length, 2);
  w.document.getElementById("filter-reset").dispatchEvent(new w.Event("click"));
  assert.equal(visibleMasses(w).length, 8);
  assert.equal(input.value, "");
  assert.equal(marked(w).length, 0);
});

test("Auswahlfeld filtert ebenso und ist per Tastatur bedienbar", () => {
  const w = page();
  const select = w.document.getElementById("name-select");
  select.value = "Klara E.";
  select.dispatchEvent(new w.Event("change"));
  const expected = PLAN.services.filter((s) => s.servers.includes("Klara E.")).length;
  assert.equal(visibleMasses(w).length, expected);
  assert.equal(w.document.getElementById("name-search").value, "Klara E.");
});

test("Formularfelder haben sichtbare Beschriftungen", () => {
  const w = page();
  for (const id of ["name-search", "name-select"]) {
    const label = w.document.querySelector(`label[for="${id}"]`);
    assert.ok(label && label.textContent.trim().length > 0, id);
    assert.equal(label.hasAttribute("hidden"), false);
  }
});

test("Druckansicht benennt die gewaehlte Ansicht eindeutig", () => {
  const w = page();
  const scope = w.document.getElementById("print-scope");
  assert.match(scope.textContent, /Gesamtplan/);
  const input = w.document.getElementById("name-search");
  input.value = "Zita B.";
  input.dispatchEvent(new w.Event("input"));
  assert.match(scope.textContent, /Gefilterte Ansicht: Zita B\./);
  assert.match(scope.textContent, /2 Termine/);
});

test("Kontaktlink verweist auf anita@einsle.at", () => {
  const w = page();
  const a = w.document.querySelector('a[href="mailto:anita@einsle.at"]');
  assert.ok(a);
  assert.equal(a.textContent.trim(), "anita@einsle.at");
});

test("Hinweis auf die geaenderte Abendmesse ist sichtbar", () => {
  const w = page();
  assert.match(w.document.querySelector(".notice").textContent,
    /Ab Sonntag, 25\. Oktober, beginnt die Abendmesse um 19:00 Uhr\./);
});
