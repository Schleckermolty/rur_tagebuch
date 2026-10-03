# Rute & Revier Tagebuch

Angel- und (bald) Jagdtagebuch von [Rute & Revier](https://www.rute-und-revier.de) als installierbare Web-App.

## Grundsätze

- **Alle Daten bleiben auf dem Gerät** (IndexedDB). Kein Konto, kein Server, kein Tracking.
- **Fotos** werden beim Hinzufügen neu gespeichert, dabei fallen EXIF- und GPS-Daten weg.
- **Wetter**: Open-Meteo, nur mit auf 0,1° gerundeten Koordinaten.
- **Karte**: OpenStreetMap-Kacheln. Dabei wird die IP-Adresse an OSM übertragen.
- **Schriften und Bibliotheken** liegen im Repository, es gibt keine Anfragen an Google oder CDNs.

## Aufbau

| Pfad | Inhalt |
|---|---|
| `daten/` | Regeldatenbank: Schonzeiten und Maße mit Quelle, Rechtsstand und Prüfdatum. Format in `daten/FORMAT.md`, Übersicht in `daten/PRUEFSTAND.md` |
| `src/app.html` | Quelle der App (identisch mit der Vorschau-Fassung) |
| `tools/build.py` | erzeugt `index.html` und `sw.js` aus der Quelle |
| `tools/sw.template.js` | Service Worker für den Offline-Betrieb |
| `index.html`, `sw.js` | erzeugte Dateien, werden über GitHub Pages ausgeliefert |
| `fonts/`, `vendor/`, `icons/` | lokale Schriften (OFL), Leaflet (BSD-2), App-Symbole |

## Ändern und veröffentlichen

```bash
# src/app.html bearbeiten, Version in tools/build.py erhöhen, dann:
python3 tools/build.py
git add -A && git commit -m "…" && git push
```

GitHub Pages veröffentlicht den Stand von `main` automatisch.

Regeldaten ändern: nur die Datei in `daten/` bearbeiten (Ablauf in `daten/FORMAT.md`). Die App lädt sie beim Start und nimmt die neue Fassung ohne App-Update. Der Build bettet zusätzlich eine Kopie als Rückfall ein.

## Daten und Quellen

- Schonzeiten und Mindestmaße: Fischereiverordnungen der 16 Länder, Stand 02.10.2026. Ohne Gewähr, die Gewässerordnung kann strenger sein.
- Ländergrenzen: [deutschlandGeoJSON](https://github.com/isellsoap/deutschlandGeoJSON), vereinfacht.
- Wetterdaten: [Open-Meteo.com](https://open-meteo.com) (CC BY 4.0).
- Karte: © OpenStreetMap-Mitwirkende.
