# Grocy-Rewe-Connect

Dieses Projekt ermöglicht es, Einkaufsbelege von der REWE-Website abzurufen und die Daten in die Grocy-Anwendung zu importieren.

## Funktionalitäten

- Abrufen von Einkaufsbelegen von der REWE-Website mithilfe eines RTSP-Tokens.
- Importieren von Einkaufsdaten in die Grocy-Anwendung.
- Unterstützung für benutzerdefinierte EAN-Mappings.

## Voraussetzungen

- Python 3.x
- Benutzerkonto auf der REWE-Website
- Grocy-Anwendung mit API-Zugriff

## Verwendung
1. Öffne das Terminal und navigiere zum Projektverzeichnis.
2. Führe python main.py aus.
3. Folge den Anweisungen, um das RTSP-Token einzugeben und den Einkaufsbeleg zu importieren.

### REWE RTSP Token

Um den RTSP Token zu bekommen musst du folgende Schritte befolgen:
1. Besuche die Rewe Website unter https://shop.rewe.de
2. Logge dich ein
3. Öffne die Browser Console und navigiere zu "Web-Speicher" > Cookies > RTSP Token
4. Kopiere den RTSP Token und füge ihn nach der Aufforderung ins Terminal ein.
5. Du solltest nun eine Auswahl deiner letzten 5 Einkäufe sehen.

## Lizenz

Dieses Projekt ist unter der [GNU General Public License v3](LICENSE) lizenziert.
