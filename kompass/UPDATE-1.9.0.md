# Nährstoff-Kompass 1.9.0 · Ein Foto, zwei Wege

Stand: 27.09.2026. Die feste Adresse bleibt https://dimitrit86-bot.github.io/mythenquai-open/kompass/ . Das vorhandene App-Symbol und alle bisherigen Daten bleiben verwendbar.

## Produkt fotografieren und Nährwerte suchen

Unter «Erfassen» den vorhandenen Scanner öffnen, «Packung fotografieren» oder «Foto aus Galerie» wählen und danach «Produkt erkennen & suchen» drücken. Die App versucht zunächst, einen lesbaren Produktbarcode im Foto zu erkennen und seine Prüfziffer zu prüfen. Ohne passenden Barcode liest sie die sichtbare Beschriftung auf dem Gerät und schlägt daraus Marke und Produktbezeichnung als Suchbegriff vor.

Die Suche kombiniert eure eigenen/gemeinsamen Produkte und den hinterlegten Katalog mit dem bestehenden Online-Produktdienst (Open Food Facts). Die Produktsuche wird durch den ausdrücklich gewählten Foto-Button gestartet, nicht allein durch die Bildauswahl oder während jeder Texteingabe. Nur Suchwörter oder Barcode werden gesendet. Der erkannte Suchbegriff ist editierbar; bei falscher oder zu ausführlicher Beschriftung lässt er sich kürzen und erneut suchen.

Die Treffer zeigen Name, Quelle und vorhandene Nährwerte. Erst den richtigen Treffer auswählen, Variante und Bezugsmenge pro 100 g oder 100 ml kontrollieren und bestätigen. Anschliessend lassen sich die Werte im Produktformular bearbeiten und eine Stückportion hinterlegen. Erst «Produkt speichern» speichert eine neue Vorlage; eine gegessene Menge wird weiterhin separat erfasst. Bereits bekannte Produkte werden wiederverwendet, statt allein durch denselben Scan ein Duplikat zu erzeugen.

## Nährwerttabelle direkt auslesen

Mit demselben hochgeladenen Foto steht auch «Nährwerttabelle auslesen» zur Verfügung. Damit werden die Zahlen direkt aus der Tabelle übernommen, ohne Produktdaten im Internet zu suchen. Die vorhandene bearbeitbare Vorschau bleibt erhalten: Ausgangswerte kontrollieren, erste/letzte Tabellenspalte wählen und die Bezugsmenge korrigieren, beispielsweise 30 g → 100 g oder 250 ml → 100 ml.

Die Umrechnung lautet Ausgangswert × 100 ÷ Bezugsmenge. Gewicht und Volumen werden nicht gleichgesetzt. Bereits korrigierte Ausgangswerte bleiben beim Wechsel zwischen den beiden Foto-Wegen erhalten. Für eine andere Ansicht der Packung ein neues Foto auswählen. Unbekannte Angaben bleiben unbekannt; Nullwerte werden nicht mit fehlenden Werten verwechselt.

## Direkt aus «Eigenes Produkt»

Neben «Nährwerttext auslesen» steht im eigenen Produkt jetzt «Foto: Produkt oder Nährwerte». Beide Foto-Wege können damit ein angefangenes Produktformular ergänzen. Eine bereits eingegebene Stückdefinition bleibt erhalten; nach einer geänderten Nährwertbasis die dazu passende Einheit kontrollieren. Beim Abbrechen bleiben die vorherigen Formularwerte erhalten. Eine bestätigte Übernahme ersetzt die Nährwertfelder durch die neue Quelle; nicht bekannte Werte werden nicht aus alten Angaben dazugemischt.

Nach dem normalen Speichern und erfolgreichen Serverabgleich steht die neue Vorlage auch dem anderen Haushaltsprofil zur Verfügung. Tagebuchmengen und Ziele bleiben getrennt.

## Grenzen und Privatsphäre

Dies ist eine Erkennung lesbarer Produktbeschriftung beziehungsweise Barcodes mit anschliessender Datensuche, keine umgekehrte Bildähnlichkeitssuche. Unscharfe Fotos, rein grafische Logos und lose Lebensmittel ohne Beschriftung liefern nicht zuverlässig einen eindeutigen Produktnamen. Die App erfindet keine Marke oder Nährwerte aus dem Aussehen einer Verpackung oder eines Tellers. Bei unlesbaren Fotos oder ausbleibenden Treffern werden ein korrigierter Suchbegriff, ein Barcode oder die direkte Nährwerttabelle angeboten.

Alle Bilder werden lokal im Browser verarbeitet und beim Schliessen des Scanners aus dem aktiven Arbeitsspeicher freigegeben. Sie werden nicht an einen Bild-, KI- oder Suchdienst hochgeladen und nicht öffentlich veröffentlicht. Die erste Bereitstellung der lokalen Erkennungsdateien und neue Online-Treffer benötigen eine Internetverbindung. An den bereits vorhandenen authentifizierten Suchdienst gehen ausschliesslich die Suchwörter oder die Produktnummer, keine Körperdaten, Tagesbilanzen oder Bilddateien. Open-Food-Facts-Daten können unvollständig oder veraltet sein; die tatsächliche Packung kontrollieren.

Schliessen, ein neues Foto und Profilwechsel entwerten laufende Erkennungs-/Suchantworten. Eine veraltete Antwort darf keine neue Eingabe überschreiben. Der Update-Button verhindert das Neuladen bei geöffnetem Scanner. Bei Netzfehlern bleiben hinterlegte Treffer und manuelle Eingaben nutzbar.

## Bestehende Funktionen

Die aktuelle 1.8.1-Basis wird erweitert, nicht durch einen alten Entwicklungsstand ersetzt. Reports und PDF-Export, Report-Häufigkeit, Stückportionen, Eier-Suche, Hersteller-/Händlerkataloge, Ernährungsziele, geteilte Vorlagen, verschlüsselte Sicherung und Synchronisierung bleiben enthalten. Die Rechen-, Report-, Katalog-, Stück-, Such- und Sync-Module wurden gegen die vorherige Version byteweise auf unveränderten Inhalt geprüft.

Keine privaten Profildaten, Passwörter, Tabellen oder Serverfunktionen wurden für dieses Release verändert. In der Produktionsbranch werden nur Dateien unter kompass/ aktualisiert; andere Repository-Seiten bleiben unverändert.

## Tatsächlich ausgeführte Prüfungen

Erfolgreicher GitHub-Prüflauf: 36319154012. Geprüfter Quellcommit: 6e7b4d467afc2456b12caa5966fd9d9d591b3906. Heruntergeladenes Artefakt: 10932120533.

294 Einzelprüfungen bestanden, einschliesslich 275 bestehender Rechen-/Makro-/Report-/Portions-/Text-/Sync-Tests und 19 neuer Barcode-, Suchbegriffs- und Trefferprüfungen. Der heruntergeladene Stand bestand die Einzeltests erneut.

Zusätzlich bestanden 34 Chromium- und 33 WebKit-Browserprüfungen mit synthetischen Haushaltsdaten und kontrollierten Serverantworten. Geprüft wurden beide Foto-Wege, automatische Suche, leere/falsche Treffer, Pflichtbestätigung, 100-g/ml-Basis, unbekannte Werte und echte Nullen, Produkt speichern, Stückportionen, Abbruch bei ungespeichertem Produkt, Wechsel der Modi ohne verlorene Korrekturen, verzögerte Antworten nach Schliessen, geteilte Vorlage, getrennte Tagebücher, Neuladen sowie Darstellung bei 320, 390 und 1440 Pixeln. Keine JavaScript-Laufzeitfehler und keine unerwarteten externen Anfragen.

Die zusätzliche Chromium-Prüfung verwendete die tatsächlich gebündelte lokale Texterkennung auf einem synthetischen PNG mit Packungsbeschriftung (ohne Erkennungs-Mock). Die übrigen OCR-/Barcode-Ergebnisse wurden für reproduzierbare Grenzfälle kontrolliert vorgegeben. Mobile Ergebnisansichten wurden visuell geprüft. Dies ist kein neuer Hardwarekamera- oder Installationstest auf einem physischen Android-Handy beziehungsweise iPhone und keine Garantie für beliebige echte Verpackungsfotos.

## Update laden

Den bisherigen Link oder das vorhandene App-Symbol öffnen, bei Bedarf «App aktualisieren» wählen und Version 1.9.0 kontrollieren. Offene Eingaben vorher speichern beziehungsweise den Scanner schliessen. Keine Neuinstallation oder Löschung von Browserdaten notwendig.
