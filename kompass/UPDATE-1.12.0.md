# Nährstoff-Kompass 1.12.0 · Einmalige Neuerungen und Vortag-Check

## Neuerungen nur einmal

Der automatische Hinweis merkt sich jetzt bereits beim tatsächlichen Anzeigen, welche Versionen ein Personenprofil gesehen hat. «Weiter zur App», das Schliesskreuz oder Escape führt deshalb beim nächsten Start nicht mehr zur Wiederholung derselben Neuerungen. Eine gesonderte Lesebestätigung ist nicht mehr erforderlich.

Der angezeigte Versionsstand wird im aktiven Profil über die bestehende geschützte Speicherung gesichert und synchronisiert. Zusätzlich merkt der jeweilige Browser eine kleine Versionsmarkierung pro Profil, damit ein unmittelbares Schliessen oder Neuladen den Hinweis nicht wiederholt. Patricia und Dimitri bleiben unabhängig. Nach erfolgreichem Abgleich gilt der Profilstand auf anderen Geräten ebenfalls; bei parallel oder offline geöffneten, noch nicht synchronisierten Geräten kann eine Anzeige dort nochmals vorkommen. Bei nicht verfügbarem lokalen und serverseitigen Speicher ist eine dauerhafte Markierung nicht garantiert.

Das Archiv unter «Neuerungen» und im Profil bleibt jederzeit manuell erreichbar. Es beginnt unverändert bei v1.9 und enthält auch die Release Notes zu diesem Update. Ein manueller Archivbesuch ändert nicht ungefragt den Anzeigestand. Übersprungene Versionen werden weiterhin gesammelt dargestellt.

## Gestern vollständig protokolliert?

Hat der Vortag mindestens einen Tagebucheintrag, aber noch kein Häkchen «Tag vollständig protokolliert», erscheint eine Nachfrage mit Profilname, Datum und Anzahl vorhandener Einträge:

**Ist gestern vollständig? Hast du für den angezeigten Vortag bereits alles protokolliert?**

- **Ja, alles erfasst:** Setzt das vorhandene Vollständigkeits-Häkchen direkt für genau diesen Vortag und speichert die Antwort. Tagebuch und Auswertungen berücksichtigen danach die Markierung.
- **Nein, Vortag öffnen:** Lässt das Häkchen unverändert und öffnet den betreffenden Tag zum Nachtragen. Die Antwort wird gemerkt, damit die App für denselben Tag nicht bei jedem Start erneut fragt. Nach dem Ergänzen kann das normale Häkchen gesetzt werden.
- **Später, Schliesskreuz oder Escape:** Ändert weder Häkchen noch gespeicherte Antwort. Die Nachfrage bleibt für die aktuelle Sitzung zurückgestellt und kann beim nächsten App-Start wieder erscheinen.

Bereits vollständige Tage und Vortage ohne Einträge lösen keine Nachfrage aus. Es wird nicht automatisch aus erreichten Nährstoffzielen auf Vollständigkeit geschlossen. Die Nachfrage bezieht sich auf den lokalen Kalendertag des Geräts, auch nach Mitternacht sowie bei Monats-, Jahres- und Zeitumstellungsgrenzen.

## Bestehende Daten und sichere Bedienung

Ein «Ja» verändert nur die Tagesmarkierung und die Antwort-Metadaten des aktiven Profils, nicht Lebensmittel, Rezepte, gegessene Mengen oder Nährwerte. Das manuelle Tages-Häkchen bleibt weiterhin nutzbar. Patricia und Dimitri werden getrennt gefragt.

Automatische Hinweise warten bei offenen Formularen, Scanner und anderen Dialogen. Erst Neuerungen, dann gegebenenfalls der Vortag-Check; es erscheinen keine übereinanderliegenden Eingabefenster. Zwischenzeitlich geänderte Einträge verlangen eine erneute Prüfung. Ein Profil- oder Kalendertagwechsel darf keine alte Bestätigung auf einen falschen Tag anwenden.

Bei einem Serverausfall wird die Antwort über die vorhandene verschlüsselte lokale Sicherung aufbewahrt und später synchronisiert, sofern der Browserspeicher verfügbar ist. Schlagen beide Speicherwege fehl, bleibt eine Fehlermeldung sichtbar statt einer falschen Erfolgsmeldung. Die bisherigen Abgleich- und Konfliktregeln bleiben erhalten; die beiden reinen Anzeige-/Antwort-Marker werden monoton zusammengeführt.

Cups, Dichte- und Stückgewichts-Schätzwerte, vollständiger Rezept-Textimport, Fotoerkennung, Ernährungsziele, geteilte Vorlagen sowie Reports und PDF-Export bleiben enthalten. Keine Produktionsprofile, Passwörter, Datenbanktabellen oder Serverfunktionen wurden für diese Veröffentlichung verändert. Die Produktionsänderungen liegen ausschliesslich unter kompass/; andere Webseiten im Repository bleiben unverändert.

## Tatsächlich ausgeführte Prüfungen

Erfolgreicher Prüfworkflow **36397425938**, geprüfter Quellcommit **324fe8c397be9b4c01228c4705cdcbd356c6502e**, heruntergeladenes Artefakt **10959316055**.

Alle **489 Einzelprüfungen** bestanden, darunter 25 neue Tests für Kalendertage, Berechtigung der Nachfrage, Eintragsänderungen und konfliktfreie Antwort-Metadaten. Syntax- und Archiv-Erzeugungsprüfung bestanden ebenfalls. Die Einzeltests und Archivprüfung wurden mit dem heruntergeladenen geprüften Quellstand nochmals ausgeführt.

Je **45 Browserprüfungen in Chromium und WebKit** bestanden. Getestet wurden einmalige Anzeige ohne Bestätigung, Schliessen und Neuladen, getrennte Profile und Geräte, weiterhin erreichbares Archiv, direkte Tagesmarkierung, Auswirkungen auf Vollständigkeits-Auswertungen, Nein/Später, leere und abgeschlossene Vortage, Speicherfehler und Wiederholung, verschlüsselte lokale Sicherung bei Serverausfall, Wiederherstellung und anschliessender Abgleich, geänderte Einträge, Mitternacht und Schutz offener Eingaben. Die Dialoge passen bei 320, 390 und 1440 Pixeln ohne horizontales Überlaufen. Mobile Ansichten wurden visuell geprüft. Die Testberichte enthalten keine JavaScript-Laufzeitfehler oder unerwarteten externen Anfragen.

Die Browserabläufe verwendeten synthetische Haushaltsdaten und kontrollierte API-Antworten, nicht eure realen Profile. Ein neuer Test auf physischen Android- oder iPhone-Geräten und eine echte Anmeldung mit eurem Haushaltspasswort wurden nicht durchgeführt.

## Update laden

Die feste App-Adresse bleibt https://dimitrit86-bot.github.io/mythenquai-open/kompass/ . Bisherigen Link oder App-Symbol öffnen, offene Eingaben speichern und gegebenenfalls «App aktualisieren» drücken. Oben steht **Version 1.12.0**. Keine Neuinstallation und keine Löschung der Browserdaten erforderlich.
