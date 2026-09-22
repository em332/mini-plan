# -*- coding: utf-8 -*-
"""Eigenstaendige fachliche Validierung eines Ministrantenplans.

Bewusst UNABHAENGIG von src/generate.py und src/model.py: dieses Modul
importiert weder die Zuteilungslogik noch deren abgeleitete Verfuegbarkeiten,
sondern fuehrt eine eigene Regeltabelle mit. Es prueft jeden beliebigen,
auch von Hand veraenderten Plan.

Aufruf:  python3 src/validate.py [pfad/zum/plan.json]
"""
import json
import os
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --------------------------------------------------------------------------
# Eigene Regeltabelle (Quelle: Auftrag Abschnitte 2, 3.1-3.6, 4)
# --------------------------------------------------------------------------
SERVICES = {
    "G1": {"date": "2026-10-04", "time": "11:00", "daypart": "vormittag", "min": 8, "family": False},
    "G2": {"date": "2026-10-04", "time": "19:30", "daypart": "abend",     "min": 6, "family": False},
    "G3": {"date": "2026-10-11", "time": "11:00", "daypart": "vormittag", "min": 8, "family": False},
    "G4": {"date": "2026-10-11", "time": "19:30", "daypart": "abend",     "min": 6, "family": False},
    "G5": {"date": "2026-10-18", "time": "11:00", "daypart": "vormittag", "min": 8, "family": True},
    "G6": {"date": "2026-10-18", "time": "19:30", "daypart": "abend",     "min": 6, "family": False},
    "G7": {"date": "2026-10-25", "time": "11:00", "daypart": "vormittag", "min": 8, "family": False},
    "G8": {"date": "2026-10-25", "time": "19:00", "daypart": "abend",     "min": 6, "family": False},
}
SERVICE_ORDER = ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8"]
MORNING = [s for s in SERVICE_ORDER if SERVICES[s]["daypart"] == "vormittag"]
EVENING = [s for s in SERVICE_ORDER if SERVICES[s]["daypart"] == "abend"]

MAX_PER_MONTH = 2                       # R-GLOBAL-MAX-MONTH
MIN_TOTAL_ASSIGNMENTS = 56              # 4x8 + 4x6
MAX_PER_SERVICE = None                  # R-GLOBAL-NO-MAX: keine Hoechstzahl

# Nur um 11:00 Uhr (Abschnitt 3.2; Ida abgeleitet ueber Paarbindung R-22)
MORNING_ONLY = {"p01", "p02", "p03", "p09", "p17", "p24", "p27", "p28", "p34"}
# Nur abends (Abschnitt 3.2 / 3.5)
EVENING_ONLY = {"p13", "p14", "p05", "p06"}

# Ausschliesslich diese Gottesdienste zulaessig
ONLY_SERVICES = {
    "p01": {"G5"}, "p02": {"G5"},                       # R-05 Bereuter
    "p09": {"G1"},                                      # R-04 Christina
    "p24": {"G5"}, "p34": {"G5"},                       # R-11 Magdalena / R-21 Ida
    "p35": {"G4", "G5"},                                # R-07 Ferdinand
    "p25": {"G3", "G4", "G5", "G6"},                    # R-12 Ocvirk
    "p26": {"G3", "G4", "G5", "G6"},
    "p32": {"G3", "G4", "G5", "G6"},                    # R-08 Schmidgall (nach Sperren)
    "p33": {"G3", "G4", "G5", "G6"},
    "p05": {"G4"}, "p06": {"G4"},                       # R-10 Felix / Magnus
}

# Ausdrueckliche Sperren
BLOCKED = {
    "p03": {"G1", "G2"},                                # R-02 Zita 02.-04.10.
    "p17": {"G1", "G2"},                                # R-17 Olivia nicht erster Termin
    "p27": {"G7", "G8"}, "p28": {"G7", "G8"},           # R-03 Ottersbach 24.10.-01.11.
    "p37": {"G7", "G8"}, "p38": {"G7", "G8"},           # R-06 Woess 24.10.-01.11.
    "p04": {"G7", "G8"},                                # R-09 Greta 25.10.
    "p31": {"G7", "G8"},                                # R-14 Remus 24.10.-02.11.
    "p29": {"G7", "G8"},                                # R-16 Anna Pfefferkorn ab 25.10.
    "p21": {"G3", "G7"}, "p22": {"G3", "G7"},           # R-01 Kramer: nur 11:00 gesperrt
    "p32": {"G1", "G2", "G7", "G8"},                    # R-08 Schmidgall 04./05.10. + Ferien
    "p33": {"G1", "G2", "G7", "G8"},
    "p05": {"G1", "G2"}, "p06": {"G1", "G2"},           # R-10 Brunner 04.10.
}

MUST_SERVE = {                                          # Pflichttermine
    "p32": {"G3"}, "p33": {"G3"},                       # R-08 Lektorendienst Markus
    "p05": {"G4"}, "p06": {"G4"},                       # R-10
    "p35": {"G4"}, "p10": {"G4"}, "p11": {"G4"}, "p16": {"G4"},  # R-19 / R-20
}
EXACT_COUNT = {"p05": 1, "p06": 1}                      # R-10 genau ein Einsatz

PAIRS = [("p01", "p02"), ("p19", "p20"), ("p32", "p33"), ("p24", "p34"), ("p37", "p38")]
DIRECTED_GROUPS = [("p06", ["p10", "p11", "p16"]),      # R-19 Magnus + Begleiter
                   ("p05", ["p35", "p06"])]             # R-20 Felix + Ferdinand + Magnus

# Personen ganz ohne Rueckmeldung und ohne Einschraenkung: muessen einteilbar bleiben
NO_FEEDBACK = {"p07", "p08", "p12", "p15", "p18", "p23", "p30", "p36"}

PREFERENCES = ["P-01-REDL-SCHARINGER", "P-02-LARA-OLIVIA", "P-03-KONZETT-WISH"]


# --------------------------------------------------------------------------
def allowed_services(pid):
    """Zulaessige Gottesdienste einer Person nach dieser Regeltabelle."""
    allowed = set(ONLY_SERVICES.get(pid, SERVICE_ORDER))
    if pid in MORNING_ONLY:
        allowed &= set(MORNING)
    if pid in EVENING_ONLY:
        allowed &= set(EVENING)
    allowed -= BLOCKED.get(pid, set())
    return allowed


def _weekday_name(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    return ["Montag", "Dienstag", "Mittwoch", "Donnerstag",
            "Freitag", "Samstag", "Sonntag"][date(y, m, d).weekday()]


def validate(plan, people):
    """Prueft den Plan. Gibt (fehler, hinweise, kennzahlen) zurueck."""
    errors, notes = [], []
    ids = {p["id"] for p in people}

    def err(code, msg):
        errors.append({"code": code, "message": msg})

    def note(code, msg):
        notes.append({"code": code, "message": msg})

    # --- V01 Stammliste -----------------------------------------------
    if len(people) != 38:
        err("V01", "Stammliste hat %d statt 38 Personen" % len(people))
    if len(ids) != len(people):
        err("V01", "Doppelte Personen-IDs in der Stammliste")
    displays = [p["display"] for p in people]
    if len(set(displays)) != len(displays):
        err("V01", "Anzeigenamen sind nicht eindeutig")
    for a, b in (("p05", "p06"), ("p19", "p25")):
        if a in ids and b in ids and a == b:
            err("V01", "Personen %s und %s duerfen nicht zusammengefuehrt werden" % (a, b))
    if any("Maya" in (p["firstName"] + p["lastName"]) for p in people):
        err("V01", "Zusaetzliche Person 'Maya' in der Stammliste")

    # --- V02 Gottesdienste --------------------------------------------
    if set(plan.keys()) != set(SERVICE_ORDER):
        err("V02", "Der Plan enthaelt nicht genau die acht regulaeren Gottesdienste: %s"
            % sorted(plan.keys()))
    for sid in SERVICE_ORDER:
        if sid not in plan:
            continue
        wd = _weekday_name(SERVICES[sid]["date"])
        if wd != "Sonntag":
            err("V02", "%s (%s) ist ein %s, kein Sonntag" % (sid, SERVICES[sid]["date"], wd))
    if "G8" in plan and SERVICES["G8"]["time"] != "19:00":
        err("V02", "Abendmesse am 25.10. muss um 19:00 Uhr beginnen")
    if SERVICES["G5"]["date"] != "2026-10-18" or SERVICES["G5"]["time"] != "11:00" \
            or not SERVICES["G5"]["family"]:
        err("V02", "Familienmesse muss am 18.10.2026 um 11:00 Uhr sein")

    # --- V03/V04 Besetzungszahlen -------------------------------------
    total = 0
    for sid in SERVICE_ORDER:
        roster = plan.get(sid, [])
        total += len(roster)
        need = SERVICES[sid]["min"]
        if len(roster) < need:
            err("V03", "%s (%s %s) unterbesetzt: %d von mindestens %d"
                % (sid, SERVICES[sid]["date"], SERVICES[sid]["time"], len(roster), need))
        if MAX_PER_SERVICE is not None and len(roster) > MAX_PER_SERVICE:
            err("V04", "%s ueberbesetzt" % sid)
    if total < MIN_TOTAL_ASSIGNMENTS:
        err("V03", "Nur %d Personeneinsaetze, mindestens %d erforderlich"
            % (total, MIN_TOTAL_ASSIGNMENTS))

    # --- V05/V06 Belegung ---------------------------------------------
    for sid in SERVICE_ORDER:
        roster = plan.get(sid, [])
        for pid in roster:
            if pid not in ids:
                err("V05", "%s: unbekannte Personen-ID %s" % (sid, pid))
        if len(set(roster)) != len(roster):
            dup = sorted({p for p in roster if roster.count(p) > 1})
            err("V06", "%s: Person mehrfach in derselben Messe: %s" % (sid, ", ".join(dup)))

    by_person = {pid: [s for s in SERVICE_ORDER if pid in plan.get(s, [])] for pid in ids}

    # --- V07 Monatsobergrenze -----------------------------------------
    for pid in sorted(ids):
        n = len(by_person[pid])
        if n > MAX_PER_MONTH:
            err("V07", "%s hat %d Einsaetze, erlaubt sind hoechstens %d"
                % (pid, n, MAX_PER_MONTH))

    # --- V08 Zwei Dienste am selben Sonntag (Planungsvorsicht) --------
    for pid in sorted(ids):
        days = [SERVICES[s]["date"] for s in by_person[pid]]
        for d in sorted(set(days)):
            if days.count(d) > 1:
                note("V08", "%s ist am %s zweimal eingeteilt (Planungsvorsicht, "
                            "Zulaessigkeit waere zu klaeren)" % (pid, d))

    # --- V09 Verfuegbarkeit, Tageszeit, Sperren ------------------------
    for pid in sorted(ids):
        allowed = allowed_services(pid)
        for s in by_person[pid]:
            if s not in allowed:
                reason = []
                if pid in MORNING_ONLY and SERVICES[s]["daypart"] != "vormittag":
                    reason.append("nur 11:00 Uhr zulaessig")
                if pid in EVENING_ONLY and SERVICES[s]["daypart"] != "abend":
                    reason.append("nur Abendmesse zulaessig")
                if s in BLOCKED.get(pid, set()):
                    reason.append("ausdrueckliche Sperre")
                if pid in ONLY_SERVICES and s not in ONLY_SERVICES[pid]:
                    reason.append("ausserhalb der gemeldeten Verfuegbarkeit")
                err("V09", "%s ist in %s (%s %s) eingeteilt: %s"
                    % (pid, s, SERVICES[s]["date"], SERVICES[s]["time"],
                       "; ".join(reason) or "nicht zulaessig"))

    # --- V10 Pflichttermine --------------------------------------------
    for pid, musts in sorted(MUST_SERVE.items()):
        for s in sorted(musts):
            if s not in by_person.get(pid, []):
                err("V10", "%s fehlt beim Pflichttermin %s (%s %s)"
                    % (pid, s, SERVICES[s]["date"], SERVICES[s]["time"]))

    # --- V11 Genaue Einsatzanzahl (Felix, Magnus) ----------------------
    for pid, cnt in sorted(EXACT_COUNT.items()):
        got = len(by_person.get(pid, []))
        if got != cnt:
            err("V11", "%s muss genau %d Einsatz haben, hat aber %d" % (pid, cnt, got))

    # --- V12 Paarbindungen ----------------------------------------------
    for a, b in PAIRS:
        sa, sb = set(by_person.get(a, [])), set(by_person.get(b, []))
        if sa != sb:
            err("V12", "Paarbindung %s/%s verletzt: %s vs. %s"
                % (a, b, sorted(sa) or "-", sorted(sb) or "-"))

    # --- V13 Gerichtete Gruppenregeln -----------------------------------
    for leader, companions in DIRECTED_GROUPS:
        for s in by_person.get(leader, []):
            for c in companions:
                if c not in plan.get(s, []):
                    err("V13", "%s ist in %s eingeteilt, Pflichtbegleiter %s fehlt dort"
                        % (leader, s, c))
    # Felix: beide Paarbedingungen in DERSELBEN Messe
    felix = by_person.get("p05", [])
    if len(felix) == 1:
        s = felix[0]
        if not ({"p35", "p06"} <= set(plan.get(s, []))):
            err("V13", "Felix erfuellt seine beiden Paarbedingungen nicht in derselben Messe")
    # Begleiter duerfen zusaetzlich ohne Magnus dienen -> kein Fehler
    magnus = set(by_person.get("p06", []))
    for c in ("p10", "p11", "p16"):
        extra = set(by_person.get(c, [])) - magnus
        if extra:
            note("V13", "%s hat einen zusaetzlichen Einsatz ohne Magnus (%s) - zulaessig"
                 % (c, ", ".join(sorted(extra))))

    # --- V14 Standardverfuegbarkeit --------------------------------------
    for pid in sorted(NO_FEEDBACK):
        if allowed_services(pid) != set(SERVICE_ORDER):
            err("V14", "%s hat keine Rueckmeldung und keine Einschraenkung, "
                       "muss aber grundsaetzlich einteilbar bleiben" % pid)

    # --- V15 Wuensche (nur Dokumentation, keine Pflichtverletzung) -------
    prefs = {
        "P-01-REDL-SCHARINGER": any("p30" in plan.get(s, []) and "p31" in plan.get(s, [])
                                    for s in SERVICE_ORDER),
        "P-02-LARA-OLIVIA": "p02" in plan.get("G5", []) and "p17" in plan.get("G5", []),
        "P-03-KONZETT-WISH": sorted(by_person.get("p19", [])) == ["G5", "G8"],
    }
    for name, ok in sorted(prefs.items()):
        if not ok:
            note("V15", "Wunsch %s nicht erfuellt (Praeferenz, keine Pflichtverletzung)" % name)

    metrics = {
        "totalAssignments": total,
        "perService": {s: len(plan.get(s, [])) for s in SERVICE_ORDER},
        "perPerson": {pid: len(by_person[pid]) for pid in sorted(ids)},
        "familyMassSize": len(plan.get("G5", [])),
        "preferences": prefs,
        "unassigned": sorted(pid for pid in ids if not by_person[pid]),
    }
    return errors, notes, metrics


# --------------------------------------------------------------------------
def load_plan(path):
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    return doc.get("assignments", doc)


def main():
    plan_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "out", "plan.internal.json")
    with open(os.path.join(ROOT, "data", "people.json"), encoding="utf-8") as fh:
        people = json.load(fh)["people"]
    plan = load_plan(plan_path)
    errors, notes, metrics = validate(plan, people)

    print("Validierung: %s" % plan_path)
    print("  Gesamteinsaetze: %d   Familienmesse: %d Personen"
          % (metrics["totalAssignments"], metrics["familyMassSize"]))
    for s in SERVICE_ORDER:
        print("  %s %s %s: %2d" % (s, SERVICES[s]["date"], SERVICES[s]["time"],
                                   metrics["perService"][s]))
    if notes:
        print("\nHinweise (%d):" % len(notes))
        for n in notes:
            print("  [%s] %s" % (n["code"], n["message"]))
    if errors:
        print("\nFEHLER (%d):" % len(errors))
        for e in errors:
            print("  [%s] %s" % (e["code"], e["message"]))
        return 1
    print("\nErgebnis: alle Pflichtregeln eingehalten.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
