# Speicherreparatur · Version 1.2.2

## Reproduzierter Fehler

Wenn ein Speichervorgang auf dem Server bereits erfolgreich war, die lokale verschlüsselte Sicherung aber noch die alte Versionsnummer und «ausstehend» enthielt, behandelte die App das beim erneuten Öffnen als Konflikt. Weitere Einträge waren blockiert. Die Oberfläche ersetzte den eigentlichen Konfliktfehler irreführend durch «Browserspeicher voll oder nicht verfügbar».

Dies wurde mit dem unveränderten veröffentlichten Quellcode und synthetischen Testdaten im Chromium-DOM reproduziert. Das Foto allein beweist nicht, dass jeder betroffene Browser genau diesen Auslöser hatte.

## Korrektur

Beim Wiederherstellen und bei einer wiederholten Speicheranfrage wird geprüft, ob die vollständigen Daten bereits auf dem Server vorhanden sind. Unterschiedliche Reihenfolgen von JSON-Objektschlüsseln sind dabei bedeutungslos. Identische Inhalte werden als bereits gespeichert erkannt, ohne einen Eintrag erneut anzulegen. Tatsächlich unterschiedliche Inhalte werden nicht automatisch zusammengeführt oder überschrieben.

Speicherfehler behalten ihre tatsächliche Ursache: Synchronisierungskonflikt, abgelaufene Sitzung, verweigerter Speicherzugriff oder echte Speichergrenze werden nicht mehr pauschal als voller Browserspeicher gemeldet. Ein Fehler beim lokalen Zwischenspeichern wird nach einem bestätigten Server-Speichervorgang als lokale Offline-Einschränkung angezeigt, nicht als fehlgeschlagene Serverspeicherung.

Bei echten Konflikten gibt es «Fassungen prüfen & sichern». Die lokale Fassung kann nach ausdrücklicher Bestätigung als zusätzliches Profil gesichert und dort weiterbearbeitet werden. Die ursprüngliche Serverfassung bleibt unverändert. Diese Sicherung erfolgt nur durch Betätigung des Buttons, nicht automatisch. Noch nicht übernommene Formulareingaben sind nicht Teil der gespeicherten Fassung. Der bestehende Export bleibt verfügbar.

Die dynamisch geladene app.js erhält ebenfalls eine Versionskennung, damit ein alter Cache nicht die korrigierte Speicherlogik ersetzt. Die normale Web-App-Adresse, Startbildschirm-Installation, Profileinstellung, Lebensmitteldatenbank und Protein-Tagesübersicht bleiben bestehen.

## Prüfung und Umfang

48 bestehende Rechen-/Datenprüfungen, 15 Proteinanzeige-Prüfungen und 19 zusätzliche Speicherprüfungen bestanden lokal. Hinzu kommen 28 bestandene Chromium-DOM-Prüfungen mit synthetischen API-, Speicher- und Krypto-Adaptern: Fehlerreproduktion, neue Einträge und Gerichte, Neuladen, korrekte Behandlung verlorener Speicherbestätigungen, echte Konflikte, separate Wiederherstellung, fehlgeschlagene lokale Sicherung sowie Mobil-/Desktop-Darstellung. Diese Browserprüfungen sind kein Test der echten iPhone-Installation, der realen Netzwerkverbindung oder der Kryptografie. Die Kryptoimplementierung wurde nicht geändert.

Bei der Diagnose wurden nur vorhandener Anwendungscode, technische Anfragestatus sowie Profilgrössen/Zähler gelesen. Es wurden keine echten Tagebucheinträge, Rezepte oder Profile zu Testzwecken geschrieben oder gelöscht. Backend, Passwort und Referenzberechnungen wurden nicht geändert.

Die veröffentlichte Korrektur muss zunächst vom jeweiligen Gerät geladen werden. Keine Browserdaten löschen und die App nicht deinstallieren. Bei noch ungesendeten Änderungen zuerst eine lokale Dateisicherung erstellen.
