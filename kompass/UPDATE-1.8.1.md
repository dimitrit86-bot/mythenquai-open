# Nährstoff-Kompass 1.8.1 · Nährwerttext, Eier-Suche und weitere Lebensmittel

Die Version baut auf dem bereits veröffentlichten Stand 1.8.0 auf. Stückportionen, Textimport im eigenen Produkt und Reports werden nicht durch einen älteren Entwicklungsstand ersetzt. Die feste Adresse und das installierte App-Symbol bleiben unverändert.

## Eigenes Produkt: Nährwerttext auslesen

Unter Erfassen → Eigenes Produkt steht «Nährwerttext auslesen». Eine kopierte Nährwerttabelle einfügen, «Text auswerten» drücken, die Ausgangswerte und die Bezugsmenge kontrollieren und die Übernahme bestätigen. Beispielsweise lassen sich Angaben pro 30 g auf 100 g normalisieren. Die gegessene Menge wird davon getrennt im Tagebuch erfasst.

Die Übernahme füllt den bearbeitbaren Produkteditor; erst «Produkt speichern» speichert die Vorlage. Name und eingetragene Stückdefinition bleiben erhalten. Beim Abbrechen bleiben bisherige Eingaben bestehen. Eine bestätigte neue Nährwerttabelle ersetzt die Nährwertfelder; nicht erkannte Werte bleiben leer, statt aus einer älteren Tabelle übernommen zu werden. Deshalb die Vorschau vor dem Bestätigen kontrollieren. Foto und Nährwerttext werden weiterhin auf dem Gerät ausgewertet.

## Ei und Stückmengen

«Ei», «Eier», «Ei roh» oder «Eier gekocht» finden die vorhandenen BLV-Einträge vor zufälligen Teilworttreffern. Rohe und gekochte Eier bleiben getrennt. Die Suchkorrektur gilt auch für Rezeptzutaten. Eier waren bereits hinterlegt, wurden aber durch die alte Teilwortsuche schlecht gefunden.

Eine Stückportion kann ausdrücklich hinterlegt werden, zum Beispiel 1 Stück = 50 g essbarer Anteil. Die App nimmt dieses Gewicht nicht für jedes Ei an. Bruchteile und mehrere Stücke sind möglich; Anzahl und Gramm-/Millilitermenge werden angezeigt. Details: UPDATE-1.8.0.md.

## Acht neue Herstellerprodukte

Hinzugekommen sind Planted chicken Nature, chicken Jerusalem Style, burger Crispy, bratwurst Herbs, bratwurst Original, chicken Crispy Strips, filetstreifen Asia-Style und schnitzel Wiener Art. Jede Ergänzung enthält Hersteller-Produktadresse, Länderfassung, Bezugsmenge und Quellenstand 27.09.2026. Die tatsächliche Packung kann abweichen; dies ist kein Live-Abgleich von Rezepturen oder Verfügbarkeit. Fehlende Vitamin-/Mineralstoffwerte bleiben unbekannt.

Die 1’246 BLV-Lebensmittel und bisherigen 51 kuratierten Markenprodukte bleiben unverändert. Mit acht Ergänzungen sind 1’305 Datensätze direkt nutzbar; der separate Händlerkatalog mit 2’590 vorbefüllten Einträgen bleibt zusätzlich verfügbar. Neue Produkte sind auch als Rezeptzutaten auswählbar. Eigene Produkte und Gerichte werden weiterhin nach erfolgreichem Serverabgleich für die anderen Haushaltsprofile sichtbar.

## Reports und PDF

Im Profil unter «Deine Reports» täglich, wöchentlich oder monatlich auswählen und das Profil speichern. Diese Wahl bestimmt den Standardzeitraum beim Öffnen der Reports, nicht einen E-Mail- oder Push-Versand.

Die Report-Sektion zeigt Makros, Vitamine, Mineralstoffe und Spurenelemente mit Zielvergleich und Datenabdeckung. Der visuelle Überblick trennt erreichte Ziele, Werte unter dem Vergleich und noch offene Bewertungen. Unvollständige Tage und unbekannte Nährwerte werden nicht als Nullzufuhr gewertet. Eine Zielunterschreitung ist keine Mangeldiagnose.

«Als PDF exportieren» bietet eine kompakte Übersicht oder den vollständigen Report mit Nährstoffdetails und Quellen. Die Datei wird lokal auf dem Gerät erzeugt. Diese Report- und Exportfunktionen bleiben unverändert erhalten.

## Tatsächlich ausgeführte Prüfungen

Erfolgreicher GitHub-Prüflauf 36302064025; verifizierter Quellcommit 1b90a9fa6eca37488931062ad3b9929e92b10d96; Artefakt 10925901552.

275 Einzelprüfungen bestanden: 265 bestehende Tests für Berechnungen, Makroziele, Stückmengen, Text, Suche, Reports, Export und Synchronisierung sowie zehn neue Prüfungen der acht Herstellerprodukte. Zusätzlich bestanden je 37 tatsächliche Browserabläufe in Chromium und WebKit. Geprüft wurden neue Produkte und Mengen-Vorschau, Nährwerttext im eigenen Produkt, 30-g-Umrechnung, Stückportionen, Speichern, Rezeptzutaten, geteilte Vorlagen, getrennte Tagesbilanzen, Abbruch ohne verlorene Eingaben, Eier-Suche, Report-Häufigkeit, tatsächlicher PDF-Download, Neuladen und mobile/Desktop-Darstellung. Keine JavaScript-Laufzeitfehler oder unerwarteten externen Datenanfragen.

Die Tests verwendeten synthetische Haushaltsprofile, kontrollierte Serverantworten und echten Browserspeicher. Die erzeugte PDF-Datei wurde gerendert und visuell geprüft; die mobile Produktansicht ebenfalls. Der heruntergeladene Teststand wurde mit der veröffentlichten 1.8.0-Basis verglichen: App-Logik, Nährwerttext-/Stückfunktion, Referenzberechnungen und Reportcode sind unverändert; nur Zusatzkatalog, Versions-/Ladeverweise und Tests werden ergänzt. Ein Hardwarekamera- oder Installationstest auf einem physischen iPhone beziehungsweise Android-Gerät wird nicht behauptet.

## Update und bestehende Daten

Die Veröffentlichung ändert nur kompass/-Dateien, keine persönlichen Datenbankeinträge oder Passwörter. Authentifizierung und Synchronisierung bleiben erhalten. Den bisherigen Link https://dimitrit86-bot.github.io/mythenquai-open/kompass/ öffnen, bei Bedarf «App aktualisieren» drücken und Version 1.8.1 kontrollieren. Offene Eingaben vorher speichern. Keine Neuinstallation oder Löschung von Browserdaten nötig.
