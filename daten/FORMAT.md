# Datenformat der Regeldatenbank

Alle Daten, die sich durch Gesetzesänderungen ändern können, liegen in diesem Ordner. App und Webseite lesen dieselben Dateien. Jede Änderung ist über die Git-Historie nachvollziehbar.

Die aktuelle Prüfübersicht steht in [PRUEFSTAND.md](PRUEFSTAND.md). Sie wird beim Build erzeugt.

## Dateien

| Datei | Inhalt | Prüfrhythmus |
|---|---|---|
| `schonzeiten-binnen.json` | Schonzeiten, Mindest- und Höchstmaße der 16 Länder (Binnengewässer) | 12 Monate |

Geplant: `kuestenregeln.json` (6 Monate), `jagdzeiten.json` (12 Monate), `reiseziele.json` (12 Monate).

## Aufbau einer Datei

```json
{
  "format": 1,
  "datensatz": "schonzeiten-binnen",
  "titel": "…",
  "stand": "2026-10-02",
  "pruefrhythmus_monate": 12,
  "haftung": "…",
  "eintraege": [ … ]
}
```

`stand` ist das Datum der letzten inhaltlichen Änderung der Datei. Die App nimmt eine geladene Datei nur, wenn ihr `stand` gleich oder neuer ist als der eingebaute.

## Aufbau eines Eintrags

| Feld | Pflicht | Bedeutung |
|---|---|---|
| `id` | ja | Kürzel, bei Ländern der amtliche Zweibuchstabencode (HE, BY …) |
| `name` | ja | Anzeigename |
| `rechtsgrundlage` | ja | Name und Datum der Verordnung |
| `rechtsstand` | ja | Fassung oder letzte Änderung, so wie sie in der Quelle steht |
| `allgemein` | nein | Hinweis, der für das ganze Land gilt |
| `quellen` | ja | Liste aus `titel`, `url`, `art` (Originaltext, Originaltext (Abdruck), Behördenübersicht, Auszug, Sekundärquelle) |
| `pruefung.am` | ja | Datum der letzten Prüfung (JJJJ-MM-TT) |
| `pruefung.von` | ja | Wer geprüft hat |
| `pruefung.status` | ja | siehe unten |
| `pruefung.methode` | ja | Was genau geprüft wurde, in einem Satz |
| `pruefung.naechste` | ja | Fälligkeitsdatum der nächsten Prüfung |
| `arten` | ja | Regeln je Art, siehe unten |

### Status

| Wert | Bedeutung |
|---|---|
| `geprueft` | Am Originaltext der aktuellen Fassung geprüft |
| `teilgeprueft` | Original gelesen, aber nicht die jüngste Änderung oder nicht alle Arten |
| `abgeglichen` | Mit mindestens zwei unabhängigen Sekundärquellen abgeglichen, Original offen |
| `abweichung` | Quellen widersprechen sich, Klärung offen |

### Regel je Art

```json
"Hecht": { "schonzeit": "01.02-15.04", "mindestmass_cm": 50, "hoechstmass_cm": 90, "hinweis": "…" }
```

- `schonzeit`: `"TT.MM-TT.MM"`, `"ganzjaehrig"` oder `null` (keine Schonzeit)
- `mindestmass_cm`, `hoechstmass_cm`: Zahl oder `null`. Beide gesetzt = Entnahmefenster
- `hinweis`: regionale Abweichungen, Geltungsbereich (optional)

Arten ohne landesweite Regel werden weggelassen.

## Ablauf bei einer Prüfung

1. Quelle öffnen, Werte vergleichen.
2. Abweichungen in `arten` korrigieren, `rechtsstand` aktualisieren.
3. `pruefung.am`, `von`, `status`, `methode`, `naechste` setzen.
4. `stand` der Datei auf das heutige Datum setzen, wenn sich Werte geändert haben.
5. `python3 tools/build.py`, dann committen. Die Commit-Nachricht nennt Land und Änderung.
