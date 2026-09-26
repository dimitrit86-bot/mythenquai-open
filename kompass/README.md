# Nährstoff-Kompass · private Web-App 1.0.0

Eine mobile Ernährungstagebuch-Web-App mit eigenem Rezeptrechner, Schweizer Lebensmitteldaten, Packungserkennung und getrennten Haushaltsprofilen.

## Benutzen

Die veröffentlichte HTTPS-Adresse öffnen. Zur Ersteinrichtung ist der separat übermittelte private Aktivierungslink nötig. Dort das gewünschte gemeinsame Passwort zweimal eingeben und die vorgeschlagenen Profilnamen bestätigen. Danach ist der Aktivierungslink verbraucht. Niemand kann allein mit dem normalen Seitenlink Profile oder Einträge abrufen.

Android: Chrome-Menü → App installieren / Zum Startbildschirm hinzufügen.
iPhone: Safari → Teilen → Zum Home-Bildschirm → als Web-App öffnen, sofern angeboten.

Nach der Anmeldung ein Profil wählen. Weitere Profile, Passwortänderung und Haushalts-Sicherung stehen im Profilmenü. Das gemeinsame Passwort gewährt Zugriff auf **alle** Haushaltsprofile. Diese sind getrennte Tagebücher, keine gegeneinander abgeschotteten Benutzerkonten. Persönliche Körperdaten werden nicht vorbefüllt.

## Funktionen

- 1'246 Lebensmittel aus der offiziellen Schweizer Nährwertdatenbank, Version 7.1. Quellen und unbekannte Werte bleiben erkennbar.
- Mengen in g/kg/ml/dl/l; keine stillschweigende Gleichsetzung von Gramm und Millilitern.
- Eigene Produkte, Favoriten, kürzlich verwendete Lebensmittel, Tagesprotokolle und 7-/30-Tage-Auswertung.
- Eigene Gerichte aus Zutaten, Teilportionen nach fertigem Gewicht oder Portionszahl, Bearbeitung und Varianten. Frühere Tagebucheinträge enthalten unveränderliche Nährwert-Snapshots.
- Packungstabelle fotografieren oder als Text einfügen; erkannte Werte prüfen, korrigieren und speichern. Fotos werden nicht hochgeladen. Erkennung lokal mit Tesseract.js. Unscharfe Bilder, Spalten und Einheiten können falsch erkannt werden. Nicht vorhandene Vitaminangaben werden nicht erfunden.
- Barcode per Kamera oder Tastatur; geschützte serverseitige Suche bei Open Food Facts. Community-Daten vor Übernahme mit der Packung vergleichen.
- Geschlechts-/altersbezogene DGE/ÖGE-Referenzen, bei Protein auch passendes Berechnungsgewicht. Keine Diagnose und keine Messung von Blutwerten. Individuelle Sonderfälle benötigen fachlich abgestimmte Ziele.
- Verschlüsselte lokale Zwischenspeicherung, serverseitige Synchronisierung mit Versionsprüfung, JSON-Sicherung und Wiederherstellung, CSV-Export.

## Datenschutz und Betriebsgrenzen

Die **App-Oberfläche und der allgemeine Lebensmittelbestand sind öffentlich** auf GitHub Pages. Persönliche Profile und Tagebücher sind nicht im Repository. Sie liegen im bestehenden Supabase-Projekt in getrennten, standardmässig gesperrten Tabellen. Nur der authentifizierende Serverdienst darf sie lesen und schreiben. Das Passwort wird als bcrypt-Hash gespeichert; Sitzungstoken werden serverseitig gehasht. Wiederholte falsche Passwörter führen zu einer zeitweisen Sperre. Eine kurze PIN ist trotzdem deutlich schwächer als ein langes Passwort.

Die Serverdaten sind nicht Ende-zu-Ende-verschlüsselt: der Projektinhaber und der zuständige Backenddienst besitzen technisch Zugriff. Lokale Zwischenstände sind mit AES-GCM verschlüsselt; der Schlüssel wird erst nach erfolgreicher Anmeldung geliefert. Bei aktivierter Option «angemeldet bleiben» liegt auch die Sitzung auf dem Gerät. Deshalb diese Option nur auf einem eigenen geschützten Gerät verwenden. Abmelden löscht Sitzung und aktuellen lokalen Cache. Browserdatenlöschung kann ungesendete Änderungen vernichten; regelmässig Sicherungen exportieren.

Erste Anmeldung, Profilwechsel, Produktabfragen und Abgleich brauchen Internet. Das bereits geöffnete Profil funktioniert bei kurzem Verbindungsabbruch weiter; Änderungen bleiben als noch nicht synchronisiert markiert. Es werden nie private API-Antworten vom Service Worker gecacht. Fotofunktionen laden ihre Erkennungsdateien bei der ersten Verwendung. Kamera, Installation und Speicherverhalten können je nach Browser/Handy variieren.

Bei einem Versionskonflikt bleibt die lokale Fassung erhalten. Diese zuerst sichern, dann die Serverfassung ausdrücklich laden; keine automatische, verlustbehaftete Zusammenführung.

Die Nutzung erfolgt im bestehenden GitHub-/Supabase-Konto und ist dessen verfügbaren Kontingenten und Tarifen unterworfen. Es wurde kein neuer bezahlter Plan bestellt. Keine Werbung oder externen Analytics.

## Daten und Drittsoftware

- BLV: https://naehrwertdaten.ch/de/downloads/ (Version 7.1; exakte Quelldatei per SHA-256 geprüft).
- Referenztabellen: https://www.dge.de/wissenschaft/referenzwerte/ (Einzelquellen und Vergleichsbedingungen in der App).
- Markenprodukte: https://world.openfoodfacts.org/ – ODbL; Daten sind nicht zwingend vollständig oder aktuell. Das Backend sendet nur den abgefragten Barcode, nicht Profil oder Tagebuch.
- Tesseract.js 6.0.1, Tesseract.js-core 6.0.0, Sprachmodelle Deutsch/Englisch, ZXing Browser 0.1.5. Versions- und Integritätsdaten unter `vendor/vendor-lock.json`, Lizenzen unter `vendor/licenses/`.

## Technik und Prüfungen

Vanilla JavaScript, statische PWA, app-eigener Service-Worker-Scope. Kein Replit. Der Build verändert nur `kompass/` und seine Builddateien, nicht die bestehenden Tennis-Seiten.

`kompass-src/build_data.py` importiert den offiziellen Bestand ohne Ergänzung erfundener Werte und prüft die verwendeten npm-Pakete gegen ihre Distributions-Integrität. `node kompass-src/checks.js` führt Rechen-, Parser- und Kryptografieprüfungen aus. Lokale UI-Tests haben gesonderte Testadapter und verwenden ausschliesslich synthetische Profile. Diese Tests ersetzen keine reale Prüfung der Kamera und Installation auf einem physischen Android-Gerät oder iPhone.
