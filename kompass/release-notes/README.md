# Release Notes · Nährstoff-Kompass

Das benutzerfreundliche Archiv beginnt auf Wunsch einmalig mit **v1.9.0**. Frühere technische UPDATE-Dateien bleiben unverändert, werden hier aber nicht nachgetragen. Neue Releases werden ab jetzt ergänzt.

- [v1.10.0 – Cups rein. Rezept fertig.](v1.10.0.md)
- [v1.9.1 – Kein Update mehr verpassen.](v1.9.1.md)
- [v1.9.0 – Ein Foto. Zwei Möglichkeiten.](v1.9.0.md)

## Künftige Veröffentlichung

`releases.json` ist die einzige redaktionelle Quelle. Für jede neue App-Version einen vollständigen Eintrag hinzufügen, bestehende Einträge erhalten und `python3 kompass/release-notes/build.py` ausführen. Das erzeugt `catalog.js`, den sichtbaren Ordner `index.html` und die lesbaren Markdown-Dateien. Die App bindet den Katalog versionsgebunden ein; Offline-Dateien in `sw.js` beim Ergänzen mitführen. `build.py --check` prüft, ob die generierten Dateien aktuell sind. Die Release-Prüfung verlangt einen passenden Eintrag zur veröffentlichten `version.json`.

Automatisch angezeigt werden alle Releases neuer als `profile.releaseNotesSeen` bis einschliesslich zur geladenen App-Version, numerisch sortiert. Ohne gespeicherten Lesestand beginnt die Anzeige bei v1.9. Erst eine ausdrückliche Bestätigung schreibt den Stand ins Personenprofil. Die bestehende verschlüsselte Sicherung und Synchronisierung werden genutzt. Ein höherer bestätigter Stand hat beim Abgleich Vorrang, damit parallele Geräte und ein Rollback keine Rückstufung verursachen. Die automatische Anzeige wartet bei offenen Formularen/Scannern; «Später» verschiebt bis zum nächsten App-Start. Archivbesuche markieren nichts automatisch als gelesen.
