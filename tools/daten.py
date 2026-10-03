#!/usr/bin/env python3
"""Hilfsfunktionen für die Regeldatenbank.

- embed(html): bettet die Datensätze aus daten/ als Rückfall-Kopie in die App ein
  (zwischen den Markierungen /*DATA:<name>*/ … /*END:<name>*/).
- pruefstand(): schreibt daten/PRUEFSTAND.md mit Status und Fälligkeiten.
"""
import json, pathlib, re, datetime, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATEN = ROOT / "daten"
DATASETS = ["schonzeiten-binnen"]
STATUS = {"geprueft": "geprüft (Original)", "teilgeprueft": "teilweise geprüft", "abgeglichen": "abgeglichen (Sekundär)", "abweichung": "Abweichung offen"}

def load(name):
    ds = json.loads((DATEN / f"{name}.json").read_text(encoding="utf-8"))
    if ds.get("format") != 1:
        sys.exit(f"Daten-Fehler: {name}.json hat unbekanntes Format")
    for e in ds["eintraege"]:
        for key in ("id", "name", "rechtsgrundlage", "rechtsstand", "quellen", "pruefung", "arten"):
            if key not in e:
                sys.exit(f"Daten-Fehler: {name}.json, Eintrag {e.get('id')}: Feld '{key}' fehlt")
        if e["pruefung"].get("status") not in STATUS:
            sys.exit(f"Daten-Fehler: {name}.json, Eintrag {e['id']}: unbekannter Status")
    return ds

def embed(html):
    for name in DATASETS:
        data = json.dumps(load(name), ensure_ascii=False, separators=(",", ":"))
        pat = re.compile(r"/\*DATA:%s\*/.*?/\*END:%s\*/" % (re.escape(name), re.escape(name)), re.S)
        if not pat.search(html):
            sys.exit(f"Build-Fehler: Markierung für {name} fehlt in der App")
        html = pat.sub(lambda m: f"/*DATA:{name}*/{data}/*END:{name}*/", html)
    return html

def pruefstand():
    today = datetime.date.today().isoformat()
    out = ["# Prüfstand der Regeldaten", "", f"Erzeugt am {today} aus den Dateien in diesem Ordner. Nicht von Hand bearbeiten.", ""]
    for name in DATASETS:
        ds = load(name)
        es = ds["eintraege"]
        due = [e for e in es if e["pruefung"]["naechste"] <= today]
        out += [f"## {ds['titel']}", "", f"Datei `{name}.json`, Stand {ds['stand']}, Prüfrhythmus {ds['pruefrhythmus_monate']} Monate. "
                f"{len(es)} Einträge, davon {sum(e['pruefung']['status']=='geprueft' for e in es)} am Original geprüft, {len(due)} fällig.", "",
                "| Eintrag | Status | Rechtsstand | Geprüft am | Nächste Prüfung | Hauptquelle |", "|---|---|---|---|---|---|"]
        for e in sorted(es, key=lambda e: (e["pruefung"]["naechste"], e["name"])):
            p = e["pruefung"]; q = e["quellen"][0]
            flag = " **fällig**" if p["naechste"] <= today else ""
            out.append(f"| {e['name']} | {STATUS[p['status']]} | {e['rechtsstand']} | {p['am']} | {p['naechste']}{flag} | [{q['art']}]({q['url']}) |")
        out.append("")
    (DATEN / "PRUEFSTAND.md").write_text("\n".join(out), encoding="utf-8")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        p = pathlib.Path(sys.argv[1]); p.write_text(embed(p.read_text(encoding="utf-8")), encoding="utf-8"); print(f"Daten in {p} eingebettet")
    pruefstand(); print("daten/PRUEFSTAND.md erzeugt")
