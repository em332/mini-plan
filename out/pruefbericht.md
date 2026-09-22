# Interner Pruefbericht - Ministrantenplan Oktober 2026

INTERN. Nicht veroeffentlichen. Enthaelt vollstaendige Namen und Quellenbezuege.

- Planversion: 1.0
- Erzeugt: 2026-09-22T22:01:22+02:00
- Bericht erstellt: 2026-09-22T22:01:23+02:00
- Zeitzone: Europe/Vienna
- Status: technisch validiert, organisatorisch NICHT freigegeben (keine Freigabe durch Anita Einsle eingeholt)

## 1. Ergebnis der unabhaengigen Validierung

Validator: `src/validate.py` mit eigener Regeltabelle, ohne Import der Zuteilungslogik.

- Pflichtregelverletzungen: **0**
- Hinweise: 3
  - [V13] p10 hat einen zusaetzlichen Einsatz ohne Magnus (G5) - zulaessig
  - [V13] p11 hat einen zusaetzlichen Einsatz ohne Magnus (G5) - zulaessig
  - [V13] p16 hat einen zusaetzlichen Einsatz ohne Magnus (G5) - zulaessig

## 2. Besetzung je Gottesdienst

| ID | Datum | Uhrzeit | Art | Mindest | Ist | Status |
| --- | --- | --- | --- | ---: | ---: | --- |
| G1 | 2026-10-04 | 11:00 | Vormittagsmesse | 8 | 8 | erfuellt |
| G2 | 2026-10-04 | 19:30 | Abendmesse | 6 | 6 | erfuellt |
| G3 | 2026-10-11 | 11:00 | Vormittagsmesse | 8 | 8 | erfuellt |
| G4 | 2026-10-11 | 19:30 | Abendmesse | 6 | 6 | erfuellt |
| G5 | 2026-10-18 | 11:00 | Familienmesse | 8 | 21 | erfuellt |
| G6 | 2026-10-18 | 19:30 | Abendmesse | 6 | 6 | erfuellt |
| G7 | 2026-10-25 | 11:00 | Vormittagsmesse | 8 | 8 | erfuellt |
| G8 | 2026-10-25 | 19:00 | Abendmesse | 6 | 6 | erfuellt |

Gesamteinsaetze: **69** (Mindestanforderung 56).

## 3. Einsatzanzahl je Person

| Person | Einsaetze | Gottesdienste | Obergrenze |
| --- | ---: | --- | --- |
| Annalena Bereuter | 1 | G5 | hoechstens 2 |
| Lara Bereuter | 1 | G5 | hoechstens 2 |
| Zita Bergmayer | 2 | G5, G7 | hoechstens 2 |
| Greta Berlinger | 2 | G2, G5 | hoechstens 2 |
| Felix Brunner | 1 | G4 | genau 1 (Einzelregel) |
| Magnus Brunner | 1 | G4 | genau 1 (Einzelregel) |
| Lena Buchauer | 2 | G6, G7 | hoechstens 2 |
| Lukas Buchauer | 2 | G1, G7 | hoechstens 2 |
| Christina Cukrowicz | 1 | G1 | hoechstens 2 |
| Paulus Cukrowicz | 2 | G4, G5 | hoechstens 2 |
| Vincent Dressel | 2 | G4, G5 | hoechstens 2 |
| Josef Eder | 2 | G1, G7 | hoechstens 2 |
| Klara Einsle | 2 | G2, G8 | hoechstens 2 |
| Martha Einsle | 2 | G2, G8 | hoechstens 2 |
| Elisa Erath | 2 | G3, G7 | hoechstens 2 |
| Simon Johannes Ernst | 2 | G4, G5 | hoechstens 2 |
| Olivia Eze | 2 | G5, G7 | hoechstens 2 |
| Lukas Keiler | 2 | G3, G7 | hoechstens 2 |
| Emma Konzett | 2 | G5, G8 | hoechstens 2 |
| Clara Konzett | 2 | G5, G8 | hoechstens 2 |
| Loana Kramer | 2 | G6, G8 | hoechstens 2 |
| Nora Kramer | 2 | G6, G8 | hoechstens 2 |
| Anna-Catharina Meusburger | 2 | G3, G7 | hoechstens 2 |
| Magdalena Müller-Rupp | 1 | G5 | hoechstens 2 |
| Emma Ocvirk | 2 | G3, G5 | hoechstens 2 |
| Katharina Ocvirk | 2 | G3, G5 | hoechstens 2 |
| Ella Ottersbach | 2 | G1, G5 | hoechstens 2 |
| Marie Ottersbach | 2 | G1, G5 | hoechstens 2 |
| Anna Pfefferkorn | 2 | G2, G6 | hoechstens 2 |
| Jakob Redl | 2 | G1, G5 | hoechstens 2 |
| Remus Scharinger | 2 | G1, G5 | hoechstens 2 |
| Emilia Schmidgall | 2 | G3, G5 | hoechstens 2 |
| Marlena Schmidgall | 2 | G3, G5 | hoechstens 2 |
| Ida Seitner | 1 | G5 | hoechstens 2 |
| Ferdinand Sillaber | 2 | G4, G5 | hoechstens 2 |
| Vanessa Volkmann | 2 | G1, G3 | hoechstens 2 |
| Henriette Wöß | 2 | G2, G6 | hoechstens 2 |
| Matilda Wöß | 2 | G2, G6 | hoechstens 2 |

- 2 Einsaetze: 31 Personen
- 1 Einsaetze: 7 Personen
- Jede der 38 Personen hat mindestens einen Einsatz.

## 4. Regelstatus

| Regel | Typ | Status | Betroffene | Quelle |
| --- | --- | --- | --- | --- |
| R-GLOBAL-MIN-VM | service_min | bestaetigt | alle | Auftrag Abschnitt 3.1 |
| R-GLOBAL-MIN-AM | service_min | bestaetigt | alle | Auftrag Abschnitt 3.1 |
| R-GLOBAL-NO-MAX | service_max | bestaetigt | alle | Auftrag Abschnitt 3.1 |
| R-GLOBAL-MAX-MONTH | person_max_month | bestaetigt | alle | Auftrag Abschnitt 3.1 |
| R-GLOBAL-STD-AVAIL | default_availability | bestaetigt | alle | Auftrag Abschnitt 3.1 |
| R-GLOBAL-ONE-PER-SUNDAY | person_max_per_day | planungsvorsicht | alle | Auftrag Abschnitt 3.1.1 / 5 |
| R-SVC-FAMILY | service_flag | bestaetigt | alle | Auftrag Abschnitt 2 / 3.1 |
| R-SVC-LATE-OCT-TIME | service_time | bestaetigt | alle | Auftrag Abschnitt 2 |
| R-01-KRAMER | block_services | bestaetigt | Loana Kramer, Nora Kramer | WG- Miniplan Oktober Loana und Nora Kramer.pdf |
| R-02-ZITA-ABSENT | block_services | bestaetigt | Zita Bergmayer | WG- Miniplanung Oktober.pdf |
| R-02-ZITA-VM | daypart_only | bestaetigt | Zita Bergmayer | Auftrag Abschnitt 3.1 / 3.2 |
| R-03-OTTERSBACH | block_services | bestaetigt | Ella Ottersbach, Marie Ottersbach | WG- Abwesenheiten Mini Oktober.pdf |
| R-04-CHRISTINA | allow_only_services | bestaetigt | Christina Cukrowicz | WG- mini oktober christina.pdf |
| R-05-BEREUTER | allow_only_services | bestaetigt | Annalena Bereuter, Lara Bereuter | WG- ministrieren oktober.pdf |
| R-06-WOESS | block_services | bestaetigt | Henriette Wöß, Matilda Wöß | WG- Ministrieren Oktober 2026.pdf |
| R-07-FERDINAND | allow_only_services | bestaetigt | Ferdinand Sillaber | WG- Oktober.pdf |
| R-08-SCHMIDGALL-BLOCK | block_services | bestaetigt | Emilia Schmidgall, Marlena Schmidgall | WG- Mini-Dienst Oktober 2026.pdf |
| R-08-SCHMIDGALL-LEKTOR | must_serve | bestaetigt | Emilia Schmidgall, Marlena Schmidgall | WG- Mini-Dienst Oktober 2026.pdf |
| R-09-GRETA | block_services | bestaetigt | Greta Berlinger | WG- Abwesenheit Oktober.pdf |
| R-10-BRUNNER-ABSENT | block_services | bestaetigt | Felix Brunner, Magnus Brunner | WG- Ministrieren im Oktober .pdf |
| R-10-BRUNNER-EXACT | exact_count_at | bestaetigt | Felix Brunner, Magnus Brunner | Auftrag Abschnitt 3.5 |
| R-11-MAGDALENA | allow_only_services | bestaetigt | Magdalena Müller-Rupp | WG- Ministrieren .pdf |
| R-12-OCVIRK | allow_only_services | bestaetigt | Emma Ocvirk, Katharina Ocvirk | WG- Minieinteilung Oktober.pdf |
| R-13-SEPTEMBER-HIST | historic_preference | historisch_inaktiv | Felix Brunner, Magnus Brunner | WG- Ministrieren September .pdf |
| R-14-REMUS | block_services | bestaetigt | Remus Scharinger | WG- Minis Einteilung Oktober.pdf |
| R-15-KONZETT-MONTH | source_correction | bestaetigt | Emma Konzett, Clara Konzett | x-WG- Oktober.pdf |
| R-16-ANNA-P | block_services | bestaetigt | Anna Pfefferkorn | WG- Anna ministrieren.pdf |
| R-17-OLIVIA | block_services | bestaetigt | Olivia Eze | Auftrag Abschnitt 3.2 |
| R-18-VM-ONLY | daypart_only | bestaetigt | Annalena Bereuter, Lara Bereuter, Zita Bergmayer, Christina Cukrowicz, Olivia Eze, Magdalena Müller-Rupp, Ella Ottersbach, Marie Ottersbach | Auftrag Abschnitt 3.2 |
| R-18-AM-ONLY | daypart_only | bestaetigt | Klara Einsle, Martha Einsle | Auftrag Abschnitt 3.2 |
| R-19-MAGNUS-GROUP | group_with_directed | bestaetigt | Magnus Brunner | Auftrag Abschnitt 3.5 |
| R-20-FELIX-GROUP | group_with_directed | bestaetigt | Felix Brunner | Auftrag Abschnitt 3.5 |
| R-21-PAIRS | pair_bound | bestaetigt | alle | Auftrag Abschnitt 3.3 |
| R-22-IDA-DERIVED | derived_daypart | abgeleitet | Ida Seitner | Auftrag Abschnitt 3.3 |
| P-01-REDL-SCHARINGER | preference_together | wunsch | alle | Auftrag Abschnitt 3.6 |
| P-02-LARA-OLIVIA | preference_together_at | wunsch | alle | Auftrag Abschnitt 3.6 |
| P-03-KONZETT-WISH | preference_assign | wunsch | Emma Konzett, Clara Konzett | x-WG- Oktober.pdf |
| P-04-FAMILY-MAX | preference_maximise | wunsch | alle | Auftrag Abschnitt 3.6 |
| P-05-FAIRNESS | preference_fairness | wunsch | alle | Auftrag Abschnitt 3.6 |

## 5. Wuensche und Praeferenzen

| Wunsch | Ergebnis | Bemerkung |
| --- | --- | --- |
| P-01-REDL-SCHARINGER | erfuellt | Jakob Redl und Remus Scharinger dienen gemeinsam |
| P-02-LARA-OLIVIA | erfuellt | Lara Bereuter und Olivia Eze gemeinsam in der Familienmesse (Annalena wegen Paarbindung ebenfalls) |
| P-03-KONZETT-WISH | erfuellt | Clara und Emma Konzett am 18.10. 11:00 und am 25.10. 19:00 |

Gemeinsamer Termin Redl/Scharinger: G1, G5

## 6. Familienmesse am 18.10.2026 um 11:00 Uhr

Besetzung: **21 Personen** (keine Hoechstzahl; Mindestbesetzung 8).

Fuer die Familienmesse grundsaetzlich geeignet und verfuegbar: 33 Personen.
Nicht geeignet, weil ausschliesslich abends einteilbar: Felix Brunner, Klara Einsle, Magnus Brunner, Martha Einsle.

Nicht eingeteilt, obwohl geeignet (12 Personen):

| Person | stattdessen eingeteilt |
| --- | --- |
| Anna Pfefferkorn | G2, G6 |
| Anna-Catharina Meusburger | G3, G7 |
| Elisa Erath | G3, G7 |
| Henriette Wöß | G2, G6 |
| Josef Eder | G1, G7 |
| Lena Buchauer | G6, G7 |
| Loana Kramer | G6, G8 |
| Lukas Buchauer | G1, G7 |
| Lukas Keiler | G3, G7 |
| Matilda Wöß | G2, G6 |
| Nora Kramer | G6, G8 |
| Vanessa Volkmann | G1, G3 |

Begruendung: Die Gesamtkapazitaet betraegt 69 Einsaetze (31 Personen mit hoechstens zwei Einsaetzen, 7 Personen mit nur einem zulaessigen Termin). Die uebrigen sieben Gottesdienste benoetigen zusammen mindestens 48 Einsaetze. Damit sind hoechstens 69 - 48 = 21 Personen in der Familienmesse moeglich. Die vollstaendige Suche hat fuer |G5| >= 22 nachgewiesen, dass keine Loesung existiert; fuer |G5| = 21 wurde eine Loesung gefunden. Zusaetzlich muessen mindestens vier fuer die Familienmesse geeignete Kinder ausserhalb bleiben, weil die Abendmesse am 18.10. sonst nur mit Klara und Martha Einsle besetzbar waere und ihre Mindestbesetzung von sechs Personen nicht erreichen wuerde.

## 7. Suchprotokoll des Generators

| Schritt | Ergebnis | Bemerkung |
| --- | --- | --- |
| |G5| >= 33 | unloesbar | Suchraum vollstaendig durchsucht, keine Loesung |
| |G5| >= 32 | unloesbar | Suchraum vollstaendig durchsucht, keine Loesung |
| |G5| >= 31 | unloesbar | Suchraum vollstaendig durchsucht, keine Loesung |
| |G5| >= 30 | unloesbar | Suchraum vollstaendig durchsucht, keine Loesung |
| |G5| >= 29 | unloesbar | Suchraum vollstaendig durchsucht, keine Loesung |
| |G5| >= 28 | unloesbar | Suchraum vollstaendig durchsucht, keine Loesung |
| |G5| >= 27 | unloesbar | Suchraum vollstaendig durchsucht, keine Loesung |
| |G5| >= 26 | unloesbar | Suchraum vollstaendig durchsucht, keine Loesung |
| |G5| >= 25 | unloesbar | Suchraum vollstaendig durchsucht, keine Loesung |
| |G5| >= 24 | unloesbar | Suchraum vollstaendig durchsucht, keine Loesung |
| |G5| >= 23 | unloesbar | Suchraum vollstaendig durchsucht, keine Loesung |
| |G5| >= 22 | unloesbar | Suchraum vollstaendig durchsucht, keine Loesung |
| |G5| >= 21 | loesung |  |
| Wunsch P-03-KONZETT-WISH | erfuellbar |  |
| Wunsch P-02-LARA-OLIVIA | erfuellbar |  |
| Wunsch P-01-REDL-SCHARINGER | erfuellbar |  |

## 8. Quellen

Im Ordner `input/plan-sept-2026` liegen **16 PDF-Dateien**; alle wurden gelesen und im Regelwerk erfasst.

| PDF | im Regelwerk erfasst |
| --- | --- |
| WG- Abwesenheit Oktober.pdf | ja |
| WG- Abwesenheiten Mini Oktober.pdf | ja |
| WG- Anna ministrieren.pdf | ja |
| WG- Mini-Dienst Oktober 2026.pdf | ja |
| WG- Minieinteilung Oktober.pdf | ja |
| WG- Miniplan Oktober Loana und Nora Kramer.pdf | ja |
| WG- Miniplanung Oktober.pdf | ja |
| WG- Minis Einteilung Oktober.pdf | ja |
| WG- Ministrieren .pdf | ja |
| WG- Ministrieren Oktober 2026.pdf | ja |
| WG- Ministrieren September .pdf | ja |
| WG- Ministrieren im Oktober .pdf | ja |
| WG- Oktober.pdf | ja |
| WG- mini oktober christina.pdf | ja |
| WG- ministrieren oktober.pdf | ja |
| x-WG- Oktober.pdf | ja |

Aussermonatliche und widerspruechliche Aussagen:

- `WG- Ministrieren September .pdf`: September-Wunsch, Regel R-13-SEPTEMBER-HIST als `historisch_inaktiv` gefuehrt und in der Verfuegbarkeitsableitung uebersprungen.
- `x-WG- Oktober.pdf`: Text nennt "November", Betreff "Oktober"; R-15-KONZETT-MONTH dokumentiert Oktober 2026 als bestaetigten Bezugsmonat.
- `WG- mini oktober christina.pdf`: bezweifelter Kalendereintrag 03.10. 11:00; der 03.10.2026 ist ein Samstag und keiner der acht Gottesdienste.
- `WG- Mini-Dienst Oktober 2026.pdf`: Lektorentermine 08.11., 31.12., 03.01.27 liegen ausserhalb des Planungszeitraums.
- Ausflugs- und Spaghetti-Anmeldungen, E-Mail-Verteiler und Telefonnummern sind keine Planungsdaten.

## 9. Tatsaechlich ausgefuehrte Pruefungen

| Pruefung | Aufruf | Ergebnis |
| --- | --- | --- |
| Fachliche Regeln und oeffentlicher Export (Python) | `python3 -m unittest discover -s tests -t .` | 85 Tests bestanden |
| Bedienung des Namensfilters (Node/jsdom) | `node --test tests/test_ui.mjs` | 19 Tests bestanden |
| Unabhaengige Planvalidierung | `python3 src/validate.py` | 0 Fehler, 3 Hinweise |
| Visuelle Browserpruefung (Smartphone-/Desktopbreite, Druckvorschau) | manuell im Browser | **NICHT AUSGEFUEHRT** |

Die Layout- und Druckvorgaben sind statisch geprueft (HTML-Struktur, Breakpoint, Umbruchregeln, Druckstilblock) und die Filterbedienung ist im DOM getestet. Eine visuelle Pruefung in einem echten Browser bei Smartphone- und Desktopbreite konnte in dieser Umgebung nicht durchgefuehrt werden und steht aus.

## 10. Offene Punkte

- **Q-01 (erledigt)**: Die fotografierte Ministrantenliste (IMG_7123) wurde nachgereicht und mit der Stammliste abgeglichen: 38 Namen, identische Reihenfolge und Schreibweisen, keine zusaetzliche Person. _Auswirkung: keine_
- **Q-02 (offen_nicht_planungsrelevant)**: Das Foto IMG_6746.jpeg (Uebersicht der 16 PDF-Dateien) liegt nicht vor. Die Vollstaendigkeit der 16 Rueckmeldungen wurde stattdessen gegen das Verzeichnis input/plan-sept-2026 geprueft: genau 16 PDFs, alle in Abschnitt 4 gelistet und einzeln ausgewertet. _Auswirkung: keine Auswirkung auf den Plan_
- Die oeffentliche Darstellung "Vorname + Nachnamensinitiale" ist eine reduzierte Namensdarstellung, keine Anonymisierung. Ein Zugangsschutz ist nicht eingerichtet; `noindex` und der Namensfilter ersetzen ihn nicht.
- Die Kontaktangabe "Anita Einsle / anita@einsle.at" ist laut Auftrag zur Anzeige vorgesehen und nennt damit den Nachnamen, den auch Klara E. und Martha E. tragen.
- Die visuelle Browserpruefung bei Smartphone- und Desktopbreite sowie die Druckvorschau stehen aus; sie sind vor der Veroeffentlichung nachzuholen (besonders die Familienmesse mit 21 Namen).
- Der Plan ist technisch validiert, aber organisatorisch nicht freigegeben.

