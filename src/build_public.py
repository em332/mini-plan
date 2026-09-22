# -*- coding: utf-8 -*-
"""Erzeugt das Veroeffentlichungsverzeichnis public/.

Ausgegeben werden ausschliesslich freigegebene Angaben: oeffentliche
Anzeigenamen (Vorname + Nachnamensinitiale) und die tatsaechlichen Einsaetze.
Vollstaendige Nachnamen, Elternadressen, Abwesenheitsgruende, Quelldateien und
interne Regelkommentare werden nicht exportiert.

Der Export wird vor dem Schreiben mit dem unabhaengigen Validator geprueft.
"""
import html
import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import validate as V  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = os.path.join(ROOT, "public")

WEEKDAYS = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
MONTHS = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
          "August", "September", "Oktober", "November", "Dezember"]

CONTACT_NAME = "Anita Einsle"
CONTACT_MAIL = "anita@einsle.at"
NOTICE = "Ab Sonntag, 25. Oktober, beginnt die Abendmesse um 19:00 Uhr."
STATUS_LABEL = ("Entwurf – technisch validiert, organisatorisch noch nicht "
                "durch Anita Einsle freigegeben")


def long_date(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    return "%s, %d. %s %d" % (WEEKDAYS[date(y, m, d).weekday()], d, MONTHS[m - 1], y)


def short_date(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    return "%02d.%02d.%d" % (d, m, y)


# ----------------------------------------------------------------------
def build_public_data(plan, people, internal):
    names = {p["id"]: p["display"] for p in people}
    services = []
    for sid in V.SERVICE_ORDER:
        s = V.SERVICES[sid]
        servers = sorted((names[pid] for pid in plan[sid]),
                         key=lambda n: (n.split(" ")[-1], n))
        services.append({
            "id": sid,
            "date": s["date"],
            "weekday": WEEKDAYS[date(*(int(x) for x in s["date"].split("-"))).weekday()],
            "time": s["time"],
            "daypart": "Vormittagsmesse" if s["daypart"] == "vormittag" else "Abendmesse",
            "familyMass": s["family"],
            "servers": servers,
        })
    return {
        "title": "Ministrantenplan Oktober 2026",
        "validFrom": "2026-10-01",
        "validTo": "2026-10-31",
        "timezone": "Europe/Vienna",
        "planVersion": internal["planVersion"],
        "status": STATUS_LABEL,
        "updated": internal["generatedAt"][:10],
        "notice": NOTICE,
        "contact": {"name": CONTACT_NAME, "email": CONTACT_MAIL},
        "services": services,
    }


# ----------------------------------------------------------------------
def render_html(pub):
    e = html.escape
    by_day = {}
    for svc in pub["services"]:
        by_day.setdefault(svc["date"], []).append(svc)

    days = []
    for d in sorted(by_day):
        cards = []
        for svc in sorted(by_day[d], key=lambda s: s["time"]):
            label = svc["daypart"]
            badge = ('<span class="badge">Familienmesse</span>' if svc["familyMass"] else "")
            items = "\n".join(
                '            <li data-name="%s">%s<span class="match-flag"></span></li>'
                % (e(n, quote=True), e(n)) for n in svc["servers"])
            cards.append(
                '        <article class="mass" id="%s">\n'
                '          <div class="mass-head">\n'
                '            <h3>%s<span class="time"> · %s Uhr</span></h3>\n'
                '            %s\n'
                '          </div>\n'
                '          <p class="count">%d Ministrantinnen und Ministranten</p>\n'
                '          <ul class="servers">\n%s\n          </ul>\n'
                '        </article>'
                % (svc["id"], e(label), e(svc["time"]), badge, len(svc["servers"]), items))
        days.append(
            '      <section class="day" aria-labelledby="tag-%s">\n'
            '        <h2 id="tag-%s">%s</h2>\n'
            '        <div class="day-grid">\n%s\n        </div>\n'
            '      </section>'
            % (d, d, e(long_date(d)), "\n".join(cards)))

    return """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ministrantenplan Oktober 2026</title>
<meta name="description" content="Ministrantenplan der Pfarre für Oktober 2026.">
<meta name="robots" content="noindex">
<link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="wrap">

  <header class="page-header">
    <h1>Ministrantenplan Oktober 2026</h1>
    <p class="subtitle">Gültig vom 1. Oktober 2026 bis 31. Oktober 2026</p>
    <p class="meta">
      <span class="badge">Stand: {updated}</span>
      <span class="badge">Planversion {version}</span>
      <span class="badge badge--draft">{status}</span>
    </p>
  </header>

  <p class="notice">
    <span class="notice-icon" aria-hidden="true">●</span>
    <span>{notice}</span>
  </p>

  <p id="print-scope" class="print-scope">Gesamtplan (ungefiltert)</p>

  <noscript>
    <p class="noscript">Der Namensfilter benötigt JavaScript. Der vollständige
    Plan steht unabhängig davon vollständig auf dieser Seite.</p>
  </noscript>

  <form class="filter print-hide" id="filter" hidden>
    <h2 id="filter-heading">Einsätze einer Person suchen</h2>
    <div class="filter-row">
      <div class="field">
        <label for="name-search">Name suchen</label>
        <input type="search" id="name-search" name="name-search" list="name-list"
               autocomplete="off" placeholder="z. B. Lena B." aria-describedby="filter-status">
        <datalist id="name-list"></datalist>
      </div>
      <div class="field">
        <label for="name-select">Oder Name auswählen</label>
        <select id="name-select" name="name-select" aria-describedby="filter-status">
          <option value="">Alle Ministrantinnen und Ministranten</option>
        </select>
      </div>
      <div class="field" style="flex:0 0 auto;min-width:0">
        <button type="button" id="filter-reset" class="secondary">Filter zurücksetzen</button>
      </div>
      <div class="field" style="flex:0 0 auto;min-width:0">
        <button type="button" id="print-btn">Ansicht drucken</button>
      </div>
    </div>
    <p class="filter-status" id="filter-status" role="status" aria-live="polite"></p>
  </form>

  <main>
{days}
  </main>

  <section class="contact">
    <p>Bei Änderungswünschen oder Fragen wende dich an {contact_name}:
      <a href="mailto:{contact_mail}">{contact_mail}</a></p>
    <p class="count">Gültig vom 1. Oktober 2026 bis 31. Oktober 2026 · Stand: {updated} ·
      Planversion {version} · Zeiten: {notice}</p>
  </section>

</div>
<script src="search.js"></script>
<script src="app.js"></script>
</body>
</html>
""".format(days="\n".join(days), updated=e(pub["updated"]), version=e(pub["planVersion"]),
           status=e(pub["status"]), notice=e(pub["notice"]),
           contact_name=e(pub["contact"]["name"]), contact_mail=e(pub["contact"]["email"]))


# ----------------------------------------------------------------------
def main():
    with open(os.path.join(ROOT, "data", "people.json"), encoding="utf-8") as fh:
        people = json.load(fh)["people"]
    with open(os.path.join(ROOT, "out", "plan.internal.json"), encoding="utf-8") as fh:
        internal = json.load(fh)
    plan = internal["assignments"]

    errors, notes, metrics = V.validate(plan, people)
    if errors:
        print("Export abgebrochen: der Plan ist nicht gueltig.")
        for err in errors:
            print("  [%s] %s" % (err["code"], err["message"]))
        return 1

    pub = build_public_data(plan, people, internal)
    os.makedirs(PUBLIC, exist_ok=True)
    with open(os.path.join(PUBLIC, "plan.json"), "w", encoding="utf-8") as fh:
        json.dump(pub, fh, ensure_ascii=False, indent=2)
    with open(os.path.join(PUBLIC, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(render_html(pub))

    # Gegenprobe: oeffentlicher Auszug deckt sich mit dem validierten Plan.
    names = {p["id"]: p["display"] for p in people}
    for svc in pub["services"]:
        expected = sorted(names[pid] for pid in plan[svc["id"]])
        if sorted(svc["servers"]) != expected:
            print("Export weicht vom validierten Plan ab: %s" % svc["id"])
            return 1

    print("Veroeffentlichungsverzeichnis public/ erzeugt:")
    print("  public/index.html  (Gesamtplan, ohne JavaScript lesbar)")
    print("  public/plan.json   (oeffentlicher Datenauszug)")
    print("  public/styles.css, public/search.js, public/app.js")
    print("  Familienmesse: %d Personen, Gesamteinsaetze: %d"
          % (metrics["familyMassSize"], metrics["totalAssignments"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
