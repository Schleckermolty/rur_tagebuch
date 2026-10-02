#!/usr/bin/env python3
"""Erzeugt index.html aus src/app.html (der Vorschau-Fassung).

- Schriften und Leaflet werden lokal statt per CDN geladen (DSGVO, offline).
- Vorschau-spezifische Hinweise werden durch Texte für die installierte App ersetzt.
- Manifest, App-Symbole und Service Worker (Offline-Betrieb) werden eingebunden.

Aufruf: python3 tools/build.py
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
VERSION = "0.7.1"

src = (ROOT / "src" / "app.html").read_text(encoding="utf-8")

def sub(old, new, count=1):
    global src
    n = src.count(old)
    if n != count:
        sys.exit(f"Build-Fehler: '{old[:60]}' {n}x gefunden, erwartet {count}x")
    src = src.replace(old, new)

# Externe Ressourcen durch lokale ersetzen
src = re.sub(r'<link rel="preconnect"[^>]*>\n?', '', src)
src, n = re.subn(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^"]*">', '<link rel="stylesheet" href="fonts/fonts.css">', src)
assert n == 1, "Google-Fonts-Link nicht gefunden"
sub('<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>', '<script src="vendor/leaflet.js"></script>')

# Texte für die installierte App
sub('Etappe 1 · Vorschau', f'Version {VERSION}')
sub('Kartenbild nicht geladen. In der Vorschau sind externe Karten gesperrt, in der installierten App erscheint hier die Karte. Spots und Tippen auf die Karte funktionieren.',
    'Kartenbild nicht geladen, vermutlich keine Verbindung. Spots, Fänge und Tippen auf die Karte funktionieren trotzdem.')
sub('Standort nicht verfügbar. In der Vorschau ist GPS gesperrt, in der installierten App fragt das Handy nach. Spot wählen oder Koordinaten einfügen.',
    'Standort nicht verfügbar. Bitte Standortfreigabe für die App erlauben, oder Spot wählen bzw. Koordinaten einfügen.')
sub('Wetterdienst nicht erreichbar. In der Vorschau ist das gesperrt, in der installierten App klappt es. Werte bitte von Hand eintragen.',
    'Wetterdienst nicht erreichbar, vermutlich keine Verbindung. Werte bitte von Hand eintragen oder später erneut abrufen.')

head = f'''<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="Angel- und Jagdtagebuch von Rute &amp; Revier. Alle Daten bleiben auf deinem Gerät.">
<meta name="theme-color" content="#223225">
<meta name="color-scheme" content="light dark">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/icon-192.png" type="image/png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="R&amp;R Tagebuch">
<style>
:root{{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}
body{{margin:0;font-size:14px}}
img{{max-width:100%}}
[hidden]{{display:none!important}}
</style>
'''
body_start = src.index('<header class="top">')
head_part, body_part = src[:body_start], src[body_start:]
sw = f'''
<script>
if('serviceWorker' in navigator){{window.addEventListener('load',()=>{{navigator.serviceWorker.register('sw.js').catch(()=>{{}})}})}}
</script>
'''
out = head + head_part + '</head>\n<body>\n' + body_part + sw + '</body>\n</html>\n'
(ROOT / "index.html").write_text(out, encoding="utf-8")

# Service Worker mit Versionsstand neu schreiben
sw_src = (ROOT / "tools" / "sw.template.js").read_text(encoding="utf-8").replace("__VERSION__", VERSION)
(ROOT / "sw.js").write_text(sw_src, encoding="utf-8")
print(f"index.html und sw.js erzeugt (Version {VERSION}, {len(out)//1024} KB)")
