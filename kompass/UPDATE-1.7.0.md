# Nährstoff-Kompass 1.7.0 · Visuelle Reports und PDF-Export

Die feste Adresse bleibt https://dimitrit86-bot.github.io/mythenquai-open/kompass/ . Neue Oberfläche: Version 1.7.0. Bestehende Profile, Report-Häufigkeiten, Ziele, eigene Produkte, Gerichte und Tagebucheinträge bleiben erhalten. Die Veröffentlichung enthält keine Rücksetzung persönlicher Daten und keine Serveränderung.

## Reports auf einen Blick

Der Bereich «Reports» hat eine neue, auf Handys ausgelegte Darstellung: dunkelgrüne Übersichtsfläche, grosse Kennzahlen, farbige Vergleichsbalken und kurze Zusammenfassungen. Der Ring zeigt erfasste Tage im Zeitraum, keinen Gesundheitsscore.

Vier Kennzahlen unterscheiden «Erreicht / im Plan», «Unter dem Vergleich», «Über Makro-Plan» und «Offen / ohne Bewertung». Fehlende Nährstoffangaben, offene Protokolle, fehlende Ziele oder unpassende Äquivalente werden nicht als gescheiterte Ziele ausgegeben. «Offen» ist ausdrücklich keine Mangeldiagnose.

Energie und Makros erscheinen als eigene Karten. Vitamine, Mineralstoffe/Mengenelemente und Spurenelemente sind in übersichtlichen aufklappbaren Gruppen zusammengefasst. Antippen eines Nährstoffs zeigt Menge, Referenz, Tagesverteilung, Quellen und gegebenenfalls fehlende Produktangaben. «Alle Details aufklappen» öffnet die Gruppen; ein Filter beschränkt die Ansicht auf erreichte, abweichende oder nicht beurteilbare Werte. Die drei Kernaussagen fassen erreichte Werte, bestätigte Unterschreitungen und einen sinnvollen nächsten Schritt bei der Datenerfassung zusammen.

## Täglich, wöchentlich oder monatlich

Unter «Profil» → «Deine Reports» die Häufigkeit wählen und «Profil speichern». Sie gilt für das aktive Personenprofil und wird mit dessen vorhandener Speicherlogik synchronisiert. Patricia und Dimitri können unterschiedliche Häufigkeiten verwenden.

Reports werden beim Öffnen aus den gespeicherten Einträgen berechnet. Die Häufigkeit bestimmt die Standardansicht: Kalendertag, Kalenderwoche Montag–Sonntag oder Kalendermonat. Es handelt sich nicht um ein E-Mail- oder Push-Abonnement. Im Report können Zeitraum, Archiv und Datenbasis unabhängig davon umgestellt werden. Ein PDF hält den ausdrücklich exportierten Stand fest.

## Zwei PDF-Varianten

«Reports» → «Als PDF exportieren» → Layout auswählen → «PDF erstellen» → «PDF speichern» oder «PDF öffnen».

- **Kompakt:** eine gestaltete Übersichtsseite mit Zeitraum, Datenabdeckung, Zielkennzahlen, Makronährstoffen und Kernaussagen.
- **Vollständig:** zusätzlich alle verfügbaren Nährstoffzeilen, Datenlücken, Vergleichsregeln, Hinweise und anklickbare Referenzquellen. Die Seitenzahl richtet sich nach dem Inhalt.

Der Export bezieht sich auf das aktive Profil, den ausgewählten Zeitraum und die gewählte Berücksichtigung vollständiger Protokolltage. Im vollständigen PDF stehen alle Nährstoffe, auch wenn die Bildschirmansicht gefiltert ist; dies wird im Exportdialog ausdrücklich erklärt. Der CSV-Export bleibt verfügbar.

Die Datei entsteht vollständig auf dem Gerät mit einer mitgelieferten, auf Version 4.2.1 festgelegten jsPDF-Bibliothek samt Lizenz. Keine PDF-Erstellung bei einem externen Dienst, keine automatische Veröffentlichung und kein Upload zu GitHub. Die Datei ist nicht passwortverschlüsselt und enthält persönliche Angaben; sie wird erst auf ausdrückliche Aktion gespeichert oder geteilt. «PDF teilen» erscheint nur bei unterstützter Dateifreigabe. Auf dem iPhone kann alternativ «PDF öffnen» → Teilen → «In Dateien sichern» verwendet werden. Der tatsächliche Browser entscheidet über seine Speichern-/Teilen-Oberfläche.

## Einordnung der Zahlen

Die bestehenden Report-Berechnungen bleiben unverändert. Ausgelassene oder zukünftige Tage werden nicht als null gerechnet. Bei Datenlücken erscheinen bekannte Teilmengen; bei offenen Protokollen bleibt die Zielbewertung vorläufig. Wochen-/Monatswerte sind Mittelwerte der berücksichtigten Tage, kein vollständiger Nachweis bei fehlenden Tagen.

Verglichen wird mit den aktuellen gespeicherten Profilzielen. Eine Änderung der Ziele schreibt die historischen Verzehrdaten nicht um. Referenzwerte müssen nicht an jedem einzelnen Tag erreicht werden; eine Unterschreitung ist keine Mangeldiagnose. Über 100 Prozent ist bei Mikronährstoffen weder automatisch besser noch eine Sicherheitsobergrenze. Der bestehende 90–110-Prozent-Planbereich für Energie, Kohlenhydrate und Fett ist eine Darstellungsannahme der App. Hinweise und Referenzen bleiben im Report und vollständigen PDF sichtbar.

## Ausgeführte Prüfungen

Erfolgreicher GitHub-Prüflauf: 36272888911. Geprüfter Quellcommit: 2f5fbb589485b633374f5b31baad51612e384c79. Artefakt: 10915349647. Die 13 vorbereiteten Quell-/Testdateien und die beiden Bibliotheks-/Lizenzdateien wurden mit dem heruntergeladenen Prüfartefakt byteweise abgeglichen.

237 Einzelprüfungen bestanden: Kern/Rezept 48, Makroziele 46, Portionsumrechnung 26, Produktimport 22, Proteinübersicht 15, Reportberechnung 43, Synchronisierung 15 und Reportdarstellung/PDF 22. Zusätzlich bestanden je 54 tatsächliche Browserprüfungen in Chromium und WebKit ohne JavaScript-Laufzeitfehler oder unerwartete externe Datenanfragen.

Geprüft wurden Auswahl und Speicherung der Häufigkeit, Wiederherstellung und zweites Gerät, getrennte Profile, fehlende Angaben, Wochen-/Monatsgrenzen, Schaltjahr, aktuelle Referenzen, unveränderte Historie, Filter, Aufklappen, CSV sowie tatsächlich heruntergeladene kompakte, vollständige und leere PDFs. Die PDFs wurden mit pypdf auf Inhalt, Seitenzahl, Profil, Zeitraum und Quellenlinks geprüft und nach Bildrendering visuell kontrolliert. Auch bekannte Teilmengen, Suchbarkeit deutscher Hinweise und kleine Bildschirmbreiten wurden geprüft. Testansichten: 320, 390 und 1440 Pixel.

Alle Browserabläufe verwendeten synthetische Profile und kontrollierte Netzwerkantworten. Keine echten privaten Nutzerstände wurden zum Testen gelesen oder geändert. Dies ist kein neuer Test auf einem physischen Android-/iPhone-Gerät. Native Dateifreigabe hängt von dessen Browser ab. Die Veröffentlichung übernimmt nur Dateien unter kompass/; die übrigen Repository-Seiten bleiben unverändert.

Zum Laden den bisherigen Link oder das vorhandene App-Symbol verwenden. Gegebenenfalls «App aktualisieren» drücken und oben Version 1.7.0 kontrollieren. Keine Neuinstallation oder Löschung der Browserdaten erforderlich.
