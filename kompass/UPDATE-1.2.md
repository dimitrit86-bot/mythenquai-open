# Nährstoff-Kompass · Geräte- und Katalogupdate 1.2

Stand: 26.09.2026. Dieses Update ergänzt die bestehende Tagebuch-Engine, ohne deren Berechnungen, die Anmeldung oder gespeicherte Profile zu ersetzen. Die Versionsangabe der unveränderten Engine kann an einzelnen alten Stellen weiter 1.0.0 lauten; die neue Geräteleiste zeigt Update 1.2.0.

## Buttons und Startprofil

Oben stehen App installieren, App aktualisieren und nach Anmeldung Startprofil auf diesem Gerät. Die Installation verwendet den Browserdialog, wenn verfügbar, sonst gerätespezifische Schritte. Auf dem iPhone bleibt die Bestätigung über Safari / Teilen / Zum Home-Bildschirm erforderlich. Keine automatische oder heimliche Installation.

Im Profilmenü kann ein festes Profil (zum Beispiel Immer Dimitri oder Immer Patricia), Zuletzt genutztes Profil oder Jedes Mal fragen eingestellt werden. Die Einstellung gilt für den jeweiligen Browser beziehungsweise die installierte Web-App, nicht für andere Geräte. Nach Wahl Startprofil speichern drücken. Ein manueller Wechsel ändert ein festes Startprofil nicht. Die bestehende Anmeldung bleibt erforderlich. Der bestehende Wiederherstellungsweg für nicht synchronisierte Einträge hat Vorrang; offline kann nur der vorhandene verschlüsselte Profilcache wiederhergestellt werden.

App aktualisieren prüft auf veröffentlichte App-Versionen. Der Button ändert keine Passwörter, löscht keine Browserdaten und aktualisiert nicht eigenständig die Lebensmittelangaben bei Händlern. Bei erkannten offenen Eingaben oder ungesendeten Änderungen wird die Aktivierung pausiert. Die bestehende Sicherungsfunktion bleibt verfügbar.

## Erweiterter Lebensmittelkatalog

Zusätzlich zu 1’297 vorhandenen Basis-/Markeneinträgen wurden 2’590 Produktdatensätze als separater vorbefüllter Händlerkatalog integriert. Insgesamt stehen damit 3’887 Katalogeinträge bereit, aber neue Händlerprodukte müssen vor der ersten Verwendung anhand ihrer Packung bestätigt werden.

Der offizielle öffentliche CSV-Export von Open Food Facts enthielt zum Importzeitpunkt 4’532’767 Zeilen. Die Auswahl umfasst Alpro-Markenvarianten weltweit sowie mit Schweiz und Migros, Coop, Lidl oder Aldi verknüpfte, explizit vegetarisch oder vegan gekennzeichnete Produkte mit verwertbaren Grundnährwerten.

| Auswahl | Neue Datensätze |
|---|---:|
| Alpro, inklusive internationaler Varianten | 730 |
| Migros, Schweiz im Quelldatensatz | 863 |
| Coop, Schweiz im Quelldatensatz | 724 |
| Lidl, Schweiz im Quelldatensatz | 204 |
| Aldi, Schweiz im Quelldatensatz | 118 |

Die Gruppen überschneiden sich. Unterschiedliche Barcodes, Packungsgrössen und Ländervarianten sind nicht automatisch unterschiedliche Rezepturen. Dies ist keine vollständige aktuelle Hersteller- oder Händler-Sortimentsliste und keine Bestandsauskunft. Fehlende Händler- oder Veggie-Kennzeichnungen können Produkte von der Auswahl ausschliessen. Importstand: 26.09.2026, 15:09 UTC; Quellexport: 26.09.2026, 12:31 UTC.

## Verwendung

Erfassen öffnen und den Bereich Alpro & Händlerkatalog aufklappen. Dort stehen Produkt-/Barcode-Suche, Marke/Händler, Veggie-Kennzeichnung und Länderfassung sowie Weitere Produkte anzeigen zur Verfügung. Für die Schweizer Auswahl die Länderfassung Schweiz im Datensatz setzen. Unbekannter Veggie-Status wird nicht als vegan ausgegeben.

Beim ersten Öffnen eines neuen Händlerprodukts erscheint der bereits ausgefüllte Packungswerte-Editor. Die Bezugsmenge 100 g oder 100 ml muss aktiv ausgewählt werden; Werte und Produktvariante sind zu kontrollieren und zu bestätigen. Abweichende Packungswerte lassen sich direkt korrigieren. Nach Produkt speichern ist das Produkt im aktuellen Profil verfügbar, auch als Rezeptzutat. Nicht bestätigte Produkte sind in der Rezeptauswahl deaktiviert; sie werden zuerst unter Erfassen bestätigt. Bereits bestehende Rezepte und Tagebucheinträge behalten ihre gespeicherten Kopien.

Nährwerte werden nicht allein aus Produktnamen oder Zutatenlisten erfunden. Unbekannte Vitamine bleiben unbekannt, echte Nullwerte bleiben null. Die allgemeinen BLV-Kopfzeilen beziehen sich nur auf die ursprüngliche Schweizer Datenbank; Händlerdaten sind separat gekennzeichnet. Quellen-URL und Importbericht stehen beim Katalog zur Verfügung. Quelle: Open Food Facts contributors, ODbL 1.0. Das abgeleitete öffentliche Teil-Dataset steht als retail-data.js bereit; persönliche Einträge werden nicht veröffentlicht.

## Geprüfter Umfang

GitHub-Prüflauf 36252127252 war erfolgreich: 48 bestehende Rechen-/Rezepttests, JavaScript-Syntaxprüfung und 13 zusätzliche Prüfungen für Datensatzanzahl, Alpro, Händlerabdeckung, eindeutige IDs, unbekannte Werte, vorhandene Script-Dateien und Startprofilregeln. Byte-Hashes bestätigen: app.js, core.js und household.js wurden nicht verändert.

Zusätzlich bestanden 13 lokale Chromium-DOM-Prüfungen mit synthetischem Speicher und dem heruntergeladenen, geprüften Quellpaket: fehlerfreier Start, Installationshilfe, Startprofil speichern, Katalog laden/filtern, notwendige Bezugswahl, Produkt speichern, Tagebuch erfassen, Rezept speichern, Schutzindikatoren für offene Rezept-/Profileingaben und mobile Breite ohne horizontales Überlaufen. Dabei wurden keine echten Haushaltsdaten gelesen oder geschrieben. Dies ist kein Test der tatsächlichen Installation auf einem Android-/iPhone-Gerät und kein neuer Ende-zu-Ende-Test des privaten Servers.

Die ursprüngliche Schweizer Datenbasis, die 51 kuratierten Ergänzungen sowie die private Authentifizierungs- und Tagebuchlogik bleiben unverändert. Alle veröffentlichten Änderungen dieses Updates liegen unter kompass/; die Tennisseiten bleiben unverändert.
