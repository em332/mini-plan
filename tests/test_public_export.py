# -*- coding: utf-8 -*-
"""Tests des oeffentlichen Exports (Auftrag Abschnitte 8 und 10).

Geprueft wird der fertig erzeugte Veroeffentlichungsstand in public/.
"""
import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = os.path.join(ROOT, "public")
sys.path.insert(0, os.path.join(ROOT, "src"))

import validate as V  # noqa: E402

with open(os.path.join(ROOT, "data", "people.json"), encoding="utf-8") as fh:
    PEOPLE_DOC = json.load(fh)
PEOPLE = PEOPLE_DOC["people"]
with open(os.path.join(ROOT, "out", "plan.internal.json"), encoding="utf-8") as fh:
    INTERNAL = json.load(fh)
with open(os.path.join(PUBLIC, "plan.json"), encoding="utf-8") as fh:
    PUB = json.load(fh)

PUBLIC_FILES = sorted(f for f in os.listdir(PUBLIC) if not f.startswith("."))
PUBLIC_TEXT = ""
for _f in PUBLIC_FILES:
    with open(os.path.join(PUBLIC, _f), encoding="utf-8") as fh:
        PUBLIC_TEXT += "\n" + fh.read()

DISPLAY = {p["id"]: p["display"] for p in PEOPLE}


class OeffentlicheDaten(unittest.TestCase):
    def test_keine_vollstaendigen_nachnamen_in_den_plandaten(self):
        """In den Einsatzdaten erscheint nur Vorname + Nachnamensinitiale."""
        plandaten = json.dumps(PUB["services"], ensure_ascii=False)
        with open(os.path.join(PUBLIC, "index.html"), encoding="utf-8") as fh:
            roster = "\n".join(re.findall(r'<li data-name=[^>]*>.*?</li>', fh.read()))
        for p in PEOPLE:
            with self.subTest(person=p["id"]):
                self.assertNotIn(p["lastName"], plandaten)
                self.assertNotIn(p["lastName"], roster)

    def test_nachnamen_sonst_nirgends_ausser_freigegebener_kontaktangabe(self):
        """Einzige Ausnahme: die ausdruecklich zur Anzeige vorgesehene Kontaktangabe.

        'Einsle' ist zugleich der Nachname von Klara E. und Martha E. Die
        Kontaktangabe 'Anita Einsle / anita@einsle.at' ist laut Auftrag
        Abschnitt 7 zur Anzeige vorgesehen; sie wird hier bewusst zugelassen.
        """
        erlaubt = {"Einsle"}
        for p in PEOPLE:
            if p["lastName"] in erlaubt:
                continue
            with self.subTest(person=p["id"]):
                self.assertNotIn(p["lastName"], PUBLIC_TEXT)
        for treffer in re.finditer(r"Einsle", PUBLIC_TEXT):
            umfeld = PUBLIC_TEXT[max(0, treffer.start() - 8):treffer.end() + 4]
            self.assertTrue("Anita Einsle" in umfeld or "anita@einsle" in umfeld,
                            "unerwartete Fundstelle: %r" % umfeld)

    def test_keine_internen_personen_ids(self):
        for p in PEOPLE:
            self.assertNotRegex(PUBLIC_TEXT, r"\b%s\b" % re.escape(p["id"]))

    def test_keine_elternadressen_oder_quellen(self):
        verboten = ["@gmx", "@gmail", "@hotmail", "@web.de", "@chello", "@yahoo",
                    "cn-architekten", "bischof-fuchs", "vlkh.at", "htl-bregenz",
                    ".pdf", "input/", "Deuringstra", "+43", "05574", "Lektor",
                    "Herbstferien", "Graz", "Aquamundo", "Spag", "Spaghetti"]
        for token in verboten:
            with self.subTest(token=token):
                self.assertNotIn(token, PUBLIC_TEXT)

    def test_nur_die_freigegebene_kontaktadresse(self):
        mails = set(re.findall(r"[\w.+-]+@[\w.-]+\.\w+", PUBLIC_TEXT))
        self.assertEqual(mails, {"anita@einsle.at"})

    def test_keine_internen_regel_oder_quellendaten(self):
        for token in ["rules.json", "people.json", "plan.internal", "searchLog",
                      "assignmentsByPerson", "Rueckmeldung", "R-08", "V09",
                      "openQuestions", "sourceMappingURL"]:
            with self.subTest(token=token):
                self.assertNotIn(token, PUBLIC_TEXT)

    def test_keine_source_maps_im_verzeichnis(self):
        self.assertFalse([f for f in PUBLIC_FILES if f.endswith(".map")])
        self.assertEqual(sorted(PUBLIC_FILES),
                         ["app.js", "index.html", "plan.json", "search.js", "styles.css"])

    def test_alias_und_abwesenheitsgruende_nicht_exportiert(self):
        for alias in PEOPLE_DOC["aliases"]:
            self.assertNotIn(alias["variant"], PUBLIC_TEXT)


class ExportDecktSichMitPlan(unittest.TestCase):
    def test_acht_gottesdienste_mit_korrekten_zeiten(self):
        self.assertEqual([s["id"] for s in PUB["services"]], V.SERVICE_ORDER)
        for svc in PUB["services"]:
            ref = V.SERVICES[svc["id"]]
            self.assertEqual(svc["date"], ref["date"])
            self.assertEqual(svc["time"], ref["time"])
            self.assertEqual(svc["weekday"], "Sonntag")
        self.assertEqual(PUB["services"][-1]["time"], "19:00")

    def test_familienmesse_gekennzeichnet(self):
        fam = [s for s in PUB["services"] if s["familyMass"]]
        self.assertEqual(len(fam), 1)
        self.assertEqual((fam[0]["date"], fam[0]["time"]), ("2026-10-18", "11:00"))

    def test_besetzung_stimmt_mit_validiertem_plan_ueberein(self):
        errors, _, _ = V.validate(INTERNAL["assignments"], PEOPLE)
        self.assertEqual(errors, [])
        for svc in PUB["services"]:
            expected = sorted(DISPLAY[pid] for pid in INTERNAL["assignments"][svc["id"]])
            self.assertEqual(sorted(svc["servers"]), expected, svc["id"])

    def test_gesamtplan_steht_vollstaendig_im_html(self):
        """Ohne JavaScript lesbar: jeder Name steht statisch im HTML."""
        with open(os.path.join(PUBLIC, "index.html"), encoding="utf-8") as fh:
            page = fh.read()
        for svc in PUB["services"]:
            for name in svc["servers"]:
                self.assertIn('data-name="%s"' % name, page)
        self.assertEqual(page.count('class="mass"'), 8)
        self.assertEqual(page.count('<li data-name='), sum(len(s["servers"]) for s in PUB["services"]))

    def test_anzeigenamen_sind_eindeutig(self):
        namen = {n for s in PUB["services"] for n in s["servers"]}
        self.assertEqual(len(namen), len({DISPLAY[p] for p in INTERNAL["counts"] if INTERNAL["counts"][p]}))

    def test_status_ist_als_entwurf_gekennzeichnet(self):
        self.assertIn("Entwurf", PUB["status"])
        self.assertIn("nicht", PUB["status"])
        with open(os.path.join(PUBLIC, "index.html"), encoding="utf-8") as fh:
            self.assertIn("Entwurf", fh.read())

    def test_zeitraum_stand_und_hinweis_vorhanden(self):
        with open(os.path.join(PUBLIC, "index.html"), encoding="utf-8") as fh:
            page = fh.read()
        self.assertIn("Ministrantenplan Oktober 2026", page)
        self.assertIn("Gültig vom 1. Oktober 2026 bis 31. Oktober 2026", page)
        self.assertIn("Ab Sonntag, 25. Oktober, beginnt die Abendmesse um 19:00 Uhr.", page)
        self.assertIn("Stand: %s" % PUB["updated"], page)
        self.assertIn("Planversion %s" % PUB["planVersion"], page)
        self.assertIn('href="mailto:anita@einsle.at"', page)


if __name__ == "__main__":
    unittest.main(verbosity=2)


class LayoutUndDruck(unittest.TestCase):
    """Statische Pruefung der Layout- und Druckvorgaben.

    Diese Tests pruefen die dafuer notwendigen Regeln in HTML und CSS.
    Sie ersetzen KEINE visuelle Browserpruefung; diese steht noch aus
    (siehe out/pruefbericht.md, Abschnitt 10).
    """

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(PUBLIC, "styles.css"), encoding="utf-8") as fh:
            cls.css = fh.read()
        with open(os.path.join(PUBLIC, "index.html"), encoding="utf-8") as fh:
            cls.html = fh.read()

    def test_viewport_und_sprache_gesetzt(self):
        self.assertIn('<html lang="de">', self.html)
        self.assertIn('name="viewport" content="width=device-width, initial-scale=1"', self.html)

    def test_desktop_zwei_spalten_je_sonntag(self):
        self.assertRegex(self.css, r"\.day-grid\s*\{[^}]*grid-template-columns:\s*1fr 1fr")
        self.assertEqual(self.html.count('class="day-grid"'), 4)
        tage = re.split(r'<section class="day"', self.html)[1:]
        self.assertEqual(len(tage), 4)
        for tag in tage:
            self.assertEqual(tag.count('<article class="mass"'), 2)

    def test_mobil_untereinander_ohne_horizontales_scrollen(self):
        mobile = re.search(r"@media \(max-width: 760px\) \{(.*?)\n\}\n", self.css, re.S)
        self.assertIsNotNone(mobile, "Mobiler Breakpoint fehlt")
        self.assertRegex(mobile.group(1), r"\.day-grid\s*\{\s*grid-template-columns:\s*1fr;")
        self.assertRegex(self.css, r"body\s*\{[^}]*overflow-x:\s*hidden")

    def test_lange_namen_brechen_um(self):
        self.assertRegex(self.css, r"\.servers li\s*\{[^}]*overflow-wrap:\s*anywhere")
        self.assertRegex(self.css, r"\.servers\s*\{[^}]*flex-wrap:\s*wrap")

    def test_grosse_familienmesse_ohne_begrenzung_dargestellt(self):
        fam = [s for s in PUB["services"] if s["familyMass"]][0]
        self.assertGreater(len(fam["servers"]), 8)
        block = re.search(r'<article class="mass" id="%s">(.*?)</article>' % fam["id"],
                          self.html, re.S).group(1)
        self.assertEqual(block.count("<li data-name="), len(fam["servers"]))
        self.assertNotRegex(self.css, r"\.servers\s*\{[^}]*max-height")

    def test_druckansicht_blendet_bedienelemente_aus_und_zeigt_den_umfang(self):
        printblock = re.search(r"@media print \{(.*)\n\}\n", self.css, re.S).group(1)
        self.assertIn(".filter", printblock)
        self.assertIn("display: none !important", printblock)
        self.assertRegex(printblock, r"\.print-scope\s*\{\s*display:\s*block")
        self.assertIn('id="print-scope"', self.html)
        self.assertRegex(self.css, r"\.print-scope\s*\{\s*display:\s*none")

    def test_druckausgabe_enthaelt_zeitraum_stand_zeiten_und_kontakt(self):
        fuss = re.search(r'<section class="contact">(.*?)</section>', self.html, re.S).group(1)
        self.assertIn("1. Oktober 2026 bis 31. Oktober 2026", fuss)
        self.assertIn("Stand: %s" % PUB["updated"], fuss)
        self.assertIn("19:00 Uhr", fuss)
        self.assertIn("mailto:anita@einsle.at", fuss)
        self.assertNotIn("print-hide", re.search(
            r'<section class="contact">', self.html).group(0))

    def test_fokusmarkierung_und_bedienelementgroesse(self):
        self.assertRegex(self.css, r":focus-visible\s*\{[^}]*outline:")
        self.assertRegex(self.css, r"button\s*\{[^}]*min-height:\s*46px")
        self.assertRegex(self.css, r'input\[type="search"\], select\s*\{[^}]*min-height:\s*46px')

    def test_hervorhebung_nicht_allein_durch_farbe(self):
        self.assertRegex(self.css, r"\.servers li\.is-match\s*\{[^}]*font-weight:\s*700")
        self.assertRegex(self.css, r"\.servers li\.is-match\s*\{[^}]*border-left-width")
        self.assertIn('<span class="match-flag">', self.html)

    def test_keine_externen_ressourcen(self):
        self.assertNotIn("http://", self.html.replace("http://www.w3.org", ""))
        for token in ["https://", "cdn.", "fonts.googleapis"]:
            self.assertNotIn(token, self.css)
        self.assertEqual(re.findall(r'<script src="([^"]+)"', self.html),
                         ["search.js", "app.js"])
        self.assertEqual(re.findall(r'<link rel="stylesheet" href="([^"]+)"', self.html),
                         ["styles.css"])
