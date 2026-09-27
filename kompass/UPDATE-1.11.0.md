# Nährstoff-Kompass 1.11.0 · Cup-Referenzen und Gemüse in Stück

Stand: 27.09.2026. Die feste Adresse bleibt https://dimitrit86-bot.github.io/mythenquai-open/kompass/ . Die bestehende Version 1.10.0 mit Cups und vollständigem Rezept-Textimport wird erweitert. Keine persönlichen Profile, Ziele, Produkte, Rezepte oder Tagebucheinträge werden zurückgesetzt.

## Ungefähre Umrechnungen statt einer Waage für jede Zutat

Für 31 gezielt zugeordnete vorhandene Lebensmittel sind jetzt 41 Cup-/Füllvarianten und 39 Stück-/Grössenvarianten hinterlegt. Die Zuordnung verwendet die genaue Lebensmittelkennung und den Namen, nicht eine unkontrollierte Wortähnlichkeit. Paprikapulver erhält deshalb keine Stückgewichte einer frischen Peperoni. Vorhandene eigene Cup-/Stückdefinitionen haben Vorrang.

Unter anderem enthalten: rohe Zwiebel, rote und grüne Peperoni/Paprika, Karotte, Tomate, Zucchini, Gurke, Champignon, Broccoli, Blumenkohl, Spinat, Knoblauch, Apfel, Banane, rohes Vollei, Mandeln, weisses Mehl, Zucker, Haferflocken sowie getrennte Varianten für trockenen und gekochten Reis, Quinoa und Kichererbsen. Nicht jedes dieser Lebensmittel hat sowohl eine Cup- als auch eine Stückreferenz.

## Stückmengen erfassen

Lebensmittel auswählen, als Einheit «Stück» verwenden und bei Bedarf die Referenzgrösse wechseln. Beispiele aus den hinterlegten USDA-Referenzen für den essbaren Anteil:

| Lebensmittel, roh | Klein | Mittel | Gross |
|---|---:|---:|---:|
| Zwiebel | ca. 70 g | ca. 110 g | ca. 150 g |
| Peperoni/Paprika, rot oder grün | ca. 74 g | ca. 119 g | ca. 164 g |
| Karotte | ca. 50 g | ca. 61 g | ca. 72 g |
| Tomate | ca. 91 g | ca. 123 g | ca. 182 g |
| Zucchini | ca. 118 g | ca. 196 g | ca. 323 g |

Zum Beispiel werden zwei mittlere Zwiebeln mit ca. 220 g oder eine halbe mittlere Peperoni mit ca. 59,5 g berechnet. Die Nährwertvorschau und der Tagebucheintrag zeigen ausdrücklich «ca.» beziehungsweise «geschätzt». Diese Grössen sind praktische Quellenreferenzen, keine neu erhobenen Durchschnittsgewichte des Schweizer Handels.

Du kannst das Grammgewicht pro Stück unmittelbar überschreiben. Eine eigene Angabe wird anstelle der Referenz verwendet. Über das Hinterlegen einer Stückportion lässt sich daraus eine dauerhafte eigene Produktvariante machen; bei fremden/generischen Vorlagen bleibt das Original erhalten. Schale, Kerne, Stiel und andere nicht gegessene Teile nicht mitrechnen. Beim Ei beziehen sich die Grammangaben auf den Inhalt ohne Schale; die USDA-Grössen sind keine EU-/CH-Gewichtsklassen für Eier mit Schale.

## Cups mit Zustand und Füllweise

Bei einer passenden Zutat ist das Grammgewicht einer Cup vorausgefüllt. Unter «Zustand / Füllweise · Referenz oder eigene Angabe» lässt sich zum Beispiel zwischen gehackten Zwiebeln und Scheiben wählen. Beispiele für die in der App angenäherte Küchen-Cup von 240 ml:

| Zutat / Form | Referenzgewicht pro Cup |
|---|---:|
| Zwiebel, gehackt/gewürfelt | ca. 160 g |
| Zwiebel, in Scheiben | ca. 115 g |
| Peperoni/Paprika, gehackt | ca. 149 g |
| Peperoni/Paprika, in Streifen/Scheiben | ca. 92 g |
| Weisses Weizenmehl, locker | ca. 125 g |
| Haferflocken, trocken | ca. 89 g |
| Weisser Langkornreis, trocken | ca. 185 g |
| Weisser Langkornreis, gekocht | ca. 158 g |

Der daraus angezeigte Wert in g/ml ist eine ungefähre Füll-/Schüttdichte einschliesslich Zwischenräumen, keine gemessene Materialdichte. 160 g pro 240 ml entsprechen beispielsweise rechnerisch rund 0,667 g/ml. Bei Wechsel auf 250 ml oder US cup 236,5882365 ml wird das Gewicht proportional angepasst; das setzt dieselbe Zutat, Schnittform und Füllweise voraus. Eine pauschale Gleichsetzung von 1 Cup mit 240 g erfolgt nicht.

Die Quellen-Cups werden ausdrücklich näherungsweise einer Küchen-Cup von 240 ml zugeordnet, angelehnt an NIST Metric Kitchen. Die Quellenwerte behaupten keine exakt gemessene Dichte für das konkrete Produkt. Du kannst das Gewicht pro Cup korrigieren oder eine eigene Definition speichern. Eine vorhandene eigene Dichte bzw. Cupdefinition wird nicht stillschweigend ersetzt. Für nicht abgedeckte Lebensmittel bleibt eine eigene Umrechnung notwendig. Die neue Schüttdichte wird nicht ungeprüft auf gewöhnliche ml-, TL- oder EL-Eingaben übertragen.

## Ganze Rezepte einfügen

Die Funktion «Gerichte → Rezept hineinkopieren» aus v1.10.0 bleibt vorhanden. Nach dem Auslesen und Zuordnen einer Zutatenzeile stehen passende Referenzgrössen auch in der Rezeptvorschau bereit. Beispielsweise kann «2 grosse Zwiebeln» die grosse Quellenreferenz vorschlagen; «1 cup Reis, gekocht» verwendet nach Zuordnung zum gekochten Reis dessen Cupgewicht, nicht das Gewicht von trockenem Reis.

Die Zuordnung eines Lebensmittels bleibt kontrollierbar. Du kannst Grösse/Form wählen oder das Einzelgewicht überschreiben. Jede relevante Änderung setzt die Bestätigung zurück. Nicht zuordenbare Zutaten werden nicht mit erfundenen Nährwerten befüllt. Erst nach Prüfung und Bestätigung wird ein Entwurf geöffnet; «Gericht speichern» speichert die Vorlage. Der ursprüngliche Rezepttext und die Zubereitung bleiben erhalten.

Schätzungen sind in den Zutaten, der Rezeptvorschau und bei daraus erfassten Gerichten kenntlich. Intern bleiben Mengen in g/ml gespeichert; zusätzliche Metadaten bewahren Stück-/Cupform, Quelle und Schätzkennzeichnung. Nach dem normalen Abgleich sind gespeicherte Varianten und Gerichte in anderen Haushaltsprofilen verfügbar. Gegessene Mengen und persönliche Tagebücher bleiben getrennt. Spätere Änderungen einer Vorlage verändern keine alten protokollierten Nährwertkopien.

## Datenquellen und Grenzen

Die Ergänzung betrifft Haushaltsmasse, nicht neue Nährwerte. Die bisherigen BLV-/Hersteller-/Produkt-Nährwertangaben werden nicht durch USDA-Nährwertdaten ersetzt.

- USDA FoodData Central, SR Legacy, Datenstand April 2018: https://fdc.nal.usda.gov/download-datasets/
- Offizieller Quell-Export: https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_csv_2018-04.zip
- King Arthur Baking, allgemeine Zeile «Oats (old-fashioned or quick-cooking)», 89 g pro Cup: https://www.kingarthurbaking.com/learn/ingredient-weight-chart
- NIST Metric Kitchen, ausdrücklich ungefähre Küchenäquivalente: https://www.nist.gov/pml/owm/metric-si/metric-kitchen/metric-kitchen-cooking-measurement-equivalencies

Quellengrösse, Masse, Quellenkennung und Abruf-/Prüfdatum sind im separaten Referenzkatalog enthalten. Der USDA-Abruf lief erfolgreich unter 36337599401. 79 ausgewählte USDA-Masszeilen wurden mit dem tatsächlich heruntergeladenen Quell-Dataset auf Kennung, Beschreibung, Bezugsmenge und Grammgewicht abgeglichen; die zusätzliche Haferflockenreferenz stammt aus der genannten Backzutaten-Tabelle. Unterschiede durch Sorte, Reife, Schnitt, Packung, Kochwasseraufnahme und Füllweise bleiben möglich. Wiegen ist für die konkrete Menge genauer als diese Näherung.

## Tatsächlich ausgeführte Prüfungen

Erfolgreicher GitHub-Prüflauf: 36339523168. Geprüfter Quellcommit: 6cdda415ec6e1e067ed481b8667d87c3e0b02622. Artefakt: 10938745976.

429 Einzelprüfungen bestanden, davon 42 neue Referenzmass-Tests. Zusätzlich bestanden jeweils 47 echte Browserabläufe in Chromium und WebKit mit synthetischen Haushaltsprofilen und kontrollierten API-Antworten. Geprüft wurden automatische Stückreferenzen, Grössenwahl, manuelle Priorität, Cup-Formen und Volumenwechsel, fehlende Umrechnungen, gespeicherte Schätzmetadaten, kompletter Rezeptimport, geteilte Varianten, getrennte Tagebücher, unveränderte Historie und Darstellung bei 320, 390 und 1440 Pixeln. Keine JavaScript-Laufzeitfehler oder unerwarteten externen Anfragen.

Alle 16 vorbereiteten Anwendungs-/Testdateien wurden mit dem heruntergeladenen CI-Artefakt byteweise abgeglichen. Die 429 Einzelprüfungen und die Release-Archivprüfung wurden auf diesem Artefakt erneut ausgeführt. Die mobilen WebKit-Ansichten wurden visuell geprüft. Ein neuer Test mit einem physischen iPhone oder Android-Gerät wird nicht behauptet.

Keine echten privaten Profile wurden für Tests gelesen oder verändert. Keine Datenbank-/Serveränderung und keine neuen externen Dienste. Die Produktionsveröffentlichung betrifft nur kompass/; die übrigen Seiten bleiben unverändert. Die Release Notes enthalten v1.11.0 und erscheinen entsprechend dem bestätigten Stand des jeweiligen Profils.

## Update laden

Bisherigen Link oder vorhandenes App-Symbol öffnen, bei Bedarf «App aktualisieren» drücken und oben Version 1.11.0 kontrollieren. Offene Eingaben vorher speichern. Keine Neuinstallation oder Löschung von Browserdaten nötig.
