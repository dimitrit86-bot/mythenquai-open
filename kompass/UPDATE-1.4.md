# Nährstoff-Kompass 1.4.0

## Produktname, Barcode und Link
Unter Erfassen und bei der Zutatensuche gibt es «Nährwerte finden · Name / Barcode / Link». Zuerst werden eigene und gemeinsame Produkte, Basisdaten sowie der Händlerkatalog durchsucht. «Online ergänzen» fragt zusätzlich Open Food Facts ab. Online-Abfragen werden nicht bei jedem Tastendruck gesendet. Neue Werte erscheinen zuerst im bearbeitbaren Produktformular; die passende 100-g-/100-ml-Basis und Packung müssen bestätigt werden. Erst Speichern übernimmt ein Produkt in den privaten Haushalt. Ein Import bucht noch keine gegessene Menge.

Direkte Links werden derzeit für Coop und Open Food Facts verarbeitet. Kein Versprechen, jede beliebige Händlerseite automatisch auslesen zu können: Ein Händler kann Zugriffe ablehnen, Seiten können mehrere oder unklare Spalten enthalten. Dann bleiben Name, Barcode, lokales Foto und eingefügter Nährwerttext als Alternativen. Quellen und unbekannte Werte bleiben erkennbar.

**Coop-Grenze:** Der echte automatische Abruf der genannten Redefine-Coop-Seite wurde am 26.09.2026 von Coop mit HTTP 403 abgewiesen. Für exakt Artikel 7451865 ist deshalb der separat geprüfte öffentliche Datenstand vom 26.09.2026 verfügbar, klar als «nicht live» beschriftet. Pro 100 g: 188 kcal, 790 kJ, 26 g Protein, 6.6 g Fett, 0.8 g gesättigtes Fett, 4 g Kohlenhydrate, 1.9 g Zucker, 4.5 g Ballaststoffe, 0.88 g Salz und 2.5 µg B12. Keine Übertragung dieser Werte auf andere Produkte. Quelle: https://www.coop.ch/de/lebensmittel/fleisch-fisch/the-veggie-chef/steaks-filets/redefine-vegane-alternative-zu-flank-steak/p/7451865

Online-Datenservice: separat, nur lesend, mit serverseitiger Prüfung der bestehenden Haushaltssitzung. Keine Tagebücher, Körperdaten, Fotos oder Passwörter an Lebensmittelanbieter. Kein Browser-Schlüssel mit Serverrechten. Ausschliesslich erlaubte HTTPS-Hosts und geprüfte Weiterleitungen; Grössen-, Zeit- und Abfragelimits. Open Food Facts: ODbL, Community-Daten ohne Vollständigkeitsgarantie.

## Foto-Portionskorrektur
«Diese Werte gelten für …» ist editierbar, beispielsweise 30 g oder 250 ml. Die Vorschau zeigt Ausgangswert und Ergebnis pro 100 g/ml nebeneinander. Korrekturen rechnen immer aus den ursprünglichen Werten, nicht erneut aus bereits skalierten Resultaten. Einzelwerte und Wertespalte sind korrigierbar; die Kontrollbestätigung wird nach Änderungen zurückgesetzt. Unbekannt ist nicht null. Gramm und Milliliter werden nicht stillschweigend ineinander umgerechnet. Die tatsächlich gegessene Menge folgt erst im Tagebuch.

## Spanischer Proteinziel-Screen
Bei einem erfolgreichen Speichern, durch das die vollständig bekannten Proteinmengen des heutigen Tages das unveränderte aktive Ziel erreichen, erscheint «¡La concha de la lora! ¡Felicitaciones!». Dazu ein kurzer Konfettieffekt, die erfasste Menge und der Button «¡Vamos!» zum Schliessen. Ohne Ton; reduzierte Bewegung wird berücksichtigt. Einmal pro Datum und Profil auf dem jeweiligen Gerät, nicht bei jedem weiteren Eintrag oder Neuladen. Änderungen am Ziel allein und alte Tage lösen den Screen nicht aus. Persönliche Ziele werden nicht verändert. Auch während offener Formulare wird kein Erfolgsscreen darübergelegt.

## Unverändert
Die normale App-Adresse und installierten App-Symbole bleiben verwendbar. Keine Neuinstallation und keine Browserdatenlöschung. Standardprofile, gemeinsame Produkte/Gerichte, verschlüsselte Speicherung, Abgleich und historische Nährwertkopien bleiben erhalten. Ein physischer Android-/iPhone-Kameratest wird nicht behauptet.

## Tests
Automatisierte Prüfer liegen unter tests/. Browserabläufe verwenden ausschliesslich synthetische private Profile. Der jeweilige tatsächliche Prüflauf und seine Resultate werden im Veröffentlichungsbericht angegeben, nicht aus der Existenz eines Tests abgeleitet.
