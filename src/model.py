"""Datenmodell und Ableitung der Verfuegbarkeiten aus data/*.json.

Dieses Modul wird ausschliesslich vom Generator benutzt. Der Validator
(src/validate.py) implementiert seine Pruefungen eigenstaendig und uebernimmt
keine hier abgeleiteten Zwischenergebnisse.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


class Model:
    def __init__(self):
        self.people_doc = load("people.json")
        self.services_doc = load("services.json")
        self.rules_doc = load("rules.json")

        self.people = {p["id"]: p for p in self.people_doc["people"]}
        self.order = [p["id"] for p in self.people_doc["people"]]
        self.services = {s["id"]: s for s in self.services_doc["services"]}
        self.service_ids = [s["id"] for s in self.services_doc["services"]]
        self.rules = {r["id"]: r for r in self.rules_doc["rules"]}

        self.sunday_of = {sid: self.services[sid]["date"] for sid in self.service_ids}
        self.sundays = sorted(set(self.sunday_of.values()))

        self.min_servers = {sid: self.services[sid]["minServers"] for sid in self.service_ids}
        self.max_month = self.rules["R-GLOBAL-MAX-MONTH"]["payload"]["max"]
        self.max_per_sunday = self.rules["R-GLOBAL-ONE-PER-SUNDAY"]["payload"]["max"]

        self.allowed = self._derive_allowed()
        self.forced = self._derive_forced()
        self.exact = self._derive_exact()
        self.pairs = [tuple(p) for p in self.rules["R-21-PAIRS"]["payload"]["pairs"]]
        self.directed_groups = [
            (r["subjects"][0], r["payload"]["companions"])
            for r in self.rules_doc["rules"]
            if r["type"] == "group_with_directed"
        ]

    # ------------------------------------------------------------------
    def _derive_allowed(self):
        """Erlaubte Gottesdienste je Person.

        Ausgangspunkt ist die bestaetigte Standardregel R-GLOBAL-STD-AVAIL
        (alle Messen), danach wirken Whitelists, Tageszeitregeln und Sperren.
        Eine Sperre kann durch die Standardverfuegbarkeit nie aufgehoben werden.
        """
        allowed = {pid: set(self.service_ids) for pid in self.people}

        for rule in self.rules_doc["rules"]:
            if rule.get("status") == "historisch_inaktiv":
                continue
            rtype = rule["type"]
            subs = rule.get("subjects", [])
            pay = rule.get("payload", {})
            if rtype == "allow_only_services":
                for pid in subs:
                    allowed[pid] &= set(pay["services"])
            elif rtype in ("daypart_only", "derived_daypart"):
                keep = {s for s in self.service_ids
                        if self.services[s]["daypart"] == pay["daypart"]}
                for pid in subs:
                    allowed[pid] &= keep
            elif rtype == "block_services":
                for pid in subs:
                    allowed[pid] -= set(pay["services"])
            elif rtype == "exact_count_at":
                for pid in subs:
                    allowed[pid] &= {pay["service"]}

        # Paarbindung: gemeinsame Verfuegbarkeit ist die Schnittmenge.
        for a, b in [tuple(p) for p in self.rules["R-21-PAIRS"]["payload"]["pairs"]]:
            common = allowed[a] & allowed[b]
            allowed[a] = set(common)
            allowed[b] = set(common)
        return allowed

    def _derive_forced(self):
        forced = {pid: set() for pid in self.people}
        for rule in self.rules_doc["rules"]:
            if rule["type"] == "must_serve":
                for pid in rule["subjects"]:
                    forced[pid].add(rule["payload"]["service"])
            if rule["type"] == "exact_count_at":
                for pid in rule["subjects"]:
                    forced[pid].add(rule["payload"]["service"])
        # Begleiter muessen bei Magnus dabei sein: Magnus' Termin steht fest.
        for leader, companions in [
            (r["subjects"][0], r["payload"]["companions"])
            for r in self.rules_doc["rules"] if r["type"] == "group_with_directed"
        ]:
            leader_fixed = forced[leader]
            if len(leader_fixed) == 1:
                for c in companions:
                    forced[c] |= set(leader_fixed)
        return forced

    def _derive_exact(self):
        exact = {}
        for rule in self.rules_doc["rules"]:
            if rule["type"] == "exact_count_at":
                for pid in rule["subjects"]:
                    exact[pid] = rule["payload"]["count"]
        return exact

    # ------------------------------------------------------------------
    def cap(self, pid):
        return self.exact.get(pid, self.max_month)

    def display(self, pid):
        return self.people[pid]["display"]

    def full_name(self, pid):
        p = self.people[pid]
        return "%s %s" % (p["firstName"], p["lastName"])
