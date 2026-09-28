# Nährstoff-Kompass 1.13.0 · Nährwerte korrigieren und verknüpfte Einträge neu berechnen

Stand: 28.09.2026. Die feste App-Adresse bleibt https://dimitrit86-bot.github.io/mythenquai-open/kompass/ . Dieses Update erweitert den veröffentlichten Stand 1.12.0. Es setzt keine Profile, Passwörter, Vorlagen oder Tagebücher zurück.

## Einmal korrigieren

Unter «Erfassen» das eigene Produkt öffnen und über «Packungswerte bearbeiten» die falschen Angaben korrigieren. Erst «Produkt speichern» übernimmt die Änderung. Zusammen mit dem Produkt werden seine verknüpften Zutatenkopien, gespeicherten Gerichte und Tagebucheinträge neu berechnet – einschliesslich früherer Tage. Im Produktformular wird auf diese rückwirkende Wirkung hingewiesen; eine Meldung nennt die Zahl neu berechneter Einträge und Gerichte.

Beispiel: Ein Produkt hatte fälschlich 100 kcal pro 100 g. Nach Korrektur auf 120 kcal ergeben bereits erfasste 150 g neu 180 statt 150 kcal. Die erfassten 150 g, Datum, Mahlzeit, Kennung und das Vollständigkeitshäkchen bleiben gleich. Entsprechend werden geänderte Protein-, Kohlenhydrat-, Fett-, Vitamin- und Mineralstoffangaben berücksichtigt. Fehlende Werte bleiben unbekannt und echte Nullwerte bleiben Null.

Bereits vor diesem Update vorgenommene Korrekturen erhalten nicht allein durch die Veröffentlichung rückwirkend eine Markierung. Ein betroffenes eigenes Produkt nochmals öffnen und speichern, damit die neue Korrekturfunktion seine verknüpften Einträge abgleicht.

## Mengen und damalige Rezeptzusammensetzung bleiben erhalten

Neue direkte Tagebucheinträge speichern zusätzlich ihre ursprüngliche Gramm-/Millilitermenge. Stückportionen und Cups behalten damit das damals verwendete Gewicht, auch wenn die Vorlage später eine andere Stück- oder Cup-Grösse bekommt. Bei Rezeptbuchungen wird der erfasste Anteil an der damaligen Zutatenzusammensetzung festgehalten.

Eine Nährwertkorrektur ersetzt nicht rückwirkend die Zutatenzusammensetzung eines damals anders gekochten Gerichts. Sie korrigiert die Nährwerte der tatsächlich verknüpften Produktzutaten. Neue Sorten oder geänderte Herstellerrezepturen deshalb als neues Produkt beziehungsweise eigene Variante speichern, statt alte korrekte Angaben als Erfassungsfehler zu überschreiben.

Alte Einträge werden nur neu berechnet, wenn Quelle und damalige Menge eindeutig zugeordnet werden können. Die App verwendet gespeicherte Mengen, ihre eigenen alten Mengenbeschriftungen oder einen anhand aller vorhandenen Nährstoffkopien konsistent bestimmbaren Rezeptanteil. Sind diese Angaben widersprüchlich, nicht rekonstruierbar oder wurde zwischen 100 g und 100 ml gewechselt, bleiben die alten Zahlen erhalten und der Eintrag wird zur Prüfung markiert. Über «Betroffene Einträge prüfen» lässt sich der betreffende Tag oder das Gericht öffnen. Die passende Menge dann neu zuordnen beziehungsweise erneut erfassen.

## Gemeinsame Vorlagen, getrennte Tagebücher

Korrigiert Patricia ein von ihr angelegtes Produkt, wird die Quellenkorrektur zusammen mit ihrer Vorlage synchronisiert. Beim sicheren Nachladen des Haushaltskatalogs übernimmt Dimitris Profil die Korrektur in seine eindeutig damit verknüpften Einträge und Gerichte. Eigene Varianten mit anderer Kennung oder gleich benannte, unabhängig angelegte Produkte werden nicht geändert.

Für die Übernahme auf einem anderen Gerät sind eine erfolgreiche Synchronisierung und ein neuer Katalogabruf erforderlich. Bei offenen Eingaben, laufendem Speichern oder Abgleichkonflikten wartet die automatische Anwendung. Die bestehende verschlüsselte Sicherung, serielle Speicherung und Konfliktbehandlung bleiben zuständig. Ein erneuter Abruf derselben Korrektur skaliert Zahlen nicht ein zweites Mal.

Die Veröffentlichung liest oder verändert keine echten Haushaltsdaten auf dem Server. Neuberechnungen werden erst durch ausdrückliches Speichern einer Produktkorrektur und den anschliessenden App-Abgleich ausgelöst. Öffentliche Händler-/Lebensmitteldatenänderungen allein führen nicht zu rückwirkenden Änderungen.

## Reports und PDF

Tagesübersicht, Verlauf und neue Reports verwenden die neu berechneten Tagebucheinträge. Ein danach exportierter PDF-Report enthält die korrigierten Summen. Eine schon heruntergeladene PDF-Datei verändert sich nicht; bei Bedarf erneut exportieren. Noch nicht automatisch auflösbare Korrekturen werden in der App angezeigt und in den Hinweisen des vollständigen Reports kenntlich gemacht.

## Vorhandene Funktionen bleiben erhalten

Cups, ungefähre Dichte-/Stückreferenzen, kompletter Rezept-Textimport, beide Foto-Wege, Textauslesen, geteilte Vorlagen, Makroziele, Reports/PDF, einmalige Neuerungen pro Profil und die Nachfrage zum Vortag sind weiterhin enthalten. Die neuen Release Notes stehen im bestehenden Archiv ab v1.9. Nur kompass/-Dateien werden veröffentlicht; andere Repository-Seiten und Serverfunktionen bleiben unverändert.

## Tatsächlich ausgeführte Prüfungen

Erfolgreicher GitHub-Prüflauf: 36437288151. Geprüfter Quellcommit: eb8f2cbc885e932708a93908e999df3a186633d5. Artefakt: 10975784510. Alle 16 vorbereiteten Anwendungs-/Testdateien stimmen byteweise mit dem heruntergeladenen geprüften Artefakt überein.

496 Einzelprüfungen bestanden, einschliesslich 42 neuer Korrekturfälle. Zusätzlich bestanden je 27 Browserprüfungen in Chromium und WebKit mit synthetischen Haushaltsprofilen, kontrollierten API-Antworten und tatsächlichem verschlüsseltem Browserspeicher. Geprüft wurden direkte historische Einträge, Rezeptanteile, gespeicherte Vorlagen, der Abgleich zweier Profile, unveränderte eigene Varianten, offene Formulare, wiederholte Abrufe, Stückgewichte, Neuladen, unvereinbare Bezugsgrössen sowie Ansichten bei 320, 390 und 1440 Pixeln. Keine JavaScript-Laufzeitfehler oder unerwarteten externen Anfragen.

Beide Browser erzeugten über die vorhandene Exportoberfläche einen echten PDF-Testreport mit der erwarteten korrigierten Energiesumme von 290 kcal. Text und Darstellung der exportierten PDF sowie der Prüfhinweise wurden kontrolliert. Die Testprofile und ihre Zielwerte sind künstliche Prüfdaten, keine Empfehlungen oder echten Angaben von Patricia und Dimitri. Ein neuer Hardwarekamera-/Installationstest auf einem physischen Handy wird nicht behauptet.

## Update verwenden

Die App über den bisherigen Link oder das vorhandene Symbol öffnen, offene Eingaben speichern und bei Bedarf «App aktualisieren» wählen. Oben muss Version 1.13.0 stehen. Keine Neuinstallation und keine Löschung von Browserdaten nötig.
