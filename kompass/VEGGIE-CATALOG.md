# Veggie-Datenupdate · 26.09.2026

## Umfang

Die unveränderte BLV-Basis mit 1'246 Lebensmitteln wurde um 51 separat gekennzeichnete Markenprodukte ergänzt. Insgesamt sind 1'297 Lebensmittel verfügbar. 45 Ergänzungen sind vegan, 6 vegetarisch mit Ei bzw. Milch.

| Gruppe | Neue Produkte |
| --- | ---: |
| Fleischalternativen | 21 |
| Pflanzendrinks | 14 |
| Tofu | 6 |
| Joghurtalternativen | 4 |
| Käsealternativen | 4 |
| Kochcremes | 2 |

Marken: Planted 13, Alpro 17, Quorn 7, Taifun 6, Violife 4, Oatly 3, Beyond Meat 1.

## Benutzung

Alle Ergänzungen erscheinen in der bestehenden Lebensmittel- und Zutatensuche. Suche nach Marke, Produktname, vegan, vegetarisch oder Ersatzbegriffen wie Hafermilch, Feta und Hackfleisch. Die Ernährungsweise ist in der Kategorie sichtbar. Dies ist kein Allergiefilter. Die separate interaktive Filteroberfläche wurde nicht veröffentlicht; das Update nutzt die bewährte Suche.

Die allgemeinen BLV-Kopfzeilen der bestehenden Quellenansichten beziehen sich nur auf den ursprünglichen Basisbestand. Neue Markenprodukte sind keine BLV-Datensätze: Ihre tatsächlichen Hersteller-/Produktquellen stehen im Quellenfeld und in der Herleitung der Einzelwerte. Der aufklappbare Datenhinweis am Seitenanfang erläutert diese Unterscheidung.

## Quellen und Qualität

Jeder Datensatz in veggie-data.js enthält eine konkrete HTTPS-Produktquelle, Bezugsmenge pro 100 g oder 100 ml, Länderfassung und Quellenstand. Quellen sind Herstellerseiten von Planted, Alpro, Quorn, Taifun, Oatly, Violife und Beyond Meat sowie für Violife Greek White die Schweizer Produktdeklaration von Coop. Die Quelle CH/DE/DACH ist keine Verfügbarkeitsgarantie. Die Werte sind eine Momentaufnahme, kein automatischer Live-Abgleich.

Nur tatsächlich bezifferte Nährwerte wurden übernommen. Fehlende Mikronährstoffe bleiben null im Datensatz und werden von der App als unbekannt behandelt, nicht als Nullaufnahme. Deklarierte echte Nullwerte bleiben echte Nullen. Weniger-als-Angaben werden als unbekannter exakter Wert mit Originalgrenze dokumentiert. Es gibt keine erfundenen Vitamine oder stillschweigende Umrechnung zwischen g und ml.

Widersprüchliche Vitamin-E-Angaben bei Alpro Mandeldrink, Calciumangaben bei Alpro Cuisine und eine unplausible Eisen-Einheit bei Planted Skewers Herbs wurden nicht numerisch übernommen. Bei mehreren Quorn-Produkten weicht die Kurzvorschau von der detaillierten Herstellertabelle ab: Die detaillierte Tabelle ist übernommen und der Widerspruch im Quellennachweis dokumentiert. Die tatsächliche Packung sollte vor Verwendung verglichen werden. Ländervarianten werden nicht vermischt.

Zwei Alpro-Protein-Joghurtseiten wurden wegen unklarer Gewichts-/Volumenbasis ausgeschlossen. Zutatenlisten allein liefern keine exakten Vitamin- oder Mineralstoffmengen.

## Datenbestand und Privatsphäre

catalog.js ergänzt ausschliesslich den öffentlichen In-Memory-Lebensmittelkatalog vor dem App-Start. Die bestehenden BLV-Lebensmittelobjekte werden nicht verändert. Es erfolgen keine Profil-, Tagebuch-, Rezept-, Passwort- oder Backend-Mutationen. Die vorhandenen Rezept- und Tagebuch-Snapshots bleiben erhalten. Keine zusätzlichen externen Abfragen und keine neuen Drittanbieter-Skripte. Alle Änderungen dieser Veröffentlichung sind auf kompass/ beschränkt.

## Prüfungen

48 bestehende Kern-Rechentests bestanden. Zusätzlich 16 Prüfungen der tatsächlich veröffentlichten Katalogintegration bestanden: eindeutige IDs und unveränderter Basisbestand, keine Speicheränderung beim Laden, gültige Nährstoffwerte, null/Null-Unterscheidung, wiederholtes Laden, vegane und Marken-Suche, Favoriten, Hersteller-Quellennachweis, ursprüngliche BLV-Suche, Rezeptmengen, Snapshot-Erhaltung, Rekonstruktion gespeicherter Daten und mobile/Desktop-Layouts ohne horizontales Überlaufen oder JavaScript-Fehler.

Rezepttest: 100 g planted.hack plus 0.5 dl Alpro Sojadrink Ohne Zucker ergeben auf Basis der hinterlegten Deklarationen 19.65 g Protein und 192.5 kcal. Calcium ist nur teilweise bekannt und bleibt entsprechend gekennzeichnet.

Umgebung: Chromium mit lokal gerendertem DOM, synthetischen Testdaten und Test-Speicheradapter. Die Integration wurde gegen die vorhandene v0.1-UI getestet; relevante Live-Handler wurden über GitHub gegengeprüft. Ein neuer Test auf echten Android-/iPhone-Geräten, des Kamera-Zugriffs oder des authentifizierten Serverabgleichs ist damit nicht behauptet.

SHA-256 von veggie-data.js: 00d333492232ab9adbb168cf531fa3e785c72cbafae3db9664317458b4e71da9
