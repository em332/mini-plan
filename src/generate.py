"""Reproduzierbare Erzeugung des Ministrantenplans.

Vollstaendige Tiefensuche ueber Personen- bzw. Paar-Einheiten mit
Kapazitaets- und Besetzungspruning. Die Suche ist deterministisch
(keine Zufallskomponente, feste Sortierung) und kann Unloesbarkeit
innerhalb des Knotenbudgets nachweisen. Wird das Budget erschoepft,
lautet das Ergebnis ausdruecklich "keine Loesung gefunden".
"""
import itertools
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import Model, ROOT  # noqa: E402

NODE_BUDGET = 4_000_000


# ----------------------------------------------------------------------
def build_units(m):
    """Paargebundene Personen bilden eine gemeinsame Einheit."""
    paired = {}
    for a, b in m.pairs:
        paired[a] = b
        paired[b] = a

    units, seen = [], set()
    for pid in m.order:
        if pid in seen:
            continue
        if pid in paired:
            members = sorted([pid, paired[pid]])
        else:
            members = [pid]
        seen.update(members)

        allowed = set(m.service_ids)
        forced = set()
        cap = m.max_month
        for x in members:
            allowed &= m.allowed[x]
            forced |= m.forced[x]
            cap = min(cap, m.cap(x))
        units.append({
            "id": "+".join(members),
            "members": members,
            "w": len(members),
            "allowed": allowed,
            "forced": forced,
            "cap": cap,
        })
    return units


def unit_domain(m, u):
    """Alle zulaessigen Einsatzmengen einer Einheit."""
    allowed = sorted(u["allowed"], key=m.service_ids.index)
    out = []
    for size in range(len(u["forced"]), u["cap"] + 1):
        for combo in itertools.combinations(allowed, size):
            s = set(combo)
            if not u["forced"] <= s:
                continue
            days = [m.sunday_of[x] for x in s]
            if len(set(days)) != len(days):          # max. 1 Dienst je Sonntag
                continue
            out.append(frozenset(s))
    return out


def order_values(m, u, domain, g5_target):
    """Deterministische Wertreihenfolge; bevorzugt gute Loesungen zuerst."""
    scarce = {"G7": 3, "G8": 3, "G5": 4, "G2": 1, "G6": 1}

    def key(s):
        bonus = sum(scarce.get(x, 0) for x in s)
        if u["id"] == "p19+p20" and s == frozenset({"G5", "G8"}):
            bonus += 20                                   # P-03 Konzett-Wunsch
        if "p17" in u["members"] and "G5" in s:
            bonus += 10                                   # P-02 Lara/Olivia
        return (-bonus, -len(s), tuple(sorted(s)))

    return sorted(domain, key=key)


# ----------------------------------------------------------------------
def solve(m, g5_target, node_budget=NODE_BUDGET, max_solutions=200, restrict=None):
    """Sucht Plaene mit |G5| >= g5_target.

    ``restrict`` bildet Einheit-IDs auf ein Praedikat ab und dient dazu,
    einen Wunsch versuchsweise als harte Bedingung zu erzwingen. Bleibt die
    Suche dann erfolglos, ist der Wunsch unter allen Pflichtregeln
    nachweislich nicht erfuellbar.
    """
    restrict = restrict or {}
    units = build_units(m)
    mins = dict(m.min_servers)
    mins["G5"] = max(mins["G5"], g5_target)

    domains = {}
    for u in units:
        dom = unit_domain(m, u)
        pred = restrict.get(u["id"])
        if pred:
            dom = [v for v in dom if pred(v)]
        if not dom:
            return ("unloesbar", [], "Einheit %s hat keine zulaessige Einsatzmenge" % u["id"])
        domains[u["id"]] = order_values(m, u, dom, g5_target)

    units.sort(key=lambda u: (len(domains[u["id"]]), u["id"]))

    n = len(units)
    # Restpotenzial je Gottesdienst und Restkapazitaet ab Index i
    pot = [{s: 0 for s in m.service_ids} for _ in range(n + 1)]
    capleft = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        u = units[i]
        for s in m.service_ids:
            pot[i][s] = pot[i + 1][s] + (u["w"] if s in u["allowed"] else 0)
        best = max(len(d) for d in domains[u["id"]])
        capleft[i] = capleft[i + 1] + best * u["w"]

    counts = {s: 0 for s in m.service_ids}
    choice = [None] * n
    solutions = []
    nodes = [0]
    exhausted = [False]

    def prune(i):
        deficit = 0
        for s in m.service_ids:
            need = mins[s] - counts[s]
            if need > 0:
                if need > pot[i][s]:
                    return True
                deficit += need
        return deficit > capleft[i]

    def rec(i):
        if nodes[0] > node_budget:
            exhausted[0] = True
            return
        nodes[0] += 1
        if prune(i):
            return
        if i == n:
            solutions.append(list(choice))
            return
        u = units[i]
        for val in domains[u["id"]]:
            for s in val:
                counts[s] += u["w"]
            choice[i] = (u, val)
            rec(i + 1)
            for s in val:
                counts[s] -= u["w"]
            if len(solutions) >= max_solutions or exhausted[0]:
                return
        choice[i] = None

    rec(0)
    if solutions:
        return ("loesung", solutions, None)
    if exhausted[0]:
        return ("keine_loesung_gefunden", [], "Knotenbudget %d erschoepft" % node_budget)
    return ("unloesbar", [], "Suchraum vollstaendig durchsucht, keine Loesung")


# ----------------------------------------------------------------------
def to_plan(m, solution):
    plan = {s: [] for s in m.service_ids}
    for u, val in solution:
        for s in val:
            plan[s].extend(u["members"])
    for s in plan:
        plan[s].sort(key=m.order.index)
    return plan


def score(m, plan):
    """Bewertung der Wuensche und der Verteilung (Abschnitt 3.6.5)."""
    counts = {p: 0 for p in m.order}
    for s, ids in plan.items():
        for p in ids:
            counts[p] += 1

    p01 = any("p30" in plan[s] and "p31" in plan[s] for s in plan)
    p02 = "p02" in plan["G5"] and "p17" in plan["G5"]
    konzett = sorted(s for s in plan if "p19" in plan[s])
    p03 = konzett == ["G5", "G8"]

    served = sum(1 for p in counts if counts[p] > 0)
    spread = max(counts.values()) - min(counts.values())
    total = sum(counts.values())
    return (
        (30 if p01 else 0) + (30 if p02 else 0) + (30 if p03 else 0)
        + 4 * served - 2 * spread + total,
        {"P-01-REDL-SCHARINGER": p01, "P-02-LARA-OLIVIA": p02, "P-03-KONZETT-WISH": p03},
    )


def preference_candidates(m):
    """Wuensche als harte Zusatzbedingung, in Prioritaetsreihenfolge.

    Jeder Eintrag liefert eine Liste gleichwertiger Varianten; die erste
    machbare Variante wird uebernommen.
    """
    def konzett():
        return [{"p19+p20": lambda v: v == frozenset({"G5", "G8"})}]

    def lara_olivia():
        return [{"p01+p02": lambda v: "G5" in v, "p17": lambda v: "G5" in v}]

    def redl_scharinger():
        shared = sorted(m.allowed["p30"] & m.allowed["p31"], key=m.service_ids.index)
        return [{"p30": (lambda s: (lambda v: s in v))(s),
                 "p31": (lambda s: (lambda v: s in v))(s)} for s in shared]

    return [
        ("P-03-KONZETT-WISH", konzett()),
        ("P-02-LARA-OLIVIA", lara_olivia()),
        ("P-01-REDL-SCHARINGER", redl_scharinger()),
    ]


def generate(verbose=True):
    m = Model()
    g5_eligible = [p for p in m.order if "G5" in m.allowed[p]]
    upper = len(g5_eligible)

    log = []
    target = None
    for t in range(upper, 0, -1):
        status, sols, info = solve(m, t, max_solutions=1)
        log.append({"step": "|G5| >= %d" % t, "status": status, "info": info})
        if verbose:
            print("  |G5| >= %2d -> %-24s %s" % (t, status, info or ""))
        if status == "loesung":
            target = t
            break
        if status == "keine_loesung_gefunden":
            raise SystemExit("Abbruch: keine Loesung gefunden fuer |G5| >= %d "
                             "(Knotenbudget erschoepft). Kein Unloesbarkeitsbeweis." % t)
    if target is None:
        raise SystemExit("Unloesbar: kein gueltiger Gesamtplan unter den bestaetigten Bedingungen.")

    # Wuensche nacheinander als harte Bedingung hinzunehmen, solange loesbar.
    if verbose:
        print("\nWuensche bei |G5| = %d nacheinander erzwingen:" % target)
    active, prefs = {}, {}
    for name, variants in preference_candidates(m):
        for variant in variants:
            trial = dict(active)
            trial.update(variant)
            status, sols, info = solve(m, target, max_solutions=1, restrict=trial)
            if status == "loesung":
                active, prefs[name] = trial, True
                break
        else:
            prefs[name] = False
        log.append({"step": "Wunsch %s" % name, "status": "erfuellbar" if prefs[name] else "nicht erfuellbar"})
        if verbose:
            print("  %-22s -> %s" % (name, "erfuellbar" if prefs[name] else "nicht erfuellbar"))

    status, sols, info = solve(m, target, max_solutions=200, restrict=active)
    best, best_score = None, None
    for sol in sols:
        plan = to_plan(m, sol)
        sc, _ = score(m, plan)
        if best_score is None or sc > best_score:
            best, best_score = plan, sc
    _, prefs_final = score(m, best)
    return m, best, target, prefs_final, log


def main():
    print("Suche maximale Besetzung der Familienmesse (Regel P-04-FAMILY-MAX):")
    m, plan, g5max, prefs, log = generate()
    counts = {p: 0 for p in m.order}
    for s, ids in plan.items():
        for p in ids:
            counts[p] += 1

    doc = {
        "_comment": "INTERN. Erzeugt von src/generate.py. Nicht veroeffentlichen.",
        "planVersion": m.rules_doc["planVersion"],
        "generatedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "generator": "src/generate.py (deterministische vollstaendige Tiefensuche, kein Zufall)",
        "timezone": m.services_doc["timezone"],
        "period": {"start": m.services_doc["periodStart"], "end": m.services_doc["periodEnd"]},
        "familyMassSize": g5max,
        "preferencesSatisfied": prefs,
        "searchLog": log,
        "assignments": {s: plan[s] for s in m.service_ids},
        "assignmentsByPerson": {p: sorted([s for s in m.service_ids if p in plan[s]]) for p in m.order},
        "counts": counts,
    }
    out = os.path.join(ROOT, "out", "plan.internal.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=2)
    print("\nFamilienmesse 18.10.: %d Personen" % g5max)
    for s in m.service_ids:
        sv = m.services[s]
        print("  %s %s %s: %2d Personen" % (s, sv["date"], sv["time"], len(plan[s])))
    print("Gesamteinsaetze: %d" % sum(counts.values()))
    print("geschrieben: %s" % out)


if __name__ == "__main__":
    main()
