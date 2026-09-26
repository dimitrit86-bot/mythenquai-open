# Nährstoff-Kompass 1.4.0 · Produktsuche, Foto-Portionen und Proteinziel

Die feste App-Adresse bleibt unverändert. Neue Oberfläche: Version 1.4.0. Bestehende Profile, Passwortanmeldung, Tagebücher, gemeinsame Vorlagen und Referenzberechnungen bleiben erhalten. Das Update enthält keine Rücksetzung oder Migration persönlicher Daten.

## Produktname, Barcode oder Coop-Link

Unter Erfassen steht jetzt «Produkt automatisch finden». Das Eingabefeld akzeptiert Namen wie Redefine Flank Steak, einen Barcode oder einen deutschen HTTPS-Produktlink von Coop. Zuerst werden vorhandene eigene, gemeinsame und hinterlegte Produkte durchsucht. Über «Online nach Namen suchen» werden Ergebnisse aus Open Food Facts ergänzt. Externe Anfragen erfolgen nur nach Betätigung des Buttons, nicht beim Tippen.

Treffer enthalten Produktname, Quelle, Nährwertvorschau und soweit vorhanden Packungsgrösse. Externe Angaben gelangen zunächst in den bearbeitbaren Produkteditor. Die passende Variante und Bezugsmenge müssen bestätigt werden. Erst «Produkt speichern» übernimmt die Vorlage in das aktive Profil; nach dessen Synchronisierung ist sie wie bisher im privaten Haushaltskatalog verfügbar. Gegessene Mengen bleiben getrennte Tagebucheinträge. Vorhandene Vorlagen werden anhand von Kennung oder Quellenadresse erkannt.

### Tatsächliche Grenze des Coop-Imports

Coop blockierte beim überprüften automatischen Serverabruf die Produktseite mit HTTP 403. Ein funktionierender Live-Abruf beliebiger Coop-Seiten wird deshalb ausdrücklich nicht behauptet. Der Import versucht die streng geprüfte Produktadresse; bei nicht eindeutig auswertbarer oder gesperrter Seite zeigt die App eine klare Meldung und bietet die aus dem Link abgeleitete Namenssuche an. Deren Alternativtreffer sind keine vermeintlichen Coop-Werte.

Für den vom Nutzer genannten Artikel 7451865 (Redefine vegane Alternative zu Flank Steak, 200 g) ist zusätzlich die anhand der veröffentlichten Coop-Seite geprüfte Deklaration vom 26.09.2026 hinterlegt. Sie wird beim blockierten Abruf ausdrücklich als gespeicherter Quellenstand, nicht als aktueller Live-Abruf angezeigt. Werte pro 100 g: 188 kcal, 790 kJ, 26 g Protein, 6.6 g Fett, 0.8 g gesättigte Fettsäuren, 4 g Kohlenhydrate, 1.9 g Zucker, 4.5 g Ballaststoffe, 0.88 g Salz, 2.5 µg Vitamin B12. Nicht deklarierte Werte bleiben unbekannt. Die genaue Quellenadresse steht im Datensatz und im Editor.

Andere Händlerlinks sind in diesem Release nicht als direkte Seitenimporte unterstützt. Dafür bleiben Namenssuche, Barcode, Packungsfoto und kopierter Nährwerttext verfügbar. Die Open-Food-Facts-Suche wurde separat gegen den öffentlichen Dienst geprüft und lieferte beim Beispiel Redefine vier Varianten. Community-Daten können unvollständig oder veraltet sein; die tatsächliche Packung ist zu vergleichen.

## Fotoangaben auf 100 g oder 100 ml umrechnen

Nach der Erkennung lässt sich einstellen: «Diese Werte gelten für …», zum Beispiel 30 g. Die App zeigt editierbare Ausgangswerte und daneben deren normierte Werte. Berechnung: Ausgangswert × 100 ÷ Bezugsmenge. Auch 250 ml → 100 ml ist möglich; Gewicht und Volumen werden nicht gleichgesetzt.

Eine erkannte Portionsüberschrift kann als Vorschlag dienen. Bei mehreren Spalten lässt sich die erste oder letzte Wertespalte auswählen und die dazugehörige Menge korrigieren. Jede Änderung rechnet neu aus den Ausgangswerten, nicht erneut aus bereits umgerechneten Ergebnissen. Bestätigungen werden bei Änderungen zurückgesetzt. Einzeln falsch erkannte Zahlen sind editierbar. Unbekannte Werte bleiben unbekannt, ausdrücklich deklarierte Nullen bleiben Null; Grenzwertangaben werden nicht als exakte Werte ausgegeben.

Die Bezugsmenge der Nährwerttabelle ist nicht die gegessene Menge. Nach dem Speichern stehen die Produktwerte pro 100 g/ml bereit. Die konsumierte Portion wird später im Tagebuch eingegeben. Fotos werden weiterhin auf dem Gerät verarbeitet und nicht hochgeladen.

## Spanischer Glückwunschbildschirm

Sobald das aktive Profil laut seinen vollständig bekannten Proteinangaben das aktuelle Tagesziel erreicht und die heutige Tagesübersicht sichtbar ist, erscheint ein Glückwunschdialog mit kurzer Konfetti-Animation:

**¡La concha de la lora! ¡Felicitaciones!**

Darunter stehen der Profilname und die erfasste Menge im Verhältnis zum Ziel. Mit «¡Vamos! Volver al día» lässt sich der Dialog schliessen. Er erscheint höchstens einmal pro Profil und Kalendertag auf diesem Gerät/Browser. Ein anderes Gerät hat eine eigene Anzeigemarkierung. Keine erneute Anzeige bei normalem Neuladen oder Navigation. Bei unbekanntem Ziel oder fehlenden Proteinangaben wird keine Zielerreichung behauptet. Offene Eingabeformulare werden nicht überdeckt; die Animation berücksichtigt die Einstellung für reduzierte Bewegung.

## Schutz und Prüfungen

Der zusätzliche Produktsuchdienst validiert dieselbe bestehende Sitzung serverseitig. Er liest nur die Sitzungsgültigkeit, nicht Körperdaten oder Tagebücher. Er schreibt keine Profile. Nach aussen gehen die eingegebenen Suchwörter oder die bereinigte öffentliche Produktadresse, keine privaten Tageswerte. Linkimporte sind auf geprüfte Coop-Adressen beschränkt; interne Adressen und nicht zugelassene Weiterleitungen werden abgelehnt. Tracking-Parameter werden entfernt. Öffentliche Ergebnisse werden zwischengespeichert und Suchanfragen begrenzt. Open Food Facts: ODbL 1.0; Quellenhinweis bei den Ergebnissen.

Erfolgreicher Prüfworkflow: 36259965889. Verifizierter Quellcommit: a4cf216d0826096e27117e066f5090791fa50e11. Der heruntergeladene Quellstand wurde mit dem vorbereiteten Update byteweise abgeglichen.

126 Einzelprüfungen bestanden: Kern-/Rezeptberechnungen 48, Proteinübersicht 15, Synchronisierung 15, Portionsumrechnung 26, Produktimport/Zielerkennung 22. Zusätzlich bestanden jeweils 27 echte Browserabläufe in Chromium und WebKit mit synthetischen Haushaltsprofilen und kontrollierten Netzwerkantworten. Getestet wurden unter anderem Foto-Textreview, Mengenänderung, Speicherung, Link-Snapshot-Fallback, Namenssuche, geteilte Produkte und Gerichte, getrennte Tagesbilanzen, Glückwunsch je Profil und Tag, Neuladen sowie 320-Pixel- und Desktop-Ansicht. Keine JavaScript-Laufzeitfehler.

Drei zusätzliche Anfragen gegen den tatsächlich bereitgestellten Produktsuchdienst bestätigten die erwartete Abweisung ohne Sitzung, mit ungültiger Sitzung und fremder Herkunft (401/401/403). Dafür wurden keine echten Haushaltszugangsdaten verwendet. Die automatisierten Browserläufe sind kein neuer Kameratest und keine Installation auf einem physischen Android- oder iPhone-Gerät.

Alle produktiven Repository-Änderungen dieses Releases liegen unter kompass/. Die Tennisseiten bleiben unverändert. Zum Laden bei Bedarf «App aktualisieren» verwenden. Keine Browserdaten löschen und keine Neuinstallation vornehmen.
