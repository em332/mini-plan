# -*- coding: utf-8 -*-
"""Automatisierte Tests der kritischen Planungsregeln (Auftrag Abschnitt 10).

Getestet wird der unabhaengige Validator gegen den erzeugten Plan UND gegen
gezielt veraenderte Plaene. Aufruf: python3 -m unittest discover -s tests -v
"""
import copy
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

import validate as V  # noqa: E402

with open(os.path.join(ROOT, "data", "people.json"), encoding="utf-8") as fh:
    PEOPLE = json.load(fh)["people"]
with open(os.path.join(ROOT, "out", "plan.internal.json"), encoding="utf-8") as fh:
    PLAN_DOC = json.load(fh)
PLAN = PLAN_DOC["assignments"]

FREE = ["p07", "p08", "p12", "p15", "p18", "p23", "p30", "p36"]  # ohne Rueckmeldung


def run(plan):
    return V.validate(plan, PEOPLE)


def codes(errors):
    return {e["code"] for e in errors}


def mutate(**changes):
    p = copy.deepcopy(PLAN)
    p.update(changes)
    return p


def spare(plan, service, exclude=()):
    """Eine Person, die in ``service`` noch fehlt und dort zulaessig waere."""
    for pid in FREE:
        if pid not in plan[service] and pid not in exclude:
            return pid
    raise AssertionError("keine Ersatzperson gefunden")


# --------------------------------------------------------------------------
class ErzeugterPlan(unittest.TestCase):
    def test_plan_ist_fehlerfrei(self):
        errors, notes, m = run(PLAN)
        self.assertEqual(errors, [], "Fehler im erzeugten Plan: %s" % errors)

    def test_acht_gottesdienste(self):
        self.assertEqual(sorted(PLAN.keys()), V.SERVICE_ORDER)

    def test_mindestbesetzung_und_summe(self):
        _, _, m = run(PLAN)
        for s in V.MORNING:
            self.assertGreaterEqual(m["perService"][s], 8)
        for s in V.EVENING:
            self.assertGreaterEqual(m["perService"][s], 6)
        self.assertGreaterEqual(m["totalAssignments"], 56)

    def test_alle_wuensche_erfuellt(self):
        _, _, m = run(PLAN)
        self.assertEqual(m["preferences"],
                         {"P-01-REDL-SCHARINGER": True, "P-02-LARA-OLIVIA": True,
                          "P-03-KONZETT-WISH": True})

    def test_niemand_unbekannt_und_keine_38_abweichung(self):
        self.assertEqual(len(PEOPLE), 38)
        ids = {p["id"] for p in PEOPLE}
        for roster in PLAN.values():
            self.assertTrue(set(roster) <= ids)

    def test_reproduzierbar(self):
        """Zweimaliges Erzeugen liefert denselben Plan (kein Zufall)."""
        import generate
        _, plan_a, t_a, _, _ = generate.generate(verbose=False)
        _, plan_b, t_b, _, _ = generate.generate(verbose=False)
        self.assertEqual(t_a, t_b)
        self.assertEqual(plan_a, plan_b)
        self.assertEqual({k: sorted(v) for k, v in plan_a.items()},
                         {k: sorted(v) for k, v in PLAN.items()})


# --------------------------------------------------------------------------
class Besetzungszahlen(unittest.TestCase):
    def test_sieben_vormittags_ist_unterbesetzung(self):
        p = mutate(G1=PLAN["G1"][:7])
        self.assertIn("V03", codes(run(p)[0]))

    def test_fuenf_abends_ist_unterbesetzung(self):
        p = mutate(G2=PLAN["G2"][:5])
        self.assertIn("V03", codes(run(p)[0]))

    def test_zehn_in_familienmesse_ist_gueltig(self):
        """Grosse Besetzung darf nicht allein wegen der Anzahl scheitern."""
        p = copy.deepcopy(PLAN)
        p["G5"] = PLAN["G5"][:10]
        errors = run(p)[0]
        self.assertNotIn("V04", codes(errors))

    def test_sieben_abends_ist_zahlenmaessig_gueltig(self):
        p = copy.deepcopy(PLAN)
        extra = spare(p, "G6")
        p["G6"] = PLAN["G6"] + [extra]
        self.assertNotIn("V04", codes(run(p)[0]))

    def test_keine_kuenstliche_obergrenze_definiert(self):
        self.assertIsNone(V.MAX_PER_SERVICE)


# --------------------------------------------------------------------------
class EinsatzGrenzen(unittest.TestCase):
    def test_dritter_monatseinsatz_faellt_auf(self):
        pid = "p07"
        p = copy.deepcopy(PLAN)
        for s in V.SERVICE_ORDER:
            if pid not in p[s] and s in V.allowed_services(pid):
                p[s] = p[s] + [pid]
            if sum(1 for x in V.SERVICE_ORDER if pid in p[x]) >= 3:
                break
        self.assertIn("V07", codes(run(p)[0]))

    def test_doppelter_eintrag_in_einer_messe(self):
        p = mutate(G1=PLAN["G1"] + [PLAN["G1"][0]])
        self.assertIn("V06", codes(run(p)[0]))

    def test_unbekannte_personen_id(self):
        p = mutate(G1=PLAN["G1"] + ["p99"])
        self.assertIn("V05", codes(run(p)[0]))


# --------------------------------------------------------------------------
class FelixMagnusFerdinand(unittest.TestCase):
    def test_zweiter_einsatz_von_felix_unzulaessig(self):
        p = mutate(G6=PLAN["G6"] + ["p05"])
        self.assertTrue({"V11", "V09"} & codes(run(p)[0]))

    def test_zweiter_einsatz_von_magnus_unzulaessig(self):
        p = mutate(G6=PLAN["G6"] + ["p06"])
        self.assertTrue({"V11", "V09"} & codes(run(p)[0]))

    def test_vormittagseinsatz_von_felix_unzulaessig(self):
        p = mutate(G4=[x for x in PLAN["G4"] if x != "p05"],
                   G5=PLAN["G5"] + ["p05"])
        self.assertIn("V09", codes(run(p)[0]))

    def test_vormittagseinsatz_von_magnus_unzulaessig(self):
        p = mutate(G4=[x for x in PLAN["G4"] if x != "p06"],
                   G5=PLAN["G5"] + ["p06"])
        self.assertIn("V09", codes(run(p)[0]))

    def test_magnus_ohne_begleiter_unzulaessig(self):
        p = copy.deepcopy(PLAN)
        p["G4"] = [x for x in PLAN["G4"] if x != "p10"] + [spare(p, "G4")]
        self.assertIn("V13", codes(run(p)[0]))

    def test_begleiter_zusaetzlich_ohne_magnus_ist_gueltig(self):
        """Paulus, Vincent, Simon duerfen einen zweiten Einsatz ohne Magnus haben."""
        errors, notes, _ = run(PLAN)
        self.assertEqual(errors, [])
        self.assertTrue(any(n["code"] == "V13" and "zulaessig" in n["message"] for n in notes))

    def test_felix_ohne_ferdinand_wird_erkannt(self):
        p = copy.deepcopy(PLAN)
        p["G4"] = [x for x in PLAN["G4"] if x != "p35"] + [spare(p, "G4")]
        self.assertIn("V13", codes(run(p)[0]))

    def test_felix_ohne_magnus_wird_erkannt(self):
        p = copy.deepcopy(PLAN)
        p["G4"] = [x for x in PLAN["G4"] if x != "p06"] + [spare(p, "G4")]
        self.assertIn("V13", codes(run(p)[0]))

    def test_getrennte_termine_fuer_die_beiden_felix_bedingungen_unzulaessig(self):
        """Felix einmal mit Ferdinand, ein zweites Mal mit Magnus: unzulaessig.

        Beide Paarbedingungen muessen in DERSELBEN Messe erfuellt sein.
        """
        p = copy.deepcopy(PLAN)
        p["G4"] = [x for x in PLAN["G4"] if x != "p06"]        # Felix + Ferdinand
        p["G6"] = PLAN["G6"] + ["p05", "p06"]                  # Felix + Magnus, anderer Termin
        errors = codes(run(p)[0])
        self.assertIn("V11", errors)   # Felix haette zwei Einsaetze
        self.assertIn("V13", errors)   # und erfuellt beide Bedingungen nicht gemeinsam

    def test_sechsergruppe_am_11_10_abends_ist_vollstaendig(self):
        self.assertTrue({"p05", "p06", "p35", "p10", "p11", "p16"} <= set(PLAN["G4"]))

    def test_keine_zwei_magnus_einsaetze_gefordert(self):
        self.assertEqual(V.EXACT_COUNT["p06"], 1)
        self.assertEqual(V.EXACT_COUNT["p05"], 1)

    def test_keine_eigenstaendige_magnus_ferdinand_pflicht(self):
        leaders = dict(V.DIRECTED_GROUPS)
        self.assertNotIn("p35", leaders.get("p06", []))


# --------------------------------------------------------------------------
class Tageszeiten(unittest.TestCase):
    def _abend(self, pid):
        p = copy.deepcopy(PLAN)
        for s in V.SERVICE_ORDER:
            p[s] = [x for x in p[s] if x != pid]
        p["G6"] = p["G6"] + [pid]
        return codes(run(p)[0])

    def test_abendeinsatz_von_zita(self):
        self.assertIn("V09", self._abend("p03"))

    def test_abendeinsatz_von_christina(self):
        self.assertIn("V09", self._abend("p09"))

    def test_abendeinsatz_von_olivia(self):
        self.assertIn("V09", self._abend("p17"))

    def test_abendeinsatz_von_magdalena(self):
        self.assertIn("V09", self._abend("p24"))

    def test_abendeinsatz_von_ida(self):
        self.assertIn("V09", self._abend("p34"))

    def test_vormittagseinsatz_von_klara(self):
        p = copy.deepcopy(PLAN)
        for s in V.SERVICE_ORDER:
            p[s] = [x for x in p[s] if x != "p13"]
        p["G1"] = p["G1"] + ["p13"]
        self.assertIn("V09", codes(run(p)[0]))

    def test_vormittagseinsatz_von_martha(self):
        p = copy.deepcopy(PLAN)
        for s in V.SERVICE_ORDER:
            p[s] = [x for x in p[s] if x != "p14"]
        p["G1"] = p["G1"] + ["p14"]
        self.assertIn("V09", codes(run(p)[0]))


# --------------------------------------------------------------------------
class DatumsSperren(unittest.TestCase):
    def test_olivia_am_4_oktober_unzulaessig(self):
        p = mutate(G1=PLAN["G1"] + ["p17"])
        self.assertIn("V09", codes(run(p)[0]))

    def test_christina_an_anderem_sonntag_unzulaessig(self):
        p = mutate(G1=[x for x in PLAN["G1"] if x != "p09"] + [spare(PLAN, "G1")],
                   G3=PLAN["G3"] + ["p09"])
        self.assertIn("V09", codes(run(p)[0]))

    def test_remus_am_25_oktober_unzulaessig(self):
        p = mutate(G7=PLAN["G7"] + ["p31"])
        self.assertIn("V09", codes(run(p)[0]))

    def test_anna_pfefferkorn_am_25_oktober_unzulaessig(self):
        p = mutate(G8=PLAN["G8"] + ["p29"])
        self.assertIn("V09", codes(run(p)[0]))

    def test_greta_am_25_oktober_unzulaessig(self):
        p = mutate(G7=PLAN["G7"] + ["p04"])
        self.assertIn("V09", codes(run(p)[0]))

    def test_annalena_und_lara_nur_am_18_oktober(self):
        p = mutate(G1=PLAN["G1"] + ["p01", "p02"])
        self.assertIn("V09", codes(run(p)[0]))

    def test_zita_am_4_oktober_unzulaessig(self):
        p = mutate(G1=PLAN["G1"] + ["p03"])
        self.assertIn("V09", codes(run(p)[0]))


# --------------------------------------------------------------------------
class Schmidgall(unittest.TestCase):
    def test_lektorendienst_pflichttermin_fehlt(self):
        p = copy.deepcopy(PLAN)
        p["G3"] = [x for x in PLAN["G3"] if x not in ("p32", "p33")] + \
                  [spare(p, "G3"), spare(p, "G3", exclude=(spare(p, "G3"),))]
        p["G6"] = PLAN["G6"] + ["p32", "p33"]
        errors = codes(run(p)[0])
        self.assertIn("V10", errors)

    def test_emilia_marlena_am_11_abends_erfuellt_lektorendienst_nicht(self):
        """Abendmesse am 11.10. ersetzt den Pflichttermin um 11:00 Uhr nicht."""
        p = copy.deepcopy(PLAN)
        p["G3"] = [x for x in PLAN["G3"] if x not in ("p32", "p33")]
        p["G4"] = PLAN["G4"] + ["p32", "p33"]
        self.assertIn("V10", codes(run(p)[0]))

    def test_emilia_am_25_oktober_unzulaessig(self):
        p = mutate(G7=PLAN["G7"] + ["p32"])
        self.assertIn("V09", codes(run(p)[0]))

    def test_marlena_am_4_oktober_unzulaessig(self):
        p = mutate(G1=PLAN["G1"] + ["p33"])
        self.assertIn("V09", codes(run(p)[0]))

    def test_keine_pauschale_herbstferiensperre(self):
        """Kinder ohne eigene Ferienabwesenheit bleiben am 25.10. einteilbar."""
        for pid in FREE:
            self.assertIn("G7", V.allowed_services(pid))
            self.assertIn("G8", V.allowed_services(pid))
        self.assertTrue(set(PLAN["G7"]) & set(FREE))


# --------------------------------------------------------------------------
class PaareUndStandardregel(unittest.TestCase):
    def test_paarbindung_verletzt_wird_erkannt(self):
        p = mutate(G5=[x for x in PLAN["G5"] if x != "p01"])
        self.assertIn("V12", codes(run(p)[0]))

    def test_konzett_paar_bleibt_zusammen(self):
        p = mutate(G8=[x for x in PLAN["G8"] if x != "p19"])
        self.assertIn("V12", codes(run(p)[0]))

    def test_konzett_wunsch_oktober_erfuellt(self):
        self.assertEqual(sorted(s for s in V.SERVICE_ORDER if "p19" in PLAN[s]), ["G5", "G8"])

    def test_konzett_november_wird_nicht_aktiv(self):
        """Der Bezugsmonat ist als Oktober dokumentiert; kein November-Termin."""
        with open(os.path.join(ROOT, "data", "rules.json"), encoding="utf-8") as fh:
            rules = {r["id"]: r for r in json.load(fh)["rules"]}
        r = rules["R-15-KONZETT-MONTH"]
        self.assertEqual(r["payload"]["confirmedMonth"], "2026-10")
        for s in V.SERVICE_ORDER:
            self.assertTrue(V.SERVICES[s]["date"].startswith("2026-10"))

    def test_person_ohne_rueckmeldung_bleibt_einteilbar(self):
        for pid in FREE:
            self.assertEqual(V.allowed_services(pid), set(V.SERVICE_ORDER))

    def test_standardverfuegbarkeit_hebt_sperre_nicht_auf(self):
        self.assertNotIn("G7", V.allowed_services("p31"))   # Remus
        self.assertNotIn("G1", V.allowed_services("p03"))   # Zita
        self.assertNotIn("G8", V.allowed_services("p29"))   # Anna Pfefferkorn

    def test_kramer_abends_ist_zulaessig(self):
        """Die Nein-Angaben der Kramers sperren nur 11:00 Uhr."""
        for pid in ("p21", "p22"):
            self.assertNotIn("G3", V.allowed_services(pid))
            self.assertNotIn("G7", V.allowed_services(pid))
            self.assertIn("G4", V.allowed_services(pid))
            self.assertIn("G8", V.allowed_services(pid))
        p = mutate(G4=PLAN["G4"] + ["p21"])
        self.assertNotIn("V09", codes(run(p)[0]))

    def test_kramer_und_ottersbach_und_ocvirk_ohne_pflichtpaarung(self):
        pairs = {frozenset(x) for x in V.PAIRS}
        for a, b in (("p21", "p22"), ("p27", "p28"), ("p25", "p26")):
            self.assertNotIn(frozenset((a, b)), pairs)

    def test_emma_konzett_und_emma_ocvirk_bleiben_getrennt(self):
        self.assertNotEqual(sorted(s for s in V.SERVICE_ORDER if "p19" in PLAN[s]),
                            sorted(s for s in V.SERVICE_ORDER if "p25" in PLAN[s]))
        names = {p["id"]: p["display"] for p in PEOPLE}
        self.assertNotEqual(names["p19"], names["p25"])

    def test_keine_zusaetzliche_maya(self):
        self.assertEqual(len(PEOPLE), 38)
        self.assertFalse([p for p in PEOPLE if "Maya" in p["firstName"]])


# --------------------------------------------------------------------------
class Gesamtplanpruefung(unittest.TestCase):
    def test_grosse_familienmesse_die_anderswo_unterbesetzung_erzeugt_ist_ungueltig(self):
        p = copy.deepcopy(PLAN)
        moved = PLAN["G6"][:2]
        p["G6"] = PLAN["G6"][2:]
        p["G5"] = PLAN["G5"] + moved
        errors = codes(run(p)[0])
        self.assertIn("V03", errors)

    def test_grosse_familienmesse_die_dritte_einsaetze_erzeugt_ist_ungueltig(self):
        p = copy.deepcopy(PLAN)
        p["G5"] = PLAN["G5"] + [pid for pid in PLAN["G7"] if pid in FREE][:2]
        errors = codes(run(p)[0])
        self.assertTrue({"V07"} & errors)

    def test_generator_beweist_unloesbarkeit_groesserer_familienmesse(self):
        """|G5| >= 22 ist unter allen Pflichtregeln nachweislich unloesbar."""
        import generate
        from model import Model
        status, sols, info = generate.solve(Model(), 22, max_solutions=1)
        self.assertEqual(status, "unloesbar")
        self.assertEqual(sols, [])

    def test_generator_findet_loesung_fuer_maximum(self):
        import generate
        from model import Model
        status, sols, info = generate.solve(Model(), 21, max_solutions=1)
        self.assertEqual(status, "loesung")

    def test_validator_prueft_handplan_unabhaengig(self):
        """Der Validator akzeptiert nicht einfach das Ergebnis des Generators."""
        leer = {s: [] for s in V.SERVICE_ORDER}
        errors = run(leer)[0]
        self.assertTrue(len(errors) >= 8)
        self.assertIn("V03", codes(errors))


if __name__ == "__main__":
    unittest.main(verbosity=2)
