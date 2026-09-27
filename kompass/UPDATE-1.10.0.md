# Nährstoff-Kompass 1.10.0 · Cups und komplette Rezepte

Stand: 27.09.2026. Die feste App-Adresse und das installierte Symbol bleiben unverändert. Die bestehende Version 1.9.1 wird erweitert; private Profile und Daten werden nicht zurückgesetzt.

## Cups bei Produkten und Rezeptzutaten

Die Mengenauswahl enthält jetzt drei ausdrücklich bezeichnete Varianten: Cup 240 ml (Küche), Cup 250 ml (metrisch) und US cup 236,6 ml. Für die US-Variante wird intern mit 236,5882365 ml gerechnet. Die richtige Variante richtet sich nach dem Rezept beziehungsweise Messbecher; eine Cup wird nicht pauschal mit einem Grammgewicht gleichgesetzt.

Mengen lassen sich als Dezimalzahl mit Punkt oder Komma und als Bruch eingeben, beispielsweise 0,5, 1/2, 1 1/2 oder ½. Vorschau und Tagebuch zeigen sowohl die Cup-Menge als auch die zugehörige Menge in Gramm beziehungsweise Millilitern. Beim proportionalen Ändern eines Tagebucheintrags werden beide Darstellungen mitgeführt.

Für Produkte mit Angaben pro 100 ml wird das Cup-Volumen direkt verwendet. Bei Angaben pro 100 g braucht die Rechnung ein bekanntes Gewicht pro Cup dieser Zutat oder deren Dichte. Fehlt beides, fragt die App danach und blockiert eine scheinbar genaue Nährwertberechnung. Mehl, Haferflocken, Öl und Milch erhalten nicht stillschweigend dieselbe Dichte.

Unter «Eigenes Produkt» kann zusätzlich zur Stückportion eine Cup-Umrechnung gespeichert werden: Cup-Grösse und Grammgewicht. Die Definition wird in der Produktsuche angezeigt und nach erfolgreicher Synchronisierung mit der Produktvorlage im Haushalt verfügbar. Beim Erfassen kann ein abweichendes Gewicht für die konkrete Menge eingetragen werden; «Cup-Gewicht im Produkt hinterlegen» führt zum Speichern einer dauerhaften Definition. Bei fremden oder allgemeinen Vorlagen bleibt die bestehende Variantenlogik erhalten.

Intern werden gespeicherte Rezeptzutaten weiterhin in g/ml abgelegt. Zusätzliche Metadaten erhalten die ursprüngliche Cup-Darstellung. Dadurch benötigen gespeicherte Gerichte keine neue Basis-Schema-Version. Bereits protokollierte Nährwertkopien werden bei einer späteren Änderung des Produkts oder Gerichts nicht umgeschrieben.

Die praktische Küchenumrechnung orientiert sich an NIST Metric Kitchen; die konkreten auswählbaren Cup-Grössen werden in der Oberfläche genannt. Quelle: https://www.nist.gov/pml/owm/metric-si/metric-kitchen/metric-kitchen-cooking-measurement-equivalencies . Ein Zutatengewicht muss zur tatsächlichen Zutat und Füllweise passen.

## Ganzes Rezept hineinkopieren

Unter «Gerichte» steht «Rezept hineinkopieren». Den kompletten Text einschliesslich Titel, Portionszahl, Zutaten und Zubereitung einfügen, die Cup-Grösse wählen und «Rezept auslesen» drücken. Am zuverlässigsten sind klare Überschriften und eine Zutatenzeile pro Zeile. Deutsch und einfache englische Zutatenzeilen werden unterstützt. Das ist ein Textimport, kein automatischer Abruf einer Rezept-URL.

Die lokale Erkennung schlägt Titel, Portionszahl, Mengen und Einheiten vor. Gramm, Kilogramm, Milliliter, Liter, Cups, Stück sowie TL/tsp und EL/tbsp werden unterstützt; für Löffel verwendet dieser Import ausdrücklich 5 beziehungsweise 15 ml. Abweichende Löffelmasse müssen in ml eingegeben werden. Auch Brüche und einfache Packungsangaben wie 2 x 400 g lassen sich übernehmen; Abtropfgewicht und essbaren Anteil kontrollieren.

In der Vorschau jede Zutat mit dem passenden vorhandenen Lebensmittel verknüpfen. Eigene, gemeinsame und hinterlegte Katalogprodukte sind durchsuchbar. Suchvorschläge sind keine verifizierte Identifikation: Sorte, roh/gekocht, Fettstufe sowie Gewichts- und Volumenbasis prüfen. Mengenbereiche, «nach Geschmack», fehlende Portionszahl oder Stückgewichte müssen bewusst ergänzt werden, statt automatisch geschätzt zu werden.

Für eine noch nicht zuordenbare Zutat gibt es «Ohne Nährwertdaten: später ergänzen». Diese Zutat bleibt im Rezept, ihre Nährwerte bleiben unbekannt. Eine unvollständige Vorschau wird ausdrücklich markiert; fehlende Werte werden nicht als Null gerechnet. Eine Zeile darf nur dann als reine Notiz ausgeschlossen werden, wenn sie tatsächlich keine Zutat ist. Die Bestätigung wird bei Änderungen zurückgesetzt.

Nach Kontrolle zeigt die App eine Nährwertvorschau pro Portion. «Als Rezeptentwurf übernehmen» öffnet den normalen Rezepteditor, speichert aber noch kein Gericht. Dort können Zutaten weiter geändert und das fertige Gewicht nach dem Kochen ergänzt werden. Erst «Gericht speichern» sichert die Vorlage und macht sie nach dem normalen Abgleich für andere Haushaltsprofile verfügbar. Eine gegessene Portion wird weiterhin separat ins persönliche Tagebuch gebucht.

Zubereitung und der vollständige unveränderte Originaltext bleiben im Gericht nachlesbar. Im kopierten Text behauptete Kalorienwerte werden nicht als Ersatz für die Zutatenberechnung verwendet. Es werden keine pauschalen Kochverlust- oder Vitaminverlustfaktoren erfunden. Maximale Eingabe: 30’000 Zeichen und 200 Zutatenzeilen.

## Datenschutz und bestehende Funktionen

Parsing und Zutatenzuordnung finden lokal im Browser statt. Der eingefügte Text geht nicht an einen externen KI-Dienst. Erst ein ausdrücklich gespeichertes Gericht wird über die vorhandene geschützte Haushalts-Synchronisierung abgelegt. Der Import fügt keine neuen externen Dienste hinzu.

Fotoerkennung beider Arten, eigener Nährwerttext, Stückportionen, Reports/PDF, Ernährungsziele, Protein-Glückwunsch, gemeinsame Vorlagen, Datensicherung und Lesestand der Release Notes bleiben enthalten. Ein offener Rezeptimport wird bei Profilwechsel beziehungsweise Update als ungespeicherte Eingabe berücksichtigt. Abbrechen speichert keine neue Vorlage und ändert keine Tagesbilanz.

Der Release-Katalog enthält v1.10.0 zusätzlich zu v1.9.0 und v1.9.1. Damit erscheinen diese Neuerungen beim nächsten passenden Profilstart und bleiben im Release-Archiv nachlesbar. Alle Produktionsänderungen dieses Updates liegen unter kompass/; andere Seiten des Repositorys bleiben unverändert. Servercode und Datenbanktabellen wurden nicht verändert.

## Tatsächlich ausgeführte Prüfungen

Erfolgreicher GitHub-Prüflauf: 36335263453. Geprüfter Quellcommit: 516363fb81a70ce1a14853772306e2d6844df75f. Artefakt: 10936598317.

387 Einzelprüfungen bestanden: 323 bisherige und 64 neue Cup-/Rezepttests. Zusätzlich bestanden jeweils 40 tatsächliche Browserabläufe in Chromium und WebKit mit synthetischen Haushaltsprofilen, abgefangenen API-Antworten und echtem Browserspeicher. Keine JavaScript-Laufzeitfehler und keine unerwarteten Netzwerkanfragen.

Die Browserprüfungen umfassen explizite Cup-Gewichte, Volumenprodukte, Brüche, fehlende Umrechnungen, Speicherung und Mengenskalierung, kompletten Rezeptimport, Stückgewicht, unbekannte Zutaten, sichere Pflichtbestätigung, Zubereitung/Originaltext, unveränderte protokollierte Nährwerte, gemeinsame Vorlagen und getrennte Tagebücher. Cup- und Rezeptansichten wurden bei 320, 390 und 1440 Pixeln ohne horizontales Überlaufen geprüft. Die mobile Rezeptansicht wurde zusätzlich visuell kontrolliert.

Alle vorbereiteten geänderten Anwendungsdateien wurden mit dem heruntergeladenen CI-Artefakt abgeglichen; die 387 Einzeltests und die Release-Archivprüfung wurden auf diesem Artefakt erneut ausgeführt. Ein neuer Test auf physischen iPhones/Android-Handys wird nicht behauptet. Es wurden keine echten privaten Nutzerstände für Tests gelesen oder verändert.

## Update laden

Den bisherigen Link oder das vorhandene App-Symbol verwenden. Gegebenenfalls «App aktualisieren» drücken und oben Version 1.10.0 kontrollieren. Offene Eingaben vorher speichern. Keine Neuinstallation und keine Löschung von Browserdaten nötig.
