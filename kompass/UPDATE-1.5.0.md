# Nährstoff-Kompass 1.5.0 · Ernährungsziele im Profil

## Direkt im persönlichen Profil auswählen

Unter «Profil» steht oben «Ernährungsziel»: Normal / Gewicht halten, Muskelaufbau, Sportler / ambitioniertes Training und Abnehmen / moderat. Dazu das Aktivitätsniveau für den ganzen Tag einschliesslich Sport auswählen. Gewicht, Grösse, Alter und Tabellenbasis werden aus dem aktiven Profil verwendet, nicht aus Chat-Erinnerungen vorbefüllt.

Die Vorschau aktualisiert sich beim Ändern der Felder. Erst «Profil speichern» übernimmt die Auswahl und die Ziele. Dimitri und Patricia können unterschiedliche Ziele verwenden. Nach der normalen Synchronisierung gilt die Auswahl auf anderen Geräten desselben Profils. Das ist unabhängig vom gerätebezogenen Standardprofil.

Bestehende Profile werden nicht stillschweigend umgestellt. «Nur Basiswerte / eigene Ziele (bisher)» bleibt bis zu einer ausdrücklichen Wahl erhalten.

## Tagesmengen oben im Überblick

Energie, Protein, Kohlenhydrate und Fett zeigen jeweils erfasste Menge, Tagesbedarf/Ziel und bei vollständigen Angaben die verbleibende Menge. Ziele bleiben bei leerem Tagebuch sichtbar. Bei fehlenden Profilangaben steht «Noch nicht festgelegt». Unbekannte Nährwerte bleiben unbekannt und werden nicht als null gerechnet.

Ein Ziel- oder Gewichtswechsel schreibt frühere Verzehrmengen und Nährwertkopien nicht um. Der spanische Glückwunschbildschirm verwendet den aktiven Proteinwert; seine Begrenzung auf einmal je Profil und Tag bleibt erhalten.

## Nachvollziehbare App-Startwerte

| Ziel | Protein pro kg Berechnungsgewicht | Energieplanung |
|---|---|---|
| Normal / Gewicht halten | 0,8 g; ab 65 Jahren 1,0 g | Geschätzte Erhaltungsenergie |
| Muskelaufbau | 1,6 g | +5 %, höchstens 200 kcal; bei BMI über 25 zunächst kein Überschuss |
| Sportler / ambitioniertes Training | 1,4 g | Erhaltungsenergie mit separat gewählter Aktivität |
| Abnehmen / moderat | 1,2 g | −10 %, höchstens 400 kcal |

Die festen Sport-/Abnehmwerte und Energieanpassungen sind ausgewählte, anpassbare App-Startannahmen, keine individuellen ärztlichen Verordnungen oder exakten DGE-Einzelvorgaben. Das Sportprofil richtet sich an mehr als fünf Trainingsstunden pro Woche; sehr hohe Belastungen brauchen individuellere Planung.

Energie: Ruheenergie nach der DGE-FAQ-Formel aus aktuellem Gewicht, Alter und männlicher/weiblicher Tabellenbasis, multipliziert mit dem ausdrücklich gewählten Aktivitätsfaktor. Grösse dient der BMI-Prüfung, nicht als zusätzlicher Summand dieser Energieformel. Training nicht doppelt addieren.

Fett: standardmässig 30 % der Zielenergie geteilt durch 9. Kohlenhydrate: verbleibende Energie nach Protein und Fett geteilt durch 4. Die vereinfachte 4/4/9-Rechnung reserviert keine Alkoholenergie; Lebensmittelangaben können wegen Ballaststoffen, Polyolen und Rundung abweichen.

Bei BMI über 25 muss das Protein-Berechnungsgewicht bestätigt werden. «Referenzgewicht einsetzen» bietet ausdrücklich die Modellannahme BMI 22 × Körpergrösse² an. Das verändert weder das tatsächliche Gewicht noch definiert es ein Abnehmziel. Ein fachlich abgestimmter anderer Wert bleibt möglich.

Berechnungsweg und Primärquellen sind im Profil unter «Wie werden meine Ziele berechnet?» verlinkt: DGE Energie-FAQ, Protein-, Fett- und Kohlenhydrat-Referenzen, DGE Protein im Sport sowie Leidy et al. zum Protein-/Gewichtsmanagement. Konkrete Standardprofile und automatische Geltungsgrenzen sind Entscheidungen dieses App-Modells.

## Eigene Ziele und besondere Situationen

Manuell gesetzte Ziele haben Vorrang, auch nach einem Zielwechsel. «Für diese vier Werte wieder Automatik verwenden» leert nach Bestätigung nur Energie, Protein, Kohlenhydrate und Fett. Andere eigene Vitamin-/Mineralstoffziele bleiben erhalten. Aktiv wird dies erst nach «Profil speichern».

Eigene Energie-, Protein- oder Fettwerte beeinflussen die verbleibenden automatischen Makros. Widersprüche werden angezeigt, nicht heimlich korrigiert; keine negativen Kohlenhydratziele. Vitamine und Mineralstoffe werden nicht proportional zum Gewicht oder Sportziel erhöht.

Die Automatik gilt für gesunde Erwachsene im erläuterten Planungsrahmen. Keine normalen automatischen Ziele für Minderjährige oder bei markierter besonderer medizinischer Situation; kein automatisches Abnehmdefizit unter BMI 20 oder ab 65 Jahren. Die Grenzen sind Vorsichtsentscheidungen der App, keine Diagnosen. Fachlich abgestimmte eigene Ziele bleiben möglich.

## Update und Datenschutz

Die feste App-Adresse bleibt https://dimitrit86-bot.github.io/mythenquai-open/kompass/ . Bei Bedarf «App aktualisieren» verwenden; Kopfzeile 1.5.0. Keine Neuinstallation oder Löschung von Browserdaten nötig.

Keine Profile, Passwörter, gemeinsamen Vorlagen oder Tagebucheinträge wurden für die Veröffentlichung zurückgesetzt. Servercode und Datenbanktabellen wurden nicht verändert. Neue Profilfelder verwenden die vorhandene geschützte Speicher- und Abgleichlogik. Nur kompass/-Dateien werden veröffentlicht; übrige Repository-Seiten bleiben unverändert.

## Tatsächlich ausgeführte Prüfungen

Erfolgreicher GitHub-Prüflauf 36267931656, geprüfter Quellcommit f00a9a96c40241706bb5cc2fe253043eb078c1bb. Alle 13 vorbereiteten Anwendungs-/Testdateien wurden mit dem heruntergeladenen CI-Artefakt byteweise abgeglichen.

172 Einzelprüfungen bestanden: 48 Kern-/Rezepttests, 46 Makroziele, 26 Portionen, 22 Produktimport/Zielerkennung, 15 Proteinübersicht und 15 Synchronisierung. Zusätzlich bestanden je 38 tatsächliche Browserabläufe in Chromium und WebKit: Auswahl, Vorschau, Speichern mit verschlüsseltem Browserspeicher, getrennte Profile, zwei Geräte, manuelle Priorität, erhaltene Mikronährstoffziele, Berechnungsgewicht, besondere Situationen, spanischer Glückwunsch, unveränderte Historie und 320-/390-/1440-Pixel-Ansichten. Keine JavaScript-Laufzeitfehler.

Die Browserprüfungen verwendeten synthetische Profile und kontrollierte Serverantworten, nicht die echten privaten Haushaltsdaten. Ein neuer Praxistest auf einem physischen Android- oder iPhone-Gerät und der Kamerahardware wird nicht behauptet. Die mobile WebKit-Ansicht wurde zusätzlich visuell geprüft.
