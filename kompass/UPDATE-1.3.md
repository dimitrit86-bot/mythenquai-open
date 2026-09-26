# Nährstoff-Kompass 1.3.0 · Speichern und gemeinsamer Haushaltskatalog

Veröffentlicht am 26.09.2026 unter derselben App-Adresse. Das Passwort, die bestehenden Profile, Einträge, Referenzwerte und Lebensmittelbestände werden nicht zurückgesetzt. Die Veröffentlichung ersetzt ausschliesslich Dateien unter kompass/; andere Seiten des Repositories bleiben unverändert.

## Gemeinsame Produkte und Gerichte

Eigene Produkte und gespeicherte Rezepte aller Haushaltsprofile erscheinen nun im gemeinsamen Katalog. Ein bereits gespeichertes Produkt von Patricia ist nach erfolgreicher Synchronisierung und Laden des Katalogs auch für Dimitri verfügbar, ohne erneutes Abtippen oder Fotografieren. Dies gilt ebenfalls für vorhandene Vorlagen, nicht nur neu erstellte. In der Suche steht der Filter «Unser Haushalt» zur Verfügung. Die Herkunft wird mit dem Profilnamen gekennzeichnet.

Gegessene Mengen, Tagebucheinträge, persönliche Körperdaten und Ziele bleiben im jeweiligen Profil. Ein gemeinsam verfügbares Produkt erzeugt erst dann einen persönlichen Tagebucheintrag, wenn das aktive Profil eine Menge erfasst. Gemeinsame Produkte sind auch als Rezeptzutaten nutzbar; gemeinsame Gerichte können direkt portionsweise erfasst werden.

Beim Bearbeiten einer Vorlage aus einem anderen Profil entsteht eine eigene Variante. Das Original wird nicht stillschweigend geändert. Bereits protokollierte Nährwerte behalten ihre gespeicherten Kopien, auch wenn eine Rezeptvorlage später geändert wird.

Der Katalog wird beim Profilwechsel, nach Synchronisierung, bei Rückkehr in die App sowie bei Navigation zu Suche/Gerichten nachgeladen. «Katalog aktualisieren» erlaubt einen direkten Abruf. Für neue geräteübergreifende Vorlagen ist eine Internetverbindung nötig. Noch nicht synchronisierte Angaben eines anderen Geräts sind nicht abrufbar. Ein bereits geladener gemeinsamer Katalog bleibt während derselben Sitzung bei kurzem Verbindungsausfall im Arbeitsspeicher; bei einem vollständig neuen Offline-Start ist er nicht garantiert vorhanden.

## Speicherfehler und Abgleich

Die frühere Oberfläche meldete bei allen Speicherfehlern pauschal einen vollen Browserspeicher. Dazu zählten auch von der Abgleichlogik ausgelöste Konflikte. Die Meldung allein bewies deshalb keinen vollen Gerätespeicher. Der genaue Auslöser auf dem fotografierten iPhone konnte nicht unmittelbar auf dem Gerät gemessen werden.

Speichervorgänge werden jetzt nacheinander ausgeführt und tatsächlich abgewartet. Ungesendete Änderungen werden verschlüsselt gesichert, vorrangig in IndexedDB mit dem bisherigen lokalen Speicher als Rückfalloption. Ist die lokale Sicherung nicht verfügbar, wird bei bestehender Verbindung eine bestätigte Speicherung auf dem Server versucht. Sind beide Wege nicht verfügbar, erscheint eine ausdrückliche Warnung statt einer Erfolgsmeldung; offene Eingaben sollen dann nicht geschlossen werden.

Bei verschiedenen Versionen desselben Profils werden unabhängige Ergänzungen zusammengeführt. Widersprüchliche Änderungen an denselben Daten erfordern eine Auswahl unter «Profile & Sync». Neue Eingaben bleiben während eines solchen Konflikts weiterhin lokal speicherbar, sofern der lokale Speicher funktioniert. Beide Fassungen können vor einer Entscheidung gesichert werden. Bestehende lokale, noch nicht gesendete Daten werden bei der Wiederanmeldung berücksichtigt. Es wird keine automatische Löschung von Browserdaten verlangt.

## Schutz des gemeinsamen Katalogs

Ein neuer, rein lesender Server-Endpunkt validiert die bestehende Sitzung und liefert nur Produkt-/Rezeptvorlagen sowie die dafür benötigten Profilkennungen und Namen. Er liest keine Tagebücher, persönlichen Referenzprofile oder Körperdaten für diesen Katalogabruf aus. Der gemeinsame Zugang ist weiterhin ein Haushaltszugang: Wer dessen Passwort kennt, kann die Haushaltsprofile öffnen. Persönliche Angaben werden nicht in das öffentliche GitHub-Repository hochgeladen. Bestehende Authentifizierungs-Endpunkte und Datenbanktabellen wurden nicht ersetzt.

## Prüfungen

Erfolgreicher GitHub-Prüflauf: 36256567137. Getesteter Quellstand: 42f086095334bec6347b64e3e49e120237c75e51.

48 bestehende Kern-/Rezepttests, 15 Protein-Anzeigetests und 15 neue Abgleichtests bestanden. Zusätzlich bestanden 24 Chromium-Browserprüfungen mit tatsächlichem Browserspeicher und synthetischem privaten Datenservice. Sie umfassen Produkt- und Rezeptspeicherung, portionsweise Erfassung, Sichtbarkeit zwischen Profilen, getrennte Tagebücher, Varianten, unveränderte historische Nährwerte, zwei Geräte, echte Konflikte, Offline-Wiederherstellung und Server-Speicherung bei simuliertem lokalem Speicherausfall. 320-Pixel- und Desktop-Layout sowie der Händlerkatalog wurden geprüft; keine JavaScript-Laufzeitfehler.

Drei zusätzliche Prüfungen gegen den tatsächlich bereitgestellten Katalog-Endpunkt bestätigten die Abweisung ohne Sitzung, mit ungültiger Sitzung und bei unzulässiger Browserherkunft. Sie verwendeten keine echten Zugangsdaten. Die Browserabläufe schrieben ausschliesslich synthetische Testdaten, nicht die echten Haushaltsprofile. Ein erneuter Praxistest auf einem physischen iPhone oder Android-Handy ist nicht behauptet.

## Update verwenden

Auf beiden Geräten die bestehende App-Adresse öffnen bzw. «App aktualisieren» verwenden. Die Kopfzeile muss Version 1.3.0 zeigen. Eine Neuinstallation oder das Löschen von Browserdaten ist nicht erforderlich. Falls eine alte Version das Anwenden wegen eines Abgleichkonflikts blockiert, noch offene Formulareingaben vorher notieren oder sichern und die normale App-Seite neu öffnen; verschlüsselt gesicherte Änderungen werden beim Start berücksichtigt. Produkte und Gerichte erscheinen nach erfolgreichem Serverabgleich und Laden des gemeinsamen Katalogs auch in anderen Profilen.
