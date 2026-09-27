# Nährstoff-Kompass 1.8.0 · Stückportionen und Nährwerttext

Stand: 27.09.2026. Die feste App-Adresse bleibt https://dimitrit86-bot.github.io/mythenquai-open/kompass/ . Das vorhandene App-Symbol bleibt verwendbar. Die Veröffentlichung ändert nur kompass/-Dateien; andere Repository-Seiten, private Datenbanktabellen, Passwort und bestehende Nutzerstände werden nicht zurückgesetzt.

## Stückportion direkt beim Produkt

Unter «Eigenes Produkt» beziehungsweise beim Bearbeiten eines Produkts steht «Stückportion · optional». Dort eine Bezeichnung wie Stück, Scheibe, Riegel oder Becher, eine positive Menge und die Einheit hinterlegen. Beispiel: 1 Stück = 50 g. Die Nährwertbasis bleibt pro 100 g oder pro 100 ml; die Vorschau zeigt zusätzlich die Nährwerte einer Stückportion.

Nach dem Speichern zeigt die Produktsuche die Stückdefinition an. Beim Erfassen lässt sich die neue Einheit auswählen; bei vorhandener Definition wird ein Stück vorgeschlagen. Auch halbe oder andere Bruchteile sind möglich. Die Vorschau und der gespeicherte Tagebucheintrag enthalten beide Angaben, zum Beispiel «2 Stück (100 g)» oder «2 Becher (300 ml)». Die Nährwerte werden mit der hinterlegten Stückgrösse berechnet.

Im Produkt-Mengendialog steht ausserdem «Stückportion hinterlegen» beziehungsweise «Stückportion anpassen». Bei einem allgemeinen Datenbanklebensmittel entsteht eine eigene Vorlage, statt die offizielle Datenquelle zu verändern. Das Bearbeiten einer fremden Haushaltsvorlage erzeugt wie bisher eine eigene Variante.

Die Stückgrösse muss zur Nährwertbasis passen: g bei Angaben pro 100 g, ml bei Angaben pro 100 ml. Gewicht und Volumen werden nicht stillschweigend gleichgesetzt. Ohne bekannte Stückgrösse wird keine Stückzahl mit geratenem Gewicht berechnet. Für Lebensmittel mit nicht essbaren Teilen nur den essbaren Anteil verwenden; bei einem Ei beispielsweise ohne Schale. Die Beispielmenge 50 g ist keine vorgegebene Grösse für jedes Ei.

## Rezepte, gemeinsame Produkte und Historie

Stückportionen stehen auch für Rezeptzutaten zur Auswahl. Intern behalten gespeicherte Zutaten ihre konkrete g-/ml-Menge und zusätzlich die verwendete Stückzahl. Dadurch bleiben die Mengen auch für ältere Clients nachvollziehbar. Beim erneuten Bearbeiten wird die Stückauswahl wiederhergestellt.

Nach der Synchronisierung sehen andere Haushaltsprofile ebenfalls die Stückdefinition des gemeinsamen Produkts. Patricia und Dimitri können unterschiedliche Mengen verwenden. Der Verzehr und die persönlichen Ziele bleiben getrennt. Historische Mahlzeiten behalten ihre damaligen Nährwerte und Mengen, auch wenn später die Produktvorlage oder Stückgrösse geändert wird.

Zum Entfernen einer Stückdefinition die Stückgrösse im Produktformular leeren und das Produkt speichern. Bestehende Produkte ohne Stückangabe bleiben unverändert verwendbar.

## Nährwerttext unter «Eigenes Produkt» auslesen

Im Produktformular gibt es jetzt «Nährwerttext auslesen». Eine kopierte Nährwerttabelle lässt sich direkt einfügen, ohne das noch ungespeicherte Produkt zu verwerfen. Name und bereits eingetragene Stückportion bleiben erhalten.

Die vorhandene Erkennung und Bezugsnormalisierung werden wiederverwendet: Ausgangswerte prüfen, bei Bedarf zum Beispiel 30 g statt 100 g einstellen, auf 100 g/ml umrechnen und bestätigen. Erkannte Werte werden erst in die bearbeitbaren Formularfelder übernommen. Erst «Produkt speichern» speichert die Vorlage; die Textübernahme allein erzeugt weder ein Produkt noch einen Tagebucheintrag.

Beim Abbrechen bleiben die bisherigen Formulareingaben bestehen. Die Bestätigung ersetzt die Nährwertfelder durch die neue Tabelle; nicht erkannte Werte bleiben leer/unbekannt und werden nicht aus alten Werten ergänzt. Der Schweizer Tabellenbegriff «Nahrungsfasern» wird jetzt ebenfalls als Ballaststoffangabe erkannt. Fotoverarbeitung und Textauswertung erfolgen weiterhin lokal im Browser.

## Ei und andere Alltagsbegriffe finden

Eier waren bereits mit ihren Nährwerten in der BLV-Basis enthalten, wurden aber unter «Hühnerei» von anderen Teilworttreffern verdrängt. Die Suche wurde deshalb gezielt überarbeitet, nicht durch erfundene oder doppelte Nährwerte erweitert.

«Ei», «Eier», «Ei roh» und «Eier gekocht» finden die passenden vorhandenen Datensätze. Roh und gekocht bleiben unterscheidbar. Weitere Suchbegriffe und Pluralformen wie Linsen, Kichererbsen, Brokkoli, Zucchini und Rüebli wurden ergänzt. Bei kurzen Suchwörtern werden vollständige Wörter berücksichtigt; relevante Namen stehen vor zufälligen Teilworttreffern. Die offizielle Nährwertdatenbank und die bisherigen Marken-/Händlerkataloge bleiben erhalten.

## Reports und PDF bleiben verfügbar

Die bereits veröffentlichte Reportoberfläche ist weiter enthalten: Unter «Profil» kann täglich, wöchentlich oder monatlich als Report-Voreinstellung gewählt werden. Die Reports zeigen Makros, Vitamine, Mineralstoffe und Spurenelemente sowie Zielvergleich und Datenvollständigkeit. Fehlende Angaben sind keine Nullzufuhr; eine Zielunterschreitung ist keine Mangeldiagnose.

«PDF exportieren» bietet eine kompakte Übersicht oder den vollständigen Report. Die Datei wird auf dem Gerät erzeugt, nicht über einen neuen externen PDF-Dienst. Die Häufigkeitswahl ist eine Anzeige-/Zeitraumvoreinstellung in der App und kein automatisch versendetes E-Mail-Abonnement.

## Tatsächlich ausgeführte Prüfungen

Erfolgreicher GitHub-Prüflauf: 36301209309. Geprüfter Quellcommit: 3967d91b52bd69765721a63e563c8fb95854dfb9. Artefakt: 10925507271.

265 Einzelprüfungen bestanden: 237 bestehende Rechen-/Makro-/Report-/Import-/Sync-Tests und 28 neue Stück-/Such-/Texttests. Die heruntergeladenen geänderten App-, Core-, Scanner-, Geräte-, Cache- und HTML-Dateien wurden mit den vorbereiteten Änderungen byteweise abgeglichen; der Suchmodul-Unterschied betrifft nur die Formatierung einer Objektschreibweise.

Zusätzlich bestanden jeweils 35 tatsächliche Browserabläufe in Chromium und WebKit. Getestet wurden unter anderem Textimport im eigenen Produkt, 30-g-Normalisierung, Speichern der Stückdefinition, Bruchteile, Anzeige von Anzahl und Masse, Rezeptzutaten, gemeinsame Nutzung über zwei Profile, getrennte Tagebücher, g/ml-Prüfung, Suchbegriffe für Eier, Abbruch ohne Datenverlust, Report-Voreinstellung, tatsächlicher PDF-Download und Neuladen. Keine JavaScript-Laufzeitfehler und keine unerwarteten externen Anfragen.

Der erzeugte kompakte PDF-Report wurde zusätzlich gerendert und visuell geprüft; die mobile Produktansicht ebenfalls. Die Reportoberfläche wurde bei 320, 390 und 1440 Pixeln ohne horizontales Überlaufen geprüft. Die Tests verwendeten ausschliesslich synthetische Haushaltsprofile mit kontrollierten Serverantworten und echtem Browserspeicher. Ein Hardwarekamera- oder Installationstest auf einem physischen iPhone beziehungsweise Android-Handy wird nicht behauptet.

## Update laden

Bisherigen Link oder App-Symbol öffnen, bei Bedarf «App aktualisieren» drücken und oben Version 1.8.0 kontrollieren. Keine Neuinstallation und keine Löschung von Browserdaten notwendig. Noch offene Eingaben wie gewohnt vor einem Neuladen speichern.
