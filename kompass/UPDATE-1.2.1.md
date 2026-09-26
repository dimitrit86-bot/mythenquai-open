# Protein-Tagesbedarf im Überblick · Version 1.2.1

Der Proteinbereich oben in der Tagesübersicht zeigt jetzt die erfasste Menge und den **Tagesbedarf in g pro Tag** deutlich getrennt. Der Bedarf bleibt auch an Tagen ohne Einträge sichtbar. Bei vollständig bekannten Proteinangaben wird zusätzlich die verbleibende Menge bis zum Tagesziel angezeigt. Fehlende Angaben bleiben unbekannt; eine bekannte Teilmenge wird nicht als vollständige Tagesbilanz ausgegeben.

Der angezeigte Wert stammt unverändert aus dem aktiven Referenzprofil beziehungsweise aus dessen eigenem Proteinziel. Ein Profilwechsel oder gespeicherte Profiländerungen aktualisieren die Anzeige. Bei fehlendem oder nicht automatisch berechenbarem Ziel steht ausdrücklich «Noch nicht festgelegt» mit einem direkten Weg ins Profil. Es werden keine neuen Referenzwerte oder persönlichen Ziele erfunden.

Die Ergänzung liest ausschliesslich den vorhandenen App-Zustand. Lebensmittel, Rezepte, Tagebucheinträge, gespeicherte Profile, Passwortanmeldung und Referenzberechnungen werden nicht verändert. Die normale Adresse und das installierte App-Symbol bleiben erhalten. Bei noch zwischengespeicherter Oberfläche steht der bestehende Button «App aktualisieren» zur Verfügung. Die statische Offline-Dateiliste und die Versionsprüfung wurden auf 1.2.1 aktualisiert.

## Prüfungen vor Veröffentlichung

- 48 bestehende Rechen-, Daten- und Rezepttests bestanden.
- 15 zusätzliche Tests der Proteinanzeige bestanden, einschliesslich eigener Ziele, Altersgrenze, leerem Tagebuch, unbekannten Werten und vorhandenen Ausschlüssen automatischer Ziele.
- 20 lokale Chromium-DOM-Prüfungen bestanden: Anzeige ohne Einträge, Profilwechsel, gespeicherte Profiländerung, Datumswechsel, Zielüberschreitung, Datenlücken, richtige Nullwerte, unveränderter App-Zustand, Katalogfunktion sowie 320-Pixel- und Desktop-Layout ohne horizontales Überlaufen.

Browserprüfungen verwendeten den aktuellen Quellcode mit einem synthetischen lokalen Haushalts-/Speicheradapter; keine echten privaten Serverdaten wurden gelesen oder geschrieben. Keine Behauptung eines neuen Praxistests auf echten Android-/iPhone-Geräten. Der Tagesbedarf ist weiterhin eine Referenz bzw. ein selbst eingetragenes Ziel, keine Messung des individuellen Bedarfs.
