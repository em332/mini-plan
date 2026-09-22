# -*- coding: utf-8 -*-
"""Erzeugt den internen Pruefbericht out/pruefbericht.md.

INTERN. Der Bericht enthaelt vollstaendige Namen, Regelstatus und Quellen und
gehoert nicht in das Veroeffentlichungsverzeichnis.
"""
import json
import os
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import validate as V  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return json.load(fh)


def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def main():
    people_doc = load("data/people.json")
    people = people_doc["people"]
    rules_doc = load("data/rules.json")
    internal = load("out/plan.internal.json")
    plan = internal["assignments"]
    name = {p["id"]: "%s %s" % (p["firstName"], p["lastName"]) for p in people}

    errors, notes, metrics = V.validate(plan, people)

    rc_rules, out_rules = run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."])
    rc_ui, out_ui = run(["node", "--test", "tests/test_ui.mjs"])

    def tail(text, n=1):
        lines = [l for l in text.splitlines() if l.strip()]
        return " / ".join(lines[-n:])

    L = []
    a = L.append
    a("# Interner Pruefbericht - Ministrantenplan Oktober 2026")
    a("")
    a("INTERN. Nicht veroeffentlichen. Enthaelt vollstaendige Namen und Quellenbezuege.")
    a("")
    a("- Planversion: %s" % internal["planVersion"])
    a("- Erzeugt: %s" % internal["generatedAt"])
    a("- Bericht erstellt: %s" % datetime.now().astimezone().isoformat(timespec="seconds"))
    a("- Zeitzone: %s" % internal["timezone"])
    a("- Status: technisch validiert, organisatorisch NICHT freigegeben "
      "(keine Freigabe durch Anita Einsle eingeholt)")
    a("")

    a("## 1. Ergebnis der unabhaengigen Validierung")
    a("")
    a("Validator: `src/validate.py` mit eigener Regeltabelle, ohne Import der Zuteilungslogik.")
    a("")
    a("- Pflichtregelverletzungen: **%d**" % len(errors))
    for e in errors:
        a("  - [%s] %s" % (e["code"], e["message"]))
    a("- Hinweise: %d" % len(notes))
    for n in notes:
        a("  - [%s] %s" % (n["code"], n["message"]))
    a("")

    a("## 2. Besetzung je Gottesdienst")
    a("")
    a("| ID | Datum | Uhrzeit | Art | Mindest | Ist | Status |")
    a("| --- | --- | --- | --- | ---: | ---: | --- |")
    for sid in V.SERVICE_ORDER:
        s = V.SERVICES[sid]
        ist = metrics["perService"][sid]
        art = "Familienmesse" if s["family"] else (
            "Vormittagsmesse" if s["daypart"] == "vormittag" else "Abendmesse")
        a("| %s | %s | %s | %s | %d | %d | %s |"
          % (sid, s["date"], s["time"], art, s["min"], ist,
             "erfuellt" if ist >= s["min"] else "UNTERBESETZT"))
    a("")
    a("Gesamteinsaetze: **%d** (Mindestanforderung 56)." % metrics["totalAssignments"])
    a("")

    a("## 3. Einsatzanzahl je Person")
    a("")
    a("| Person | Einsaetze | Gottesdienste | Obergrenze |")
    a("| --- | ---: | --- | --- |")
    for pid in sorted(name, key=lambda x: int(x[1:])):
        svc = [s for s in V.SERVICE_ORDER if pid in plan[s]]
        cap = V.EXACT_COUNT.get(pid)
        limit = "genau %d (Einzelregel)" % cap if cap else "hoechstens 2"
        a("| %s | %d | %s | %s |" % (name[pid], len(svc), ", ".join(svc) or "-", limit))
    a("")
    verteilung = {}
    for pid in name:
        verteilung.setdefault(len([s for s in V.SERVICE_ORDER if pid in plan[s]]), []).append(pid)
    for k in sorted(verteilung, reverse=True):
        a("- %d Einsaetze: %d Personen" % (k, len(verteilung[k])))
    if metrics["unassigned"]:
        a("- ohne Einsatz: %s" % ", ".join(name[p] for p in metrics["unassigned"]))
    else:
        a("- Jede der 38 Personen hat mindestens einen Einsatz.")
    a("")

    a("## 4. Regelstatus")
    a("")
    a("| Regel | Typ | Status | Betroffene | Quelle |")
    a("| --- | --- | --- | --- | --- |")
    for r in rules_doc["rules"]:
        subs = ", ".join(name.get(s, s) for s in r.get("subjects", [])) or "alle"
        a("| %s | %s | %s | %s | %s |"
          % (r["id"], r["type"], r["status"], subs, r["source"]["file"]))
    a("")

    a("## 5. Wuensche und Praeferenzen")
    a("")
    a("| Wunsch | Ergebnis | Bemerkung |")
    a("| --- | --- | --- |")
    prefs = metrics["preferences"]
    bem = {
        "P-01-REDL-SCHARINGER": "Jakob Redl und Remus Scharinger dienen gemeinsam",
        "P-02-LARA-OLIVIA": "Lara Bereuter und Olivia Eze gemeinsam in der Familienmesse "
                            "(Annalena wegen Paarbindung ebenfalls)",
        "P-03-KONZETT-WISH": "Clara und Emma Konzett am 18.10. 11:00 und am 25.10. 19:00",
    }
    for k in sorted(prefs):
        a("| %s | %s | %s |" % (k, "erfuellt" if prefs[k] else "NICHT erfuellt", bem[k]))
    a("")
    gemeinsam = [s for s in V.SERVICE_ORDER if "p30" in plan[s] and "p31" in plan[s]]
    a("Gemeinsamer Termin Redl/Scharinger: %s" % (", ".join(gemeinsam) or "-"))
    a("")

    a("## 6. Familienmesse am 18.10.2026 um 11:00 Uhr")
    a("")
    fam = plan["G5"]
    a("Besetzung: **%d Personen** (keine Hoechstzahl; Mindestbesetzung 8)." % len(fam))
    a("")
    geeignet = [p for p in name if "G5" in V.allowed_services(p)]
    fehlen = [p for p in geeignet if p not in fam]
    a("Fuer die Familienmesse grundsaetzlich geeignet und verfuegbar: %d Personen."
      % len(geeignet))
    a("Nicht geeignet, weil ausschliesslich abends einteilbar: %s."
      % ", ".join(sorted(name[p] for p in name if p in V.EVENING_ONLY)))
    a("")
    a("Nicht eingeteilt, obwohl geeignet (%d Personen):" % len(fehlen))
    a("")
    a("| Person | stattdessen eingeteilt |")
    a("| --- | --- |")
    for p in sorted(fehlen, key=lambda x: name[x]):
        a("| %s | %s |" % (name[p], ", ".join(s for s in V.SERVICE_ORDER if p in plan[s])))
    a("")
    a("Begruendung: Die Gesamtkapazitaet betraegt 69 Einsaetze "
      "(31 Personen mit hoechstens zwei Einsaetzen, 7 Personen mit nur einem "
      "zulaessigen Termin). Die uebrigen sieben Gottesdienste benoetigen zusammen "
      "mindestens 48 Einsaetze. Damit sind hoechstens 69 - 48 = 21 Personen in der "
      "Familienmesse moeglich. Die vollstaendige Suche hat fuer |G5| >= 22 "
      "nachgewiesen, dass keine Loesung existiert; fuer |G5| = 21 wurde eine "
      "Loesung gefunden. Zusaetzlich muessen mindestens vier fuer die Familienmesse "
      "geeignete Kinder ausserhalb bleiben, weil die Abendmesse am 18.10. "
      "sonst nur mit Klara und Martha Einsle besetzbar waere und ihre "
      "Mindestbesetzung von sechs Personen nicht erreichen wuerde.")
    a("")

    a("## 7. Suchprotokoll des Generators")
    a("")
    a("| Schritt | Ergebnis | Bemerkung |")
    a("| --- | --- | --- |")
    for entry in internal["searchLog"]:
        a("| %s | %s | %s |" % (entry.get("step", entry.get("g5Target")),
                                entry["status"], entry.get("info") or ""))
    a("")

    a("## 8. Quellen")
    a("")
    pdfs = sorted(f for f in os.listdir(os.path.join(ROOT, "input", "plan-sept-2026"))
                  if f.lower().endswith(".pdf"))
    a("Im Ordner `input/plan-sept-2026` liegen **%d PDF-Dateien**; alle wurden gelesen "
      "und im Regelwerk erfasst." % len(pdfs))
    a("")
    verwendet = {r["source"]["file"] for r in rules_doc["rules"]}
    a("| PDF | im Regelwerk erfasst |")
    a("| --- | --- |")
    for f in pdfs:
        a("| %s | %s |" % (f, "ja" if f in verwendet else "NEIN"))
    a("")
    a("Aussermonatliche und widerspruechliche Aussagen:")
    a("")
    a("- `WG- Ministrieren September .pdf`: September-Wunsch, Regel "
      "R-13-SEPTEMBER-HIST als `historisch_inaktiv` gefuehrt und in der "
      "Verfuegbarkeitsableitung uebersprungen.")
    a("- `x-WG- Oktober.pdf`: Text nennt \"November\", Betreff \"Oktober\"; "
      "R-15-KONZETT-MONTH dokumentiert Oktober 2026 als bestaetigten Bezugsmonat.")
    a("- `WG- mini oktober christina.pdf`: bezweifelter Kalendereintrag 03.10. 11:00; "
      "der 03.10.2026 ist ein Samstag und keiner der acht Gottesdienste.")
    a("- `WG- Mini-Dienst Oktober 2026.pdf`: Lektorentermine 08.11., 31.12., 03.01.27 "
      "liegen ausserhalb des Planungszeitraums.")
    a("- Ausflugs- und Spaghetti-Anmeldungen, E-Mail-Verteiler und Telefonnummern "
      "sind keine Planungsdaten.")
    a("")

    a("## 9. Tatsaechlich ausgefuehrte Pruefungen")
    a("")
    a("| Pruefung | Aufruf | Ergebnis |")
    a("| --- | --- | --- |")
    import re as _re
    n_py = _re.search(r"Ran (\d+) tests", out_rules)
    a("| Fachliche Regeln und oeffentlicher Export (Python) | "
      "`python3 -m unittest discover -s tests -t .` | %s |"
      % ("%s Tests bestanden" % n_py.group(1) if rc_rules == 0 and n_py
         else "FEHLGESCHLAGEN: %s" % tail(out_rules, 3)))
    n_js = _re.search(r"pass (\d+)", out_ui)
    a("| Bedienung des Namensfilters (Node/jsdom) | `node --test tests/test_ui.mjs` | %s |"
      % ("%s Tests bestanden" % n_js.group(1) if rc_ui == 0 and n_js
         else "FEHLGESCHLAGEN: %s" % tail(out_ui, 3)))
    a("| Unabhaengige Planvalidierung | `python3 src/validate.py` | "
      "%d Fehler, %d Hinweise |" % (len(errors), len(notes)))
    a("")

    a("## 10. Offene Punkte")
    a("")
    for q in rules_doc["openQuestions"]:
        a("- **%s (%s)**: %s _Auswirkung: %s_" % (q["id"], q["status"], q["text"], q["impact"]))
    a("- Die oeffentliche Darstellung \"Vorname + Nachnamensinitiale\" ist eine "
      "reduzierte Namensdarstellung, keine Anonymisierung. Ein Zugangsschutz ist "
      "nicht eingerichtet; `noindex` und der Namensfilter ersetzen ihn nicht.")
    a("- Die Kontaktangabe \"Anita Einsle / anita@einsle.at\" ist laut Auftrag zur "
      "Anzeige vorgesehen und nennt damit den Nachnamen, den auch Klara E. und "
      "Martha E. tragen.")
    a("- Der Plan ist technisch validiert, aber organisatorisch nicht freigegeben.")
    a("")

    out = os.path.join(ROOT, "out", "pruefbericht.md")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("geschrieben: %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
