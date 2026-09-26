# Nährstoff-Kompass 1.6.0 · Persönliche Nährstoffreports

## Report-Häufigkeit im Profil

Unter «Profil» → «Deine Reports» kann jedes Personenprofil «Täglich», «Wöchentlich» oder «Monatlich» wählen. «Profil speichern» übernimmt die Auswahl in die bestehende geschützte Speicherung und Synchronisierung. Patricia und Dimitri können unterschiedliche Einstellungen verwenden. Bisherige Profile zeigen Wöchentlich als Vorauswahl; eine blosse Änderung des Auswahlfelds speichert nichts.

Die Häufigkeit bestimmt die Standardansicht in «Reports». Auswertung und Aktualisierung erfolgen beim Öffnen der App-Ansicht anhand der vorhandenen Einträge. Es wurde kein E-Mail-Versand, Push-Dienst oder Hintergrund-Scheduler eingerichtet. Innerhalb der Report-Sektion lassen sich andere Zeiträume ansehen, ohne die gespeicherte Häufigkeit zu ändern.

## Neue Report-Sektion

Die Navigation enthält «Reports». Verfügbar sind Kalendertage, Wochen von Montag bis Sonntag und Kalendermonate. Vorheriger/nächster Zeitraum, laufender Zeitraum, letzter abgeschlossener Zeitraum und frühere Zeiträume mit Einträgen lassen sich auswählen. Auch auf «Heute» gibt es einen Report-Einstieg. Die Auswertung bleibt auf das aktive Personenprofil begrenzt.

Der Report gruppiert Energie/Makronährstoffe, Vitamine, Mineralstoffe (Mengenelemente), Spurenelemente und weitere Nährstoffangaben. Je Nährstoff stehen die bekannte Zufuhr im Tagesmittel, das aktuelle persönliche Ziel, der Prozentvergleich soweit zulässig und ein ausgeschriebener Status. Aufklappen zeigt Tageswerte, Datenlücken mit betroffenen Lebensmitteln, die Referenzquelle und – bei bewertbaren Tagen – die Anzahl erreichter bzw. unter dem Vergleich liegender Einzeltage. Wochen-/Monatsmittel und tägliche Verteilung werden getrennt ausgewiesen.

Ein Filter beschränkt die Ansicht auf erreichte Werte, Abweichungen oder nicht abschliessend beurteilbare Angaben. «Report als CSV» exportiert die aktuelle Auswertung einschliesslich Profilname, Datumsbereich, Datenbasis, Einheiten, Status und Vergleichsgrundlage. Die Datei enthält persönliche Angaben und wird nur auf ausdrücklichen Klick heruntergeladen, nicht auf GitHub veröffentlicht.

## Erreicht, darunter oder nicht beurteilbar

Bei passenden Mindestvergleichswerten wie Protein und vielen Vitamin-/Mineralstoffreferenzen bedeutet «Vergleichswert erreicht» mindestens 100 %. Für Energie, Fett und Kohlenhydrate gilt im Report ein Planbereich von 90–110 % des bereits gespeicherten Ziels. Diese Spanne ist ausdrücklich eine Darstellungsannahme der App, keine medizinische Toleranzgrenze; das Update ändert keine Zielwerte.

Mehr als 100 % wird bei Mikronährstoffen nicht als besondere Gesundheitsleistung oder automatisch als gefährlich ausgegeben. Fehlt für eine Angabe die eindeutige Zielrichtung, bleibt es beim Zahlenvergleich. Ohne Ziel oder bei inkompatiblen Bezugsformen erfolgt keine Erfolgsbewertung; beispielsweise wird kein unzulässiger Folat-Prozentvergleich ergänzt.

Nicht protokollierte und zukünftige Tage werden nicht als Nullzufuhr in den Durchschnitt eingerechnet. Der Report nennt erfasste, vollständig markierte, berücksichtigte und noch fehlende Tage ausdrücklich. Erreichte Werte in den protokollierten Tagen sind kein Nachweis für eine vollständig abgedeckte Woche oder einen Monat.

Fehlende Nährstoffangaben bleiben unbekannt. Eine bekannte Teilmenge wird als Untergrenze gekennzeichnet, nicht als vollständige Zufuhr. Solche Werte erhalten «Datenlücken», nicht «Ziel verfehlt». Sind alle Nährstoffzahlen vorhanden, aber Protokolltage noch nicht als vollständig markiert, ist der Vergleich vorläufig. Bestätigte Erfolgs-/Unterschreitungszähler verwenden nur abgeschlossene Protokolle mit vollständigen Angaben für den jeweiligen Nährstoff. Die Option «Nur als vollständig protokolliert markierte Tage» erlaubt eine gezielte Auswahl. Im Report lassen sich Protokolltage direkt öffnen und in der Tagesansicht abschliessen.

## Vergleichsgrundlage und fachliche Grenzen

Auch frühere Zeiträume werden mit den aktuell gespeicherten Profilzielen verglichen; es gibt noch keine historische Zielversionierung. Ein geändertes Ziel ändert den Vergleich, nicht die gespeicherten Verzehrmengen. Frühere Reports werden bei Bedarf neu berechnet und sind keine unveränderlich archivierten Dokumente. Für einen festen Stand kann der CSV-Export verwendet werden.

Referenzwerte müssen nicht jeden Tag exakt erreicht werden. Eine rechnerische Unterschreitung ist keine Mangeldiagnose. Besonders Vitamin D hängt auch von körpereigener Bildung ab, die ein Ernährungstagebuch nicht misst. Der Report enthält entsprechende Hinweise, keine Supplement-Ausgleichsdosen und keinen Gesamt-Gesundheitsscore. Quellen: DGE FAQ Referenzwerte (https://www.dge.de/gesunde-ernaehrung/faq/referenzwerte/) und DGE Vitamin D (https://www.dge.de/wissenschaft/referenzwerte/vitamin-d/), geprüft am 26.09.2026. Die vorhandenen einzelnen Nährstoffquellen bleiben in den Detailzeilen sichtbar.

## Datenschutz und Update

Keine echten Haushaltsdaten wurden zum Testen gelesen oder verändert. Keine Serverfunktionen, Tabellen, Passwörter, Referenzregeln oder Lebensmittelbestände wurden ersetzt. Vorhandene Produkte, gemeinsame Rezepte, Tagesbilanzen und übrige App-Funktionen bleiben erhalten. Die Veröffentlichung betrifft ausschliesslich kompass/; die Tennisseiten bleiben unverändert.

Feste Adresse: https://dimitrit86-bot.github.io/mythenquai-open/kompass/ . Bei Bedarf «App aktualisieren» verwenden und Version 1.6.0 kontrollieren. Keine Neuinstallation und keine Löschung von Browserdaten erforderlich.

## Tatsächlich ausgeführte Prüfungen

Erfolgreicher GitHub-Prüflauf 36269662319; getesteter Anwendungscommit 21364003ab5cf1ffebb9fabddf18b0e94943b6f8; Artefakt 10915052642. Alle 11 vorbereiteten Anwendungs-/Testdateien und der Browserprüfskript wurden mit dem heruntergeladenen CI-Artefakt byteweise abgeglichen.

215 Einzelprüfungen bestanden: 48 Kern/Rezept, 46 Makroziele, 26 Portionsumrechnung, 22 Produktimport, 15 Proteinübersicht, 15 Synchronisierung und 43 neue Report-Prüfungen. Dazu je 38 echte Browserabläufe in Chromium und WebKit, mit synthetischen Haushaltsprofilen und bestehendem verschlüsseltem Browserspeicher. Keine JavaScript-Laufzeitfehler und keine nicht abgefangenen externen Datenanfragen.

Geprüft wurden Auswahl/Speichern/Neuladen, getrennte Profile, zweites Gerät, Tages-/Wochen-/Monatsgrenzen einschliesslich Schaltjahr, Zieländerung ohne Historienmutation, Null gegenüber unbekannt, vollständige gegenüber offenen Protokolltagen, CSV und Ansichten bei 320/390/1440 Pixeln ohne horizontales Überlaufen. Die erzeugten mobilen Chromium-/WebKit-Ansichten wurden zusätzlich visuell geprüft. Ein neuer Test auf physischer Android-/iPhone-Hardware wird nicht behauptet.
