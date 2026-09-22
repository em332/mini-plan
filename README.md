# Ministrantenplan Oktober 2026

Regelbasierte Planung und statische Webseite für den Ministrantenplan
vom 1. bis 31. Oktober 2026 (Pfarre Bregenz, Zeitzone `Europe/Vienna`).

Der Plan wird deterministisch erzeugt und anschließend **unabhängig von der
Zuteilungslogik** validiert. Nur der Inhalt von `public/` ist zur
Veröffentlichung bestimmt.

---

## Schnellstart

```bash
python3 src/generate.py      # Plan erzeugen          -> out/plan.internal.json
python3 src/validate.py      # Plan unabhängig prüfen -> Konsolenbericht
python3 src/build_public.py  # Veröffentlichung bauen -> public/
python3 src/report.py        # interner Prüfbericht   -> out/pruefbericht.md
```

Seite lokal ansehen:

```bash
python3 -m http.server 8000 --directory public   # http://localhost:8000
```

`public/index.html` lässt sich auch direkt im Browser öffnen; der Gesamtplan
steht statisch im HTML und benötigt kein JavaScript.

## Prüfungen

```bash
python3 -m unittest discover -s tests -t .   # Planungsregeln + öffentlicher Export (75 Tests)
node --test tests/test_ui.mjs                # Namensfilter im DOM (19 Tests)
```

Für die UI-Tests einmalig `npm install jsdom` (reine Testabhängigkeit, wird
nicht veröffentlicht). Ohne Python- oder Node-Fremdpakete läuft alles Übrige.

Die PDF-Auswertung wurde einmalig mit `pypdf` durchgeführt; für Erzeugung,
Validierung und Bau wird sie nicht benötigt.

## Verzeichnisse

| Pfad | Inhalt | Veröffentlichen? |
| --- | --- | --- |
| `public/` | **Veröffentlichungsverzeichnis**: `index.html`, `styles.css`, `search.js`, `app.js`, `plan.json` | **ja, nur dieses** |
| `input/` | Roh-PDFs der Elternrückmeldungen, fotografierte Ministrantenliste | nein |
| `data/` | Stammliste, Gottesdienste, Regelwerk mit Quellenverweisen | nein |
| `src/` | Modell, Generator, Validator, Export, Berichtsbau | nein |
| `out/` | erzeugter Plan mit internen Namen, Prüfbericht | nein |
| `tests/` | automatisierte Tests | nein |

**Veröffentlichung:** ausschließlich den Inhalt von `public/` auf den Webspace
kopieren, zum Beispiel

```bash
rsync -av --delete public/ <ziel>:/var/www/ministrantenplan/
```

`public/` enthält weder vollständige Nachnamen noch E-Mail-Adressen der Eltern,
Telefonnummern, Abwesenheitsgründe, Quelldateien oder interne Personen-IDs.
Einzige E-Mail-Adresse auf der Seite ist die zur Anzeige vorgesehene
Kontaktadresse `anita@einsle.at`. Der Test
`tests/test_public_export.py` prüft das bei jedem Lauf.

> **Hinweis:** „Vorname + Nachnamensinitiale" ist eine reduzierte
> Namensdarstellung, **keine Anonymisierung**. Es gibt keinen Zugangsschutz;
> `noindex` und der Namensfilter ersetzen keinen. Ein Betriebsmodell mit
> Zugangsschutz wäre gesondert zu klären.

## Aufbau

```
data/people.json     38 Personen: ID, Name, öffentlicher Anzeigename, Schreibvarianten
data/services.json   die acht Gottesdienste mit Datum, Uhrzeit, Mindestbesetzung
data/rules.json      jede Regel mit Kennung, Typ, Status, Quelle und Bezugsmonat
src/model.py         leitet Verfügbarkeiten aus dem Regelwerk ab (nur Generator)
src/generate.py      vollständige Tiefensuche, deterministisch, ohne Zufall
src/validate.py      eigenständige Prüfung mit EIGENER Regeltabelle
src/build_public.py  öffentlicher Datenauszug + statisch gerendertes HTML
src/report.py        interner Prüfbericht
```

### Erzeugung

`src/generate.py` sucht zuerst die größtmögliche Besetzung der Familienmesse
(Regel `P-04-FAMILY-MAX`), indem es die Zielgröße absteigend prüft. Für jede
Zielgröße läuft eine vollständige Tiefensuche mit Kapazitäts- und
Besetzungspruning, die Unlösbarkeit auch beweisen kann. Wird das Knotenbudget
erschöpft, lautet das Ergebnis ausdrücklich „keine Lösung gefunden" und **nicht**
„unlösbar". Anschließend werden die Wünsche einzeln als harte Bedingung
hinzugenommen, solange die Suche lösbar bleibt; so ist für jeden Wunsch belegt,
ob er unter allen Pflichtregeln erfüllbar ist.

Die Suche enthält keine Zufallskomponente und liefert bei gleichen Eingaben
denselben Plan (`tests/test_rules.py::ErzeugterPlan::test_reproduzierbar`).

### Validierung

`src/validate.py` importiert weder `generate.py` noch `model.py`. Es führt eine
eigene Regeltabelle und prüft jeden beliebigen, auch von Hand veränderten Plan:

```bash
python3 src/validate.py pfad/zum/anderen-plan.json
```

Rückgabewert 0 = keine Pflichtregelverletzung, 1 = Fehler gefunden.
Unerfüllte Wünsche erscheinen als Hinweis, nicht als Fehler.

## Andere Monate

`data/services.json` und `data/rules.json` sind die einzigen fachlichen
Eingaben; für einen neuen Monat werden Gottesdienste und Regeln dort ersetzt.
Mindestbesetzungen und Monatsobergrenze stehen als eigene Regeln im Regelwerk.
Für andere Monate sind keine Regeln hinterlegt — die Oktober-Regeln tragen
ihren Bezugsmonat (`referenceMonth`) und gelten nicht automatisch weiter.

## Stand

Der Plan ist **technisch validiert**, aber **organisatorisch nicht freigegeben**.
Die Seite weist ihn sichtbar als Entwurf aus. Details, offene Punkte und die
Begründung der Familienmessen-Größe stehen in `out/pruefbericht.md`.
