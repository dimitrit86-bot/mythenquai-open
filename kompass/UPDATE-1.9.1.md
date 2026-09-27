# Nährstoff-Kompass 1.9.1 · Neuerungen pro Profil und Release-Archiv

## Beim ersten Öffnen nach einem Update

Nach Anmeldung und Auswahl eines Personenprofils erscheint «Das ist neu für dich». Die Anzeige enthält alle dokumentierten Versionen nach dem zuletzt bestätigten Stand bis zur geladenen App-Version. Übersprungene Updates werden gesammelt angezeigt, neueste zuerst. Für Patricia und Dimitri werden getrennte Lesestände gespeichert.

Zum Start werden einmalig die Neuerungen von **v1.9.0** aufgenommen. Zusätzlich enthält das Archiv die nun veröffentlichte Erweiterung **v1.9.1**. Frühere Versionen werden nicht rückwirkend in dieses Archiv übernommen; die vorhandenen technischen UPDATE-Dateien bleiben unverändert bestehen. Ab jetzt ist jede neue Version im Release-Katalog zu dokumentieren.

«Gelesen – weiter» bestätigt die angezeigten Updates für das aktive Profil. Die bestehende verschlüsselte Sicherung und Synchronisierung überträgt diesen Stand nach erfolgreichem Abgleich auch auf andere Geräte. Es werden keine Körperdaten, Ziele, Lebensmittel oder Tagebucheinträge geändert. Ein anderer Browser mit noch nicht synchronisiertem Stand kann den Hinweis nochmals zeigen.

«Später», das Schliesskreuz oder Escape markiert nichts als gelesen. Innerhalb derselben geöffneten App wird das Profil nicht wiederholt unterbrochen; beim nächsten App-Start kehrt die Erinnerung zurück. Die automatische Anzeige wartet bei offenen Dialogen, Scanner oder ungespeicherten Eingaben. Ein Speicherfehler bleibt sichtbar und bestätigt keine erfolgreich gespeicherten Daten.

## Dauerhaft nachlesen

Der Button **«Neuerungen»** oben in der App und **«Neuerungen & Release Notes»** im Profil öffnen das Archiv. Die Zahl am Button zeigt unbestätigte Updates. Jede Version enthält eine Zusammenfassung, die neuen Funktionen, Bedienhinweise und wichtige Grenzen. Ein Archivbesuch allein verändert den Lesestand nicht.

Der neue Ordner **kompass/release-notes/** enthält eine übersichtliche Webseite und pro Version eine Markdown-Textdatei. Stabile Archiv-Adresse: https://dimitrit86-bot.github.io/mythenquai-open/kompass/release-notes/ . Die öffentlichen Release Notes enthalten keine persönlichen Profildaten.

## Künftige Releases

`release-notes/releases.json` ist die redaktionelle Quelle. `python3 kompass/release-notes/build.py` erzeugt daraus die Archivseite, den App-Katalog und die einzelnen Notizen. Eine zusätzliche GitHub-Prüfung mit Leserechten kontrolliert bei künftigen Änderungen, ob zur aktuellen App-Version Release Notes existieren, generierte Dateien aktuell sind und bestehende Versionseinträge erhalten bleiben. Sie erstellt keine erfundenen Änderungsbeschreibungen und ersetzt keine redaktionelle Prüfung.

Der Versionsvergleich ist numerisch (1.10 liegt nach 1.9). Beim Abgleich zweier Geräte hat der höhere bestätigte Stand Vorrang. Ein alter App-Stand oder eine parallele Bestätigung setzt den Lesestand nicht zurück; echte Konflikte in persönlichen Daten bleiben weiterhin ausdrücklich zu prüfen.

## Prüfungen und Grenzen

Erfolgreicher Prüfworkflow **36321328319**, geprüfter Quellcommit **8ed713810256199bde59996e7150452c520fc217**, Artefakt **10931638857**. Alle **323 Einzeltests** bestanden, davon 29 neue Release-Tests und 294 bestehende Tests. Die Einzeltests und die Archiv-Erzeugungsprüfung wurden auch mit dem heruntergeladenen Artefakt erneut ausgeführt.

Je **38 Browserprüfungen in Chromium und WebKit** bestanden: getrennte Profile, geräteübergreifender Lesestand, spätere Erinnerung, gesammelte übersprungene Releases, Fehler beim Speichern, sichere Zusammenführung, Vorschau ohne Änderungen, echte Textdatei-Downloads und mobile/Desktop-Ansichten. Keine JavaScript-Laufzeitfehler und keine unerwarteten externen Anfragen. Mobile Dialog- und Archivansichten wurden visuell geprüft.

Die Cache-Prüfung nutzte in Chromium echte Offline-Emulation. Da Playwrights Service-Worker-Instrumentierung nur Chromium unterstützt und WebKit bei set_offline/reload einen internen Fehler lieferte, wurde dort der unveränderte Service Worker gegen einen tatsächlich mit HTTP 503 antwortenden Testserver geprüft. Beide Prüfungen bestätigten den getrennten Cache für Haupt-App und Release-Archiv. Ein physischer iPhone-/Android-Test und ein uneingeschränkt bestandener WebKit-Offline-Test werden nicht behauptet.

Alle Browserabläufe verwendeten synthetische Haushaltsprofile und kontrollierte API-Antworten. Echte private Daten und Serverfunktionen wurden nicht verändert. Die bestehende Foto-, Report-, PDF-, Portions-, Such- und Nährwertlogik bleibt unverändert. Die Veröffentlichung betrifft kompass/ und den zusätzlichen Release-Prüfworkflow; andere Webseiten im Repository bleiben unverändert.

## Update laden

Bisherigen Link beziehungsweise das vorhandene App-Symbol öffnen und bei Bedarf «App aktualisieren» drücken. Die Kopfzeile lautet **1.9.1**. Offene Eingaben vor dem Neuladen speichern. Keine Neuinstallation und keine Löschung von Browserdaten erforderlich.
